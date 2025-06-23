# 🌟 cjc101-starscout

A FastAPI-based monitoring tool for AWS services including EC2, App Runner, and Billing.  
Provides API endpoints to track cost, resource usage, and guardrail interventions.

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
   git clone https://github.com/yourname/cjc101-starscout.git
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

## 📝 License

MIT License

---

> Developed with ❤️ by [whfan96]

