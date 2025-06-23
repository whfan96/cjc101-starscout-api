import os
import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, APIRouter
from typing import Optional, List
from datetime import datetime, timedelta, date
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

# Load environment variables from .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

app = FastAPI(
    title="AWS Monitoring API",
    description="API to monitor AWS EC2, App Runner, Billing, Logs, and Bedrock Guardrail events.",
    version="1.0.0",
)

def get_boto3_client(service_name: str):
    """
    Create and return a boto3 client for the given AWS service.
    Raises HTTPException on failure.
    """
    try:
        client = boto3.client(
            service_name,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating boto3 client: {str(e)}")

# --- EC2 Router ---
ec2_router = APIRouter(prefix="/ec2", tags=["EC2"])

@ec2_router.get("/instances", summary="List EC2 Instances", description="Retrieve a list of all EC2 instances with details.")
async def list_ec2_instances():
    ec2 = get_boto3_client("ec2")
    try:
        response = ec2.describe_instances()
        instances = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    "instance_id": instance.get("InstanceId"),
                    "instance_type": instance.get("InstanceType"),
                    "state": instance.get("State", {}).get("Name"),
                    "launch_time": instance.get("LaunchTime").isoformat() if instance.get("LaunchTime") else None,
                    "public_ip": instance.get("PublicIpAddress", None),
                    "private_ip": instance.get("PrivateIpAddress", None),
                    "availability_zone": instance.get("Placement", {}).get("AvailabilityZone")
                })

        return {"instance_count": len(instances), "instances": instances}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@ec2_router.get("/cpu_high/{instance_id}", summary="Check High CPU Usage for EC2", description="Check if the EC2 instance CPU utilization is higher than 80% in the last 10 minutes.")
async def check_ec2_cpu_high(instance_id: str):
    cloudwatch = get_boto3_client("cloudwatch")
    try:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=datetime.utcnow() - timedelta(minutes=10),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=['Average']
        )
        datapoints = response.get('Datapoints', [])
        if not datapoints:
            return {"instance_id": instance_id, "cpu_high": False, "message": "No data"}
        average_cpu = datapoints[-1]['Average']
        cpu_high = average_cpu > 80.0
        return {"instance_id": instance_id, "cpu_high": cpu_high, "average_cpu": average_cpu}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- App Runner Router ---
apprunner_router = APIRouter(prefix="/apprunner", tags=["AppRunner"])

@apprunner_router.get("/status/{service_arn}", summary="Check App Runner Service Status", description="Retrieve the current status of an App Runner service by ARN.")
async def check_apprunner_status(service_arn: str):
    apprunner = get_boto3_client("apprunner")
    try:
        response = apprunner.describe_service(ServiceArn=service_arn)
        status = response['Service']['Status']
        return {"service_arn": service_arn, "status": status}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Bedrock Guardrail Router ---
bedrock_router = APIRouter(prefix="/bedrock", tags=["Bedrock"])

@bedrock_router.get("/guardrail_events", summary="Get Bedrock Guardrail Events", description="Retrieve recent guardrail events from AWS Bedrock logs.")
async def check_bedrock_guardrail():
    logs = get_boto3_client("logs")
    try:
        log_group = "/aws/bedrock/guardrail"
        streams = logs.describe_log_streams(logGroupName=log_group, limit=5)
        events = []
        for stream in streams['logStreams']:
            response = logs.get_log_events(
                logGroupName=log_group,
                logStreamName=stream['logStreamName'],
                limit=10,
                startFromHead=False
            )
            for event in response['events']:
                events.append(event['message'])
        return {"guardrail_events": events}
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Logs Router ---
logs_router = APIRouter(prefix="/logs", tags=["Logs"])

@logs_router.get("/vpc-flowlogs", summary="List VPC Flow Logs", description="Retrieve recent log events from VPC Flow Logs log group.")
async def list_vpc_flow_logs(limit_streams: int = Query(3, ge=1, le=10, description="Number of log streams to retrieve"),
                             limit_events: int = Query(5, ge=1, le=50, description="Number of events per log stream")):
    logs = get_boto3_client("logs")
    log_group_name = "cjc101-starscout-vpc-flowlogs"
    try:
        streams_response = logs.describe_log_streams(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
            limit=limit_streams
        )
        results = []
        for stream in streams_response['logStreams']:
            stream_name = stream['logStreamName']
            log_events = logs.get_log_events(
                logGroupName=log_group_name,
                logStreamName=stream_name,
                limit=limit_events,
                startFromHead=False
            )
            events = [e['message'] for e in log_events.get('events', [])]
            results.append({
                "log_stream_name": stream_name,
                "latest_events": events
            })
        return {
            "log_group": log_group_name,
            "stream_count": len(results),
            "streams": results
        }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@logs_router.get("/", summary="Query Logs", description="Query logs with optional filters by log group, stream, and keyword within a recent time window.")
