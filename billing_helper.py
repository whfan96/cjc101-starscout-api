from fastapi import APIRouter, HTTPException, Query
from aws_clients import cost_explorer_client
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

def format_date(date_obj):
    return date_obj.strftime("%Y-%m-%d")

@router.get("/daily-cost")
async def get_daily_cost(days: Optional[int] = Query(7, ge=1, le=90, description="查詢過去幾天每日成本，預設7天")):
    """
    查詢過去 N 天每日成本
    """
    try:
        end_date = datetime.utcnow().date() + timedelta(days=1)  # AWS API EndDate 是 exclusive
        start_date = end_date - timedelta(days=days)

        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={"Start": format_date(start_date), "End": format_date(end_date)},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
        )

        daily_costs = []
        for result in response["ResultsByTime"]:
            daily_costs.append({
                "date": result["TimePeriod"]["Start"],
                "amount": float(result["Total"]["UnblendedCost"]["Amount"]),
                "unit": result["Total"]["UnblendedCost"]["Unit"]
            })

        return {"daily_costs": daily_costs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily cost: {e}")

@router.get("/current-month-cost")
async def get_current_month_cost():
    """
    取得本月（從月初到今天）依服務分類的成本
    """
    try:
        today = datetime.utcnow().date()
        start_of_month = today.replace(day=1)
        end_date = today + timedelta(days=1)  # EndDate 是 exclusive

        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={"Start": format_date(start_of_month), "End": format_date(end_date)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        results = []
        for group in response["ResultsByTime"][0]["Groups"]:
            service = group["Keys"][0]
            amount = group["Metrics"]["UnblendedCost"]["Amount"]
            unit = group["Metrics"]["UnblendedCost"]["Unit"]
            results.append({"service": service, "amount": float(amount), "unit": unit})

        total = float(response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

        return {"start_date": format_date(start_of_month), "end_date": format_date(today), "total_cost": total, "services": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current month cost: {e}")

@router.get("/months-trend")
async def get_months_trend(months: Optional[int] = Query(1, ge=1, le=12, description="查詢過去幾個月的成本趨勢，預設1個月")):
    """
    取得過去 N 個月依月份的成本趨勢
    """
    try:
        today = datetime.utcnow().date()
        first_day_this_month = today.replace(day=1)

        # 計算起始月份 (N個月前第一天)
        year = first_day_this_month.year
        month = first_day_this_month.month - months
        while month <= 0:
            month += 12
            year -= 1
        start_date = datetime(year, month, 1).date()

        end_date = first_day_this_month

        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={"Start": format_date(start_date), "End": format_date(end_date)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )

        trend = []
        for result in response["ResultsByTime"]:
            trend.append({
                "start": result["TimePeriod"]["Start"],
                "end": result["TimePeriod"]["End"],
                "amount": float(result["Total"]["UnblendedCost"]["Amount"])
            })

        return {"trend": trend}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get months trend: {e}")

@router.get("/cost-by-tag")
async def get_cost_by_tag(tag_key: str = Query(..., description="查詢特定標籤鍵的成本")):
    """
    依標籤 Key 查詢成本分佈
    """
    try:
        today = datetime.utcnow().date()
        start_of_month = today.replace(day=1)
        end_date = today + timedelta(days=1)

        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={"Start": format_date(start_of_month), "End": format_date(end_date)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "TAG", "Key": f"user:{tag_key}"}],
        )

        results = []
        for group in response["ResultsByTime"][0]["Groups"]:
            tag_value = group["Keys"][0]
            amount = group["Metrics"]["UnblendedCost"]["Amount"]
            unit = group["Metrics"]["UnblendedCost"]["Unit"]
            results.append({"tag_value": tag_value, "amount": float(amount), "unit": unit})

        total = float(response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

        return {"tag_key": tag_key, "total_cost": total, "breakdown": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cost by tag: {e}")

@router.get("/cost-forecast")
async def cost_forecast(days: Optional[int] = Query(7, ge=1, le=30, description="預估未來幾天成本")):
    """
    簡單的成本預估(未來幾天)：
    用當月平均日成本乘以天數推估。
    """
    try:
        today = datetime.utcnow().date()
        start_of_month = today.replace(day=1)
        days_passed = (today - start_of_month).days + 1

        response = cost_explorer_client.get_cost_and_usage(
            TimePeriod={"Start": format_date(start_of_month), "End": format_date(today + timedelta(days=1))},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
        )

        daily_costs = [float(result["Total"]["UnblendedCost"]["Amount"]) for result in response["ResultsByTime"]]

        avg_daily_cost = sum(daily_costs) / days_passed if days_passed > 0 else 0
        forecast_cost = avg_daily_cost * days

        return {
            "avg_daily_cost": round(avg_daily_cost, 4),
            "forecast_days": days,
            "forecast_cost": round(forecast_cost, 4),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to forecast cost: {e}")

@router.get("/saving-tips")
async def saving_tips():
    """
    節約建議示範 (實際建議可更複雜，例如根據使用狀況)
    """
    tips = [
        "檢查並關閉未使用的 EC2 實例。",
        "使用 Reserved Instances 或 Savings Plans 降低長期成本。",
        "刪除未使用的 Elastic IP 和 EBS 卷。",
        "利用自動化工具調整過度配置的資源。",
        "定期審查 S3 存儲類型，選擇成本更低的選項。",
    ]
    return {"saving_tips": tips}

