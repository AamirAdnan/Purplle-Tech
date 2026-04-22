import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import Optional
from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────
# App setup
# ─────────────────────────────────────────────
app = FastAPI(title="Apex Retail — Store Intelligence")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Paths (FIXED)
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
EVENTS_FILE = BASE_DIR / "events.jsonl"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"

# ─────────────────────────────────────────────
# Load events
# ─────────────────────────────────────────────
def load_events():
    events = []
    if not EVENTS_FILE.exists():
        print("⚠️ events.jsonl not found")
        return events

    with open(EVENTS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception as e:
                print("⚠️ JSON parse error:", e)
                continue
    return events

# Optional caching (improves performance)
@lru_cache(maxsize=1)
def load_events_cached():
    return load_events()

# ─────────────────────────────────────────────
# Metrics computation
# ─────────────────────────────────────────────
def compute_metrics(events: list) -> dict:
    customer = [e for e in events if not e.get("is_staff")]
    staff    = [e for e in events if e.get("is_staff")]

    # Footfall
    entries   = [e for e in customer if e["event_type"] == "ENTRY"]
    exits     = [e for e in customer if e["event_type"] == "EXIT"]
    reentries = [e for e in customer if e["event_type"] == "REENTRY"]

    unique_visitors = len(set(e["visitor_id"] for e in entries))

    # Zone popularity
    zone_visits = Counter(
        e["zone_id"] for e in customer
        if e["event_type"] == "ZONE_ENTER" and e.get("zone_id")
    )

    # Dwell per zone
    zone_dwell = defaultdict(list)
    for e in customer:
        if e["event_type"] == "ZONE_EXIT" and e.get("zone_id") and e.get("dwell_ms", 0) > 0:
            zone_dwell[e["zone_id"]].append(e["dwell_ms"])

    avg_dwell = {
        z: round(sum(d) / len(d) / 1000, 1)
        for z, d in zone_dwell.items()
    }

    # Billing
    billing_visitors = set(
        e["visitor_id"] for e in customer if e.get("zone_id") == "BILLING"
    )

    conversion_rate = round(
        len(billing_visitors) / unique_visitors * 100, 1
    ) if unique_visitors else 0.0

    queue_events = [e for e in customer if e["event_type"] == "BILLING_QUEUE_JOIN"]

    max_queue = max(
        (e.get("metadata", {}).get("queue_depth") or 0 for e in queue_events),
        default=0
    )

    avg_queue = round(
        sum(e.get("metadata", {}).get("queue_depth") or 0 for e in queue_events)
        / max(len(queue_events), 1), 1
    )

    abandons = [e for e in customer if e["event_type"] == "BILLING_QUEUE_ABANDON"]

    abandon_rate = round(
        len(abandons) / len(billing_visitors) * 100, 1
    ) if billing_visitors else 0.0

    # Funnel
    product_zone_visitors = set(
        e["visitor_id"] for e in customer
        if e.get("zone_id") in ("PRODUCT_ZONE_A", "PRODUCT_ZONE_B")
    )

    # Hourly traffic
    hourly = Counter()
    for e in entries:
        try:
            h = datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).hour
            hourly[h] += 1
        except:
            continue

    hourly_data = [
        {"hour": f"{h:02d}:00", "visitors": hourly[h]}
        for h in sorted(hourly)
    ]

    # Confidence
    confs = [e.get("confidence", 0) for e in events]
    avg_conf = round(sum(confs) / len(confs), 2) if confs else 0.0
    low_conf = sum(1 for c in confs if c < 0.5)

    # Anomalies
    anomalies = []

    if conversion_rate < 20:
        anomalies.append({
            "type": "CONVERSION_DROP",
            "severity": "CRITICAL",
            "message": f"Conversion rate is only {conversion_rate}% — below 20% threshold.",
            "action": "Improve product placement or staff engagement."
        })

    if avg_queue > 3:
        anomalies.append({
            "type": "BILLING_QUEUE_SPIKE",
            "severity": "WARN",
            "message": f"Average queue depth is {avg_queue}.",
            "action": "Open additional billing counters."
        })

    if abandon_rate > 30:
        anomalies.append({
            "type": "HIGH_ABANDONMENT",
            "severity": "WARN",
            "message": f"{abandon_rate}% customers abandon billing queue.",
            "action": "Reduce wait time."
        })

    if not anomalies:
        anomalies.append({
            "type": "ALL_CLEAR",
            "severity": "INFO",
            "message": "No anomalies detected.",
            "action": ""
        })

    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "footfall": {
            "unique_visitors": unique_visitors,
            "entries": len(entries),
            "exits": len(exits),
            "reentries": len(reentries),
            "staff_detected": len(set(e["visitor_id"] for e in staff)),
        },
        "conversion": {
            "rate_pct": conversion_rate,
            "billing_visitors": len(billing_visitors),
        },
        "billing": {
            "max_queue": max_queue,
            "avg_queue": avg_queue,
            "abandon_rate_pct": abandon_rate,
        },
        "zones": {
            "visits": dict(zone_visits),
            "avg_dwell_seconds": avg_dwell,
        },
        "funnel": [
            {"stage": "Entry", "count": unique_visitors},
            {"stage": "Product Zone", "count": len(product_zone_visitors)},
            {"stage": "Billing", "count": len(billing_visitors)},
        ],
        "hourly_traffic": hourly_data,
        "detection": {
            "total_events": len(events),
            "avg_confidence": avg_conf,
            "low_confidence_events": low_conf,
        },
        "anomalies": anomalies,
    }

# ─────────────────────────────────────────────
# API endpoints
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message": "Apex Retail Store Intelligence API 🚀",
        "endpoints": ["/api/metrics", "/dashboard", "/health"]
    }

@app.get("/api/metrics")
def get_metrics():
    events = load_events_cached()
    return JSONResponse(compute_metrics(events))

@app.get("/health")
def health():
    return {
        "status": "ok",
        "events_file_exists": EVENTS_FILE.exists()
    }

# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────
@app.get("/dashboard")
def dashboard():
    if not DASHBOARD_FILE.exists():
        return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)

    return HTMLResponse(DASHBOARD_FILE.read_text(encoding="utf-8"))