async def query_logs(
    log_group_name: str = Query(..., description="Name of the log group to query"),
    log_stream_name: Optional[str] = Query(None, description="Optional log stream name to filter"),
    keyword: Optional[str] = Query(None, description="Optional keyword filter pattern"),
    start_minutes_ago: int = Query(60, ge=1, le=1440, description="Minutes back from now to start querying")
):
    logs = get_boto3_client("logs")
    try:
        params = {
            'logGroupName': log_group_name,
            'startTime': int((datetime.utcnow() - timedelta(minutes=start_minutes_ago)).timestamp() * 1000),
            'endTime': int(datetime.utcnow().timestamp() * 1000),
            'limit': 50,
        }
        if log_stream_name:
            params['logStreamNames'] = [log_stream_name]
        if keyword:
            params['filterPattern'] = keyword
        response = logs.filter_log_events(**params)
        logs_output = []
        for event in response.get('events', []):
            logs_output.append({
                "timestamp": event['timestamp'],
                "message": event['message'],
                "logStreamName": event['logStreamName']
            })
        return {
            "log_group": log_group_name,
            "log_stream": log_stream_name,
            "keyword": keyword,
            "start_minutes_ago": start_minutes_ago,
            "matched_logs": logs_output
        }
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Billing Router and Models ---
billing_router = APIRouter(prefix="/billing", tags=["Billing"])

class CostSummary(BaseModel):
    period_start: date = Field(..., description="Start date of the billing period")
    period_end: date = Field(..., description="End date of the billing period")
    cost_usd: float = Field(..., description="Total cost in USD for the period")

class DailyCost(BaseModel):
    cost_date: date = Field(..., description="The date of the daily cost")
    cost_usd: float = Field(..., description="Cost amount in USD for that date")

class ServiceCost(BaseModel):
    service: str = Field(..., description="AWS Service name")
    cost_usd: float = Field(..., description="Cost amount in USD for the service")

class BudgetThreshold(BaseModel):
    monthly_budget_usd: float = Field(..., description="Monthly budget limit in USD")
    alert_triggered: bool = Field(..., description="Indicates if alert is triggered")
    current_cost_usd: float = Field(..., description="Current cost in USD")
    alert_sent_at: Optional[datetime] = Field(None, description="Timestamp when alert was sent")

class AlertRecord(BaseModel):
    alert_id: int = Field(..., description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    triggered_at: datetime = Field(..., description="Timestamp when alert was triggered")
    message: str = Field(..., description="Alert message")

@billing_router.get("/cost_summary", response_model=CostSummary, summary="Get Monthly Cost Summary", description="Retrieve the total AWS cost for the current month.")
async def get_cost_summary():
    ce = get_boto3_client("ce")
    try:
        start = datetime.today().replace(day=1).date()
        end = datetime.today().date()
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start.strftime('%Y-%m-%d'), 'End': end.strftime('%Y-%m-%d')},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
        return CostSummary(period_start=start, period_end=end, cost_usd=cost)
    except ClientError as e:
        raise HTTPException(status_code=400, detail=str(e))

@billing_router.get("/daily_costs", response_model=List[DailyCost], summary="Get Daily Costs", description="Simulated daily costs for the past N days.")
async def get_daily_costs(days: int = Query(30, ge=1, le=90, description="Number of days for daily cost data")):
    today = date.today()
    daily_costs = [
        DailyCost(cost_date=today - timedelta(days=i), cost_usd=round(2 + i * 0.1, 2))
        for i in range(days)
    ]
    return daily_costs

@billing_router.get("/cost_by_service", response_model=List[ServiceCost], summary="Get Cost by Service", description="Simulated costs broken down by AWS service.")
async def get_cost_by_service():
    return [
        ServiceCost(service="Amazon EC2", cost_usd=75.32),
        ServiceCost(service="Amazon S3", cost_usd=25.87),
        ServiceCost(service="AWS Lambda", cost_usd=12.25),
    ]

@billing_router.get("/budget/thresholds", response_model=BudgetThreshold, summary="Get Budget Thresholds", description="Retrieve simulated budget thresholds and alert status.")
async def get_budget_threshold():
    return BudgetThreshold(
        monthly_budget_usd=150.0,
        alert_triggered=True,
        current_cost_usd=160.75,
        alert_sent_at=datetime(2025, 6, 22, 10, 30)
    )

@billing_router.get("/alerts/history", response_model=List[AlertRecord], summary="Get Alert History", description="Retrieve historical alert records.")
async def get_alert_history():
    return [
        AlertRecord(alert_id=1, alert_type="EC2_CPU_High", triggered_at=datetime(2025, 6, 21, 9, 15), message="EC2 i-1234567890 CPU usage > 80%"),
        AlertRecord(alert_id=2, alert_type="Budget_Exceeded", triggered_at=datetime(2025, 6, 20, 14, 30), message="Monthly budget exceeded"),
    ]

# Include routers
app.include_router(ec2_router)
app.include_router(apprunner_router)
app.include_router(bedrock_router)
app.include_router(logs_router)
app.include_router(billing_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to AWS Monitoring API"}


