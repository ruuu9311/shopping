# 使用 Python 3.9 作為基底
FROM python:3.9

# 1. 安裝 Chrome 瀏覽器必備的依賴套件
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 2. 下載並安裝 Google Chrome (穩定版)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. 設定工作目錄
WORKDIR /app

# 4. 複製程式碼到容器內
COPY . .

# 5. 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 6. 啟動 Gunicorn 伺服器
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]