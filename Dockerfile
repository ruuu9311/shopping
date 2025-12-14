# 使用 Python 3.9 作為基底
FROM python:3.9-slim

# 1. 安裝系統必要的工具 (wget, gnupg, unzip)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 2. 安裝 Google Chrome (使用最穩定的直接下載法)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb
RUN rm google-chrome-stable_current_amd64.deb

# 3. 設定工作目錄
WORKDIR /app

# 4. 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製所有程式碼到容器內
COPY . .

# 6. 設定環境變數 (讓 Gunicorn 知道怎麼跑)
ENV PORT=10000

# 7. 啟動指令 (設定 timeout 為 600秒)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "600"]