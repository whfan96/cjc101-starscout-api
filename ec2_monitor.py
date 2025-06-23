from fastapi import APIRouter, HTTPException, Query
from aws_clients import ec2_client, cloudwatch_client
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/instances")
async def list_ec2_instances():
    """取得所有 EC2 instances 清單"""
    try:
        response = ec2_client.describe_instances()
        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "InstanceType": instance.get("InstanceType"),
                    "State": instance["State"]["Name"],
                    "LaunchTime": instance["LaunchTime"].isoformat(),
                    "PublicIpAddress": instance.get("PublicIpAddress"),
                    "PrivateIpAddress": instance.get("PrivateIpAddress"),
                    "Tags": instance.get("Tags", []),
                })
        return {"instances": instances}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list EC2 instances: {e}")

@router.get("/cpu-utilization/{instance_id}")
async def get_instance_cpu_utilization(
    instance_id: str,
    hours: int = Query(1, ge=1, le=24, description="過去多少小時的平均 CPU 利用率，預設 1 小時")
):
    """取得指定 EC2 instance 過去 N 小時 CPU 利用率平均值"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        metrics = cloudwatch_client.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5分鐘一個 datapoint
            Statistics=["Average"],
            Unit="Percent",
        )

        datapoints = metrics.get("Datapoints", [])
        if not datapoints:
            return {"instance_id": instance_id, "cpu_utilization_percent": None, "message": "No data found"}

        latest = max(datapoints, key=lambda x: x["Timestamp"])
        return {
            "instance_id": instance_id,
            "cpu_utilization_percent": round(latest["Average"], 2),
            "timestamp": latest["Timestamp"].isoformat(),
            "period_hours": hours
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get CPU utilization: {e}")

@router.get("/status-checks/{instance_id}")
async def get_instance_status_checks(instance_id: str):
    """取得 EC2 instance 狀態檢查結果 (System & Instance status checks)"""
    try:
        response = ec2_client.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
        statuses = response.get("InstanceStatuses", [])
        if not statuses:
            return {"instance_id": instance_id, "status_checks": None, "message": "No status information found"}

        status = statuses[0]
        system_status = status["SystemStatus"]["Status"]
        instance_status = status["InstanceStatus"]["Status"]

        return {
            "instance_id": instance_id,
            "system_status": system_status,
            "instance_status": instance_status,
            "details": status.get("SystemStatus", {}).get("Details", []) + status.get("InstanceStatus", {}).get("Details", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get instance status checks: {e}")

@router.get("/events/{instance_id}")
async def get_instance_events(instance_id: str):
    """查詢 EC2 instance 事件（如啟動、停止、重啟記錄）"""
    try:
        response = ec2_client.describe_instance_status(InstanceIds=[instance_id], IncludeAllInstances=True)
        statuses = response.get("InstanceStatuses", [])
        if not statuses:
            return {"instance_id": instance_id, "events": [], "message": "No status information found"}

        events = statuses[0].get("Events", [])
        event_list = []
        for event in events:
            event_list.append({
                "Code": event.get("Code"),
                "Description": event.get("Description"),
                "NotBefore": event.get("NotBefore").isoformat() if event.get("NotBefore") else None,
                "NotAfter": event.get("NotAfter").isoformat() if event.get("NotAfter") else None,
            })

        return {"instance_id": instance_id, "events": event_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get instance events: {e}")

