# 🚀 Quick Start Guide / クイックスタートガイド

## English

### 1. Prerequisites

- Python 3.10+
- Git
- (Optional) Node.js 18+ for Minecraft

### 2. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/Geode-Engine.git
cd Geode-Engine

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### 4. Run

```bash
python src/brain_stem/main.py
```

### 5. (Optional) Minecraft Integration

```bash
cd src/games/minecraft
npm install
node bot.js
```

---

## 日本語

### 1. 前提条件

- Python 3.10以上
- Git
- （オプション）Minecraft用にNode.js 18以上

### 2. クローンとセットアップ

```bash
git clone https://github.com/YOUR_USERNAME/Geode-Engine.git
cd Geode-Engine

python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 3. 設定

```bash
cp .env.example .env
```

`.env` を編集:
```
GEMINI_API_KEY=あなたのAPIキー
```

### 4. 実行

```bash
python src/brain_stem/main.py
```

### 5. （オプション）Minecraft統合

```bash
cd src/games/minecraft
npm install
node bot.js
```

---

## Troubleshooting / トラブルシューティング

| Issue | Solution |
|:---|:---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `GEMINI_API_KEY not set` | Check your `.env` file |
| Minecraft connection failed | Ensure Node.js is installed and Minecraft is running |

---

**Need help?** Open an issue on GitHub!
