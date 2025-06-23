from fastapi import FastAPI
from ec2_monitor import router as ec2_router
from billing_helper import router as billing_router
from apprunner_monitor import router as apprunner_router
from bedrock_guardrail import router as bedrock_router

app = FastAPI(
    title="AWS Multi-Scenario Monitoring API",
    description="API to monitor AWS EC2, Billing, App Runner and Bedrock Guardrail",
    version="1.0.0"
)

# 掛載不同情境的路由
app.include_router(ec2_router, prefix="/ec2", tags=["EC2 Monitoring"])
app.include_router(billing_router, prefix="/billing", tags=["Billing Helper"])
app.include_router(apprunner_router, prefix="/apprunner", tags=["App Runner Monitoring"])
app.include_router(bedrock_router, prefix="/bedrock", tags=["Bedrock Guardrail"])

@app.get("/")
async def root():
    return {"message": "Welcome to AWS Multi-Scenario Monitoring API"}

