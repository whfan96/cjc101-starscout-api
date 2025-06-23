# 🌟 CJC101-StarScout: AWS 監控與成本小幫手

本專案提供一套基於 FastAPI 的 RESTful API，整合多種 AWS 資源監控功能，包含 EC2、Billing、App Runner、Bedrock Guardrail 四大情境分析模組。支援查詢資源狀況、預算成本分析、服務異常監控等。


---

## 📁 專案結構

```
/root/cjc101-starscout/
│
├── main.py                  # FastAPI 入口，整合各情境 API
├── .env                     # 環境變數（AWS 金鑰、Region 等）
├── aws_clients.py           # Boto3 客戶端共用初始化
├── ec2_monitor.py           # 情境一：EC2 主機監控
├── billing_helper.py        # 情境二：預算 / 成本小幫手
├── apprunner_monitor.py     # 情境三：App Runner 服務監控
├── bedrock_guardrail.py     # 情境四：Bedrock Guardrail 事件查詢
└── requirements.txt         # Python 相依套件清單
```

---


## 📦 Features

- 🧾 **AWS Billing** – Monitor cost and get budget alerts
- 📊 **EC2 Monitoring** – Detect high CPU usage
- 🚀 **App Runner** – Health check and service error tracking
- 🛡️ **Bedrock Guardrail** – Monitor safety interventions (Planned)

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- AWS credentials with permissions for:
  - Cost Explorer
  - EC2
  - App Runner
- Docker (optional)

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/whfan96/cjc101-starscout.git
   cd cjc101-starscout
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv fastapi-env
   source fastapi-env/bin/activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Create and edit the environment configuration

   ```bash
   cp .env.sample .env
   # Edit .env with your AWS credentials and settings
   ```

5. Start the FastAPI server

   ```bash
   uvicorn main:app --reload
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000

   ```

## 🔐 Environment Variables

`.env` file format:

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=us-east-1
```

> ⚠️ Do not commit `.env` to version control.

## 🧪 API Endpoints (Planned)

| Method | Path                | Description                       |
|--------|---------------------|-----------------------------------|
| GET    | /billing/summary    | Get AWS cost summary              |
| GET    | /ec2/monitor        | Monitor EC2 CPU usage             |
| GET    | /apprunner/health   | Check App Runner service health   |
| GET    | /guardrail/logs     | Get Bedrock Guardrail logs        |

---

## 📡 API 功能概覽

### 🖥️ EC2 監控（情境一）

- 查詢所有 EC2 instances
- 查詢單一 EC2 的 CPU 利用率（預設過去 1 小時平均）
- 查詢 EC2 狀態檢查結果
- 查詢 EC2 過去啟停/重啟事件

### 💰 成本預算助手（情境二）

- 查詢當月各服務成本
- 查詢過去 N 個月成本趨勢
- 每日成本查詢（預設近 7 天）
- 依標籤分析成本分佈
- 成本預測（簡單線性預估）
- 精打細算建議（示意資料）

### ⚙️ App Runner 監控（情境三）

- 查詢所有 App Runner 服務
- 查詢服務狀態（Running / Failed / Stopped）
- 查詢部署版本與最後部署時間
- 查詢錯誤率與延遲資訊（從 CloudWatch）

### 🛡️ Bedrock Guardrail（情境四）

- 查詢 Guardrail 介入事件
- 查詢事件時間、資源、介入原因
- 匯出介入記錄（CSV 檔）

---

## 🧪 API 測試方式

伺服器啟動後自動提供 Swagger UI：

> 📄 http://localhost:8000/docs

---



## 📝 License

MIT License

---

> Developed with ❤️ by [whfan96]

