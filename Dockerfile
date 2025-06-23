# Dockerfile
# 使用官方 Python 影像為基底（建議用輕量版本）
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝依賴
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 複製所有專案檔案
COPY . .

# 開放容器內的 8000 端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

