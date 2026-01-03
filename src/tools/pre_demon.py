#!/usr/bin/env python
# pre_demon.py
# 🔥 Pre-Demon: 自動バグ検出スクリプト
# コード変更後に実行して、既知の危険パターンを検出する

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

# ================================================================
# 🎯 危険パターン定義
# これまでの Demon Audit で発見されたバグパターンを収録
# ================================================================

PATTERNS: List[Tuple[str, str, str]] = [
    # (正規表現, 深刻度, 説明)
    
    # === Critical: 即死バグ ===
    (r'self\.chemicals\[', '🔴 CRITICAL', 'chemicals直接アクセス → hormones.get() を使う'),
    (r'self\.chemicals\s*=', '🔴 CRITICAL', 'chemicals直接代入 → hormones.set() を使う'),
    (r'self\.chemicals\.get\(', '🔴 CRITICAL', 'chemicals.get() → hormones.get() を使う'),
    
    # === Major: 深刻なバグ ===
    (r'except:\s*pass', '🟠 MAJOR', '例外の黙殺 → 最低限ログを出す'),
    (r'except\s+Exception:\s*pass', '🟠 MAJOR', '全例外の黙殺 → 具体的な例外を指定'),
    (r'for\s+\w+\s+in\s+self\.\w+:', '🟠 MAJOR', '共有データのイテレート → lockを確認'),
    (r'min\s*\(\s*1\.0', '🟠 MAJOR', 'min(1.0) → min(config.HORMONE_MAX) スケール確認'),
    (r'max\s*\(\s*0\.0.*,\s*min\s*\(\s*1\.0', '🟠 MAJOR', 'クランプ範囲が0-1 → 0-100 スケール確認'),
    
    # === Minor: 潜在的問題 ===
    (r'\b\d{2,}\.0\b', '🟡 MINOR', 'マジックナンバー → config定数を検討'),
    (r'time\.sleep\s*\(\s*\d+\s*\)', '🟡 MINOR', 'ハードコードsleep → config定数を検討'),
    (r'# TODO', '🟡 MINOR', 'TODO残存 → 対応が必要かもしれない'),
    (r'print\s*\(\s*f?["\'].*["\']', '⚪ INFO', 'print文 → ログレベルを検討 (デバッグ用?)'),
    
    # === スレッド安全性 ===
    (r'self\.\w+\s*\+=', '🟠 MAJOR', '+=演算子 → アトミックでない。lockを確認'),
    (r'self\.\w+\s*-=', '🟠 MAJOR', '-=演算子 → アトミックでない。lockを確認'),
    
    # === データ構造 ===
    (r'\w+,\s*\w+\s*=\s*self\.\w+\[', '🟡 MINOR', 'リストアンパック → 要素数変更に脆弱'),
    
    # === 文字列操作 ===
    (r'set\s*\(\s*\w+\s*\)(?!\s*\.split)', '🟡 MINOR', 'set(string) → 文字単位になる。split()を検討'),
]

# ================================================================
# 🛡️ 除外パターン (誤検出を防ぐ)
# ================================================================

EXCLUDE_PATTERNS = [
    r'# pre_demon:ignore',  # 明示的な除外コメント
    r'hormones\.get\(',      # 正しい書き方
    r'hormones\.update\(',   # 正しい書き方
    r'hormones\.set\(',      # 正しい書き方
    r'with\s+self\.\w*lock',  # lockを使っている
]

# ================================================================
# 📂 スキャン対象
# ================================================================

SCAN_DIRS = ['src']
EXCLUSIONS = ['__pycache__', '.git', 'venv', 'MeloTTS', 'models', 'memory']
FILE_EXTENSIONS = ['.py']


def should_exclude_line(line: str) -> bool:
    """除外パターンにマッチする行を判定"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def scan_file(filepath: Path) -> List[Dict]:
    """単一ファイルをスキャン"""
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️ Cannot read {filepath}: {e}")
        return findings
    
    for line_num, line in enumerate(lines, 1):
        # 除外チェック
        if should_exclude_line(line):
            continue
        
        # 各パターンをチェック
        for pattern, severity, description in PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    'file': str(filepath),
                    'line': line_num,
                    'severity': severity,
                    'description': description,
                    'content': line.strip()[:60]
                })
    
    return findings


def scan_directory(base_dir: Path) -> List[Dict]:
    """ディレクトリを再帰的にスキャン"""
    all_findings = []
    
    for root, dirs, files in os.walk(base_dir):
        # 除外ディレクトリをスキップ
        dirs[:] = [d for d in dirs if d not in EXCLUSIONS]
        
        for file in files:
            if any(file.endswith(ext) for ext in FILE_EXTENSIONS):
                filepath = Path(root) / file
                findings = scan_file(filepath)
                all_findings.extend(findings)
    
    return all_findings


def print_report(findings: List[Dict]) -> None:
    """結果レポートを出力"""
    print("=" * 60)
    print("🔥 PRE-DEMON SCAN REPORT")
    print("=" * 60)
    print()
    
    if not findings:
        print("✅ 危険パターンは検出されませんでした！")
        return
    
    # 深刻度でグループ化
    by_severity = defaultdict(list)
    for f in findings:
        by_severity[f['severity']].append(f)
    
    # 深刻度順に出力
    severity_order = ['🔴 CRITICAL', '🟠 MAJOR', '🟡 MINOR', '⚪ INFO']
    
    for severity in severity_order:
        if severity in by_severity:
            print(f"\n{severity} ({len(by_severity[severity])}件)")
            print("-" * 40)
            
            for f in by_severity[severity]:
                rel_path = f['file'].replace('\\', '/')
                print(f"  {rel_path}:{f['line']}")
                print(f"    → {f['description']}")
                print(f"    │ {f['content']}")
                print()
    
    print("=" * 60)
    print(f"📊 Summary: {len(findings)} issues found")
    print("=" * 60)
    
    # 深刻度別カウント
    for severity in severity_order:
        count = len(by_severity.get(severity, []))
        if count > 0:
            print(f"  {severity}: {count}")


def main():
    """メインエントリポイント"""
    print("🔥 Pre-Demon Scanner v1.0")
    print("心を鬼にしてコードをスキャン中...")
    print()
    
    project_root = Path(__file__).parent.parent
    all_findings = []
    
    for scan_dir in SCAN_DIRS:
        target = project_root / scan_dir
        if target.exists():
            print(f"📂 Scanning: {scan_dir}/")
            findings = scan_directory(target)
            all_findings.extend(findings)
    
    print()
    print_report(all_findings)
    
    # CRITICALがあれば失敗
    critical_count = len([f for f in all_findings if '🔴' in f['severity']])
    if critical_count > 0:
        print(f"\n❌ {critical_count} CRITICAL issues found. Fix before commit!")
        sys.exit(1)
    else:
        print("\n✅ No critical issues. (Minor issues may still exist)")
        sys.exit(0)


if __name__ == "__main__":
    main()
