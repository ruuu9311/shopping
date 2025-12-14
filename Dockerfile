# 使用 Python 3.9 作為基底
FROM python:3.9

# 1. 安裝基本工具
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 2. 直接下載並安裝 Google Chrome (最穩定解法)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

# 3. 設定工作目錄
WORKDIR /app

# 4. 複製程式碼到容器內
COPY . .

# 5. 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 6. 啟動 Gunicorn 伺服器
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]