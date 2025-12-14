# 比價購GO！ - 全網比價神器

- 這是一個基於 Python Flask 與 React 的即時比價搜尋引擎。透過 混合式爬蟲技術 (API 逆向工程 + Selenium 自動化)，同時抓取台灣三大電商平台的即時價格。

```
shopping/
├── static/
│   └── css/
│       └── shop.css        # 自訂樣式與游標特效
├── templates/
│   └── shop.html           # 前端頁面 (React + Tailwind)
├── app.py                  # 後端核心 (Flask + 爬蟲邏輯)
├── requirements.txt        # Python 套件清單
└── render.yaml             # Render 部署配置檔
```

### 🚀 開始

#### Step 1: 本地測試 (Localhost)
```bash
# 1. 進入專案資料夾
cd shopping

# 2. 啟動虛擬環境 (Windows)
.\venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 運行應用
python app.py

# 5. 開啟瀏覽器訪問
# http://127.0.0.1:5000
```

### Step 2: 部署到 Render (正式上線)
- 本專案因使用 Selenium，需部署於支援 Chrome 的環境 (Render)。

```bash
# 1.推送到 GitHub：
git add .
git commit -m "Final version"
git push origin main

# 2.Render 設定：
- 建立 Web Service，連結 GitHub 專案。
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn app:app
- ⚠️ 關鍵設定：在 Environment / Settings 加入 Buildpacks：
        1. https://github.com/render-examples/chrome-headless-buildpack.git (Chrome)
        2. python (Python)
```
### 📱 核心功能（已全部實現）
- 爬蟲技術：
- ✅ PChome：API 逆向工程 (自動翻頁，抓滿30筆)
- ✅ MOMO：Selenium 無頭瀏覽器 (自動切換電腦/手機版型)
- ✅ 博客來：Selenium + Regex (圖片防盜連破解、價格清洗)

- 前端特色：
- ✅ React + Tailwind CSS：極速響應式介面
- ✅ RWD 優化：手機版搜尋框、Grid 排版自動適配
- ✅ 智慧排序：支援價格高低、評分、銷量排序
- ✅ 視覺優化：創意游標、載入動畫、Sticky Footer

### ⚙️ 技術細節
- 後端：Python Flask, Gunicorn
- 爬蟲：Selenium, BeautifulSoup4, Requests
- 前端：React 18 (CDN), Tailwind CSS (CDN)
- 部署：Render (Free Tier)

### 📝 注意事項
1. Render 休眠機制：免費版主機在 15 分鐘無人訪問後會休眠，下次開啟時約需等待 30~50 秒 喚醒。
2. 爬取限制：目前設定每個平台最多抓取 30 筆 資料，以確保回應速度。
3. 瀏覽器模擬：後端已設定 referrerPolicy="no-referrer" 與 User-Agent 偽裝，以繞過基礎防爬機制。
