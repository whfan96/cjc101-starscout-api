# 🌟 CJC101-StarScout: AWS 監控與成本小幫手

本專案提供一套基於 FastAPI 的 RESTful API，整合多種 AWS 資源監控功能，包含 EC2、Billing、App Runner、Bedrock Guardrail 四大情境分析模組。支援查詢資源狀況、預算成本分析、服務異常監控等。

---

## 📁 專案結構

```
/root/cjc101-starscout/
│
├── .env                      # 環境變數（AWS 金鑰、Region 等）
├── main.py                   # FastAPI 入口，整合各情境 API
├── aws_clients.py            # Boto3 客戶端共用初始化
├── ec2_monitor.py            # 情境一：EC2 主機監控
├── billing_helper.py         # 情境二：預算 / 成本小幫手
├── apprunner_monitor.py      # 情境三：App Runner 服務監控
├── bedrock_guardrail.py      # 情境四：Bedrock Guardrail 事件查詢
├── requirements.txt          # Python 相依套件清單
├── Dockerfile                # Docker 映像建置設定檔
├── .dockerignore             # Docker 忽略檔案設定
└── docker-compose.yml        # Docker Compose 服務定義檔
```

---

## 📦 Features

- 🧾 **AWS Billing** 
- 📊 **AWS EC2** 
- 🚀 **AWS App Runner** 
- 🛡️ **Bedrock Guardrail**

---

## 🚀 Getting Started

### 前置需求

- Python 3.11+
- AWS 帳號與對應權限（Cost Explorer、EC2、App Runner）
- Docker（可選）

### 安裝步驟

1. 下載專案

   ```bash
   git clone https://github.com/whfan96/cjc101-starscout-api.git
   cd cjc101-starscout
   ```

2. 建立並啟動虛擬環境

   ```bash
   python -m venv fastapi-env
   source fastapi-env/bin/activate
   ```

3. 安裝依賴套件

   ```bash
   pip install -r requirements.txt
   ```

4. 複製並編輯環境變數檔案

   ```bash
   cp .env.sample .env
   # 編輯 .env，填入你的 AWS 金鑰與區域設定
   ```

5. 啟動 FastAPI 服務

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

---

## 🔐 環境變數格式

`.env` 範例格式：

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
```

> ⚠️ **請勿將 `.env` 檔提交至版本控制，以避免機密外洩。**

---

## 🧪 API 端點 (規劃中)

| 方法 | 路徑                | 功能說明                       |
|------|---------------------|-------------------------------|
| GET  | /billing/summary     | 取得 AWS 成本摘要              |
| GET  | /ec2/monitor        | 監控 EC2 CPU 使用率            |
| GET  | /apprunner/health   | 檢查 App Runner 服務健康狀況    |
| GET  | /guardrail/logs     | 查詢 Bedrock Guardrail 事件記錄 |
   ⋮

---

## 📡 功能詳解

### 🖥️ EC2 監控（情境一）

- 列出所有 EC2 執行個體
- 查詢指定 EC2 的 CPU 利用率（預設過去 1 小時平均）
- EC2 狀態檢查結果查詢
- EC2 過去啟停與重啟事件紀錄

### 💰 成本預算助手（情境二）

- 查詢當月 AWS 服務成本
- 查詢歷史 N 個月成本趨勢
- 每日成本明細查詢（預設近 7 天）
- 標籤成本分佈分析
- 簡單線性成本預測
- 成本節省建議（示意）

### ⚙️ App Runner 監控（情境三）

- 查詢所有 App Runner 服務列表
- 服務狀態監控（Running / Failed / Stopped）
- 部署版本與最後部署時間查詢
- 錯誤率與延遲資料（從 CloudWatch 擷取）

### 🛡️ Bedrock Guardrail（情境四）

- 監控 Guardrail 介入事件
- 查詢事件時間、資源與介入原因
- 匯出事件紀錄（CSV 格式）

---

## 🧪 API 測試

啟動服務後，自動提供 Swagger UI：

> http://localhost:8000/docs

---

## 📝 授權條款

MIT License

---

> Developed with ❤️ by [whfan96]

