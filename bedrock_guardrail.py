from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse
import csv
import io

router = APIRouter(prefix="/guardrail", tags=["Bedrock Guardrail"])

# 模擬資料（實際應整合 CloudTrail 或 Bedrock 審計事件）
MOCK_EVENTS = [
    {"id": "event001", "user": "userA", "resource": "model-1", "timestamp": "2025-06-20T14:30:00Z", "reason": "toxicity"},
    {"id": "event002", "user": "userB", "resource": "model-1", "timestamp": "2025-06-21T10:15:00Z", "reason": "jailbreak"},
    {"id": "event003", "user": "userA", "resource": "model-2", "timestamp": "2025-06-22T09:50:00Z", "reason": "bias"},
    {"id": "event004", "user": "userC", "resource": "model-1", "timestamp": "2025-06-23T01:12:00Z", "reason": "toxicity"},
]

# 查詢所有事件
@router.get("/events", summary="查詢所有 Guardrail 介入事件")
def get_all_guardrail_events():
    return MOCK_EVENTS

# 依使用者統計介入次數
@router.get("/events/group-by-user", summary="依使用者統計介入次數")
def count_events_by_user():
    result = {}
    for e in MOCK_EVENTS:
        result[e["user"]] = result.get(e["user"], 0) + 1
    return result

# 依資源統計介入次數
@router.get("/events/group-by-resource", summary="依資源統計介入次數")
def count_events_by_resource():
    result = {}
    for e in MOCK_EVENTS:
        result[e["resource"]] = result.get(e["resource"], 0) + 1
    return result

# 介入事件時間趨勢
@router.get("/events/trend", summary="介入事件時間趨勢")
def trend_by_day(days: int = 7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = {}
    for e in MOCK_EVENTS:
        ts = datetime.strptime(e["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        if ts >= cutoff:
            key = ts.strftime("%Y-%m-%d")
            result[key] = result.get(key, 0) + 1
    return result

# 匯出事件為 CSV 或 JSON
@router.get("/events/export", summary="匯出事件（JSON 或 CSV）")
def export_events(format: str = Query("json", enum=["json", "csv"])):
    if format == "json":
        return JSONResponse(content=MOCK_EVENTS)
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=MOCK_EVENTS[0].keys())
        writer.writeheader()
        for e in MOCK_EVENTS:
            writer.writerow(e)
        return JSONResponse(content={"csv": output.getvalue()})

# 查詢自訂規則（示範）
@router.get("/rules", summary="查詢自訂 Guardrail 規則")
def list_custom_rules():
    return {
        "rules": [
            {"name": "block-toxic", "type": "content-filter", "enabled": True},
            {"name": "prevent-jailbreak", "type": "input-sanitizer", "enabled": True},
        ]
    }

