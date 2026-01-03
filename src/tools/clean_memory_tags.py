
import os
import json
import shutil
import time

# Defined in brain.py, copied here for standalone execution
YOLO_TO_JP = {
    "person": "人", "bicycle": "自転車", "car": "車", "motorcycle": "バイク",
    "airplane": "飛行機", "bus": "バス", "train": "電車", "truck": "トラック",
    "boat": "ボート", "traffic light": "信号機", "bird": "鳥", "cat": "猫",
    "dog": "犬", "horse": "馬", "sheep": "羊", "cow": "牛",
    "backpack": "リュック", "umbrella": "傘", "handbag": "バッグ", "tie": "ネクタイ",
    "suitcase": "スーツケース", "frisbee": "フリスビー", "skis": "スキー板",
    "snowboard": "スノーボード", "sports ball": "ボール", "kite": "凧",
    "baseball bat": "バット", "baseball glove": "グローブ", "skateboard": "スケボー",
    "surfboard": "サーフボード", "tennis racket": "ラケット", "bottle": "ボトル",
    "wine glass": "ワイングラス", "cup": "コップ", "fork": "フォーク",
    "knife": "ナイフ", "spoon": "スプーン", "bowl": "ボウル", "banana": "バナナ",
    "apple": "リンゴ", "sandwich": "サンドイッチ", "orange": "オレンジ",
    "broccoli": "ブロッコリー", "carrot": "ニンジン", "hot dog": "ホットドッグ",
    "pizza": "ピザ", "donut": "ドーナツ", "cake": "ケーキ", "chair": "椅子",
    "couch": "ソファ", "potted plant": "観葉植物", "bed": "ベッド",
    "dining table": "テーブル", "toilet": "トイレ", "tv": "テレビ",
    "laptop": "ノートPC", "mouse": "マウス", "remote": "リモコン",
    "keyboard": "キーボード", "cell phone": "スマホ", "microwave": "電子レンジ",
    "oven": "オーブン", "toaster": "トースター", "sink": "シンク",
    "refrigerator": "冷蔵庫", "book": "本", "clock": "時計", "vase": "花瓶",
    "scissors": "ハサミ", "teddy bear": "テディベア", "hair drier": "ドライヤー",
    "toothbrush": "歯ブラシ"
}

def clean_memory():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_path = os.path.join(base_dir, "memory_data", "brain_concepts.json")
    
    if not os.path.exists(target_path):
        print(f"❌ Target not found: {target_path}")
        return

    print(f"🧹 Scanning memory: {target_path}")
    
    # 1. Backup
    backup_path = target_path + ".bak"
    shutil.copy2(target_path, backup_path)
    print(f"📦 Backup created: {backup_path}")
    
    # 2. Load
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            concepts = data.get("concepts", {})
    except Exception as e:
        print(f"❌ Load error: {e}")
        return

    # 3. Clean
    removed = []
    english_tags = set(YOLO_TO_JP.keys())
    
    # Iterate safely
    current_keys = list(concepts.keys())
    for key in current_keys:
        if key in english_tags:
            del concepts[key]
            removed.append(key)
            
    # 4. Save
    if removed:
        print(f"🗑️ Removing {len(removed)} English tags: {', '.join(removed)}")
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print("✅ Cleaned memory saved.")
    else:
        print("✨ No English tags found. Memory is clean.")

if __name__ == "__main__":
    clean_memory()
