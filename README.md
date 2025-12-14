# 商品價格比較平台 - 加速開發版本
## ⚡ 明天交付版本（24小時內完成）

### 📋 專案結構
```
price-compare-app/
├── app.py                  # Flask 主應用
├── scrapers/
│   ├── __init__.py
│   ├── momo.py            # MOMO 爬蟲
│   ├── pchome.py          # PChome 爬蟲
│   └── books.py           # 博客來爬蟲
├── requirements.txt        # Python 依賴
├── vercel.json            # Vercel 部署配置
├── index.html             # 前端頁面
└── .gitignore
```

### 🚀 快速開始（5分鐘）

#### Step 1: 本地測試
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  
# Windows: .\venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 運行應用
python app.py

# 訪問 http://localhost:5000
```

#### Step 2: 部署到 Vercel
```bash
# 安裝 Vercel CLI
npm install -g vercel

# 部署
vercel

# 選擇: 
# - Which scope? (你的 Vercel 帳戶)
# - Link to existing project? (No)
# - Project name? (price-compare)
```

### 📱 核心功能（已全部實現）
- ✅ 蝦皮爬蟲
- ✅ MOMO 爬蟲  
- ✅ PChome 爬蟲
- ✅ 博客來爬蟲
- ✅ 價格比較和排序
- ✅ 最便宜標記
- ✅ 響應式前端
- ✅ Vercel 部署準備完成

### ⏱️ 開發時間預計
- 複製代碼: 2分鐘
- 本地測試: 10分鐘
- 部署: 5分鐘
- **總共: 17分鐘**

### 📝 注意事項
1. 爬蟲可能遭到反爬（IP 被擋），如果發生請聯絡教授說明
2. 如需修改目標商品，直接改 `index.html` 的搜尋框
3. 首次部署到 Vercel 可能需要調整 `vercel.json`
