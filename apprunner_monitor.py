from fastapi import APIRouter, HTTPException, Query
from aws_clients import apprunner_client, cloudwatch_client
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/services", summary="列出所有 App Runner 服務")
def list_apprunner_services():
    services = apprunner_client.list_services()["ServiceSummaryList"]
    return [
        {
            "ServiceName": s["ServiceName"],
            "Status": s["Status"],
            "ServiceArn": s["ServiceArn"]
        } for s in services
    ]


@router.get("/service/deployments", summary="取得 App Runner 部署歷史")
def get_deployment_history(service_arn: str = Query(..., description="App Runner 服務 ARN")):
    try:
        response = apprunner_client.list_deployments(ServiceArn=service_arn)
        return response.get("DeploymentSummaryList", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/health", summary="取得服務健康狀態")
def get_service_health(service_arn: str = Query(..., description="App Runner 服務 ARN")):
    try:
        response = apprunner_client.describe_service(ServiceArn=service_arn)
        return {
            "Status": response["Service"]["Status"],
            "HealthStatus": response["Service"].get("HealthStatus", "Unknown"),
            "ServiceUrl": response["Service"].get("ServiceUrl"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service/error-metrics", summary="查詢錯誤率與請求失敗率")
def get_error_metrics(
    service_arn: str = Query(..., description="App Runner 服務 ARN"),
    minutes: int = Query(60, description="查詢過去幾分鐘內的錯誤率")
):
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)

        metrics = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/AppRunner",
            MetricName="4XXResponses",
            Dimensions=[{"Name": "ServiceArn", "Value": service_arn}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Sum"]
        )
        return {
            "MetricName": "4XXResponses",
            "StartTime": start_time.isoformat(),
            "EndTime": end_time.isoformat(),
            "Datapoints": metrics.get("Datapoints", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/service/restart", summary="重啟 App Runner 服務")
def restart_apprunner_service(service_arn: str = Query(..., description="App Runner 服務 ARN")):
    try:
        apprunner_client.pause_service(ServiceArn=service_arn)
        # 建議實務上可加入輪詢等待狀態切換完成
        apprunner_client.resume_service(ServiceArn=service_arn)
        return {"message": "Service restart triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

