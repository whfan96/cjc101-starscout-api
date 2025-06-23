# 使用官方 Python 影像為基底（建議用輕量版本）
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔案到容器內
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案程式碼到容器內
COPY . .

# 指定要執行的指令，這裡用 uvicorn 啟動 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

