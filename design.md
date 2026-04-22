# 🧠 System Design — Apex Retail Store Intelligence

## 📌 Overview

This project implements an end-to-end pipeline for analyzing in-store customer behavior using CCTV footage. The goal is not just detection, but converting raw video into structured business events such as entry, exit, dwell time, and billing activity.

The system was developed iteratively, with multiple debugging steps, improvements, and design adjustments based on observed outputs.

---

## 🔄 End-to-End Pipeline

Video Input  
→ Person Detection (YOLOv8)  
→ Multi-Object Tracking (ByteTrack)  
→ Re-Identification (Custom Tracker)  
→ Event Generation Engine  
→ JSONL Event Storage  
→ FastAPI Backend  
→ Dashboard Visualization (Chart.js)

---

## 🎥 Input Handling

- Multi-camera setup:
  - Entry Camera (entry/exit detection)
  - Floor Cameras (zone tracking)
  - Billing Camera (queue & conversion tracking)
  - Backstore Camera (staff detection)

- Videos processed frame-by-frame using OpenCV
- FPS dynamically extracted from each clip

---

## 🤖 Detection & Tracking

### Object Detection
- YOLOv8 used for detecting persons (class 0)
- Confidence threshold applied to filter weak detections

### Tracking
- ByteTrack used to assign temporary track IDs
- Helps maintain identity across frames

### Re-Identification (Custom Layer)
- Built a `ReIDTracker` to maintain persistent visitor IDs
- Handles:
  - Re-entry detection
  - Session tracking
  - Identity continuity

⚠️ Limitation:
- Cross-camera ReID is not perfect
- ID switches can occur

---

## 📍 Spatial Logic

### Entry Detection
- Uses a horizontal line (`ENTRY_LINE_Y`)
- Crossing logic:
  - Top → Bottom → ENTRY
  - Bottom → Top → EXIT

### Zone Mapping
- Each camera mapped to a zone (e.g., PRODUCT_ZONE_A)
- First detection → ZONE_ENTER
- Exit → ZONE_EXIT

### Dwell Tracking
- Time inside zone tracked using frame difference
- Periodic events emitted:
  - `ZONE_DWELL` (heartbeat)
  - `LOITER_ALERT` (> threshold time)

---

## 🧾 Event System

All system outputs are structured as events:

### Event Types
- ENTRY / EXIT / REENTRY
- ZONE_ENTER / ZONE_EXIT
- ZONE_DWELL
- LOITER_ALERT
- BILLING_QUEUE_JOIN
- CROWD_ALERT

### Event Format
Stored as JSONL:
```json
{
  "visitor_id": "...",
  "event_type": "...",
  "timestamp": "...",
  "zone_id": "...",
  "dwell_ms": ...,
  "confidence": ...
}
