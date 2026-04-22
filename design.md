# DESIGN.md

This document describes the architecture and flow of the Store Intelligence system built for analyzing retail CCTV footage.

---

## 1. System Overview

The system converts raw multi-camera CCTV footage into structured business events such as:
- Entry / Exit
- Zone activity
- Dwell time
- Billing behavior

These events are then aggregated into metrics and visualized in a dashboard.

---

## 2. High-Level Pipeline

Video Input  
→ Object Detection (YOLOv8)  
→ Tracking (ByteTrack)  
→ Re-Identification (Custom Logic)  
→ Event Generation  
→ JSONL Storage  
→ FastAPI Backend  
→ Dashboard (Chart.js)

---

## 3. Video Processing Layer

### Input
- Multiple camera feeds:
  - Entry camera
  - Floor cameras
  - Billing camera
  - Backstore camera

### Processing
- Frames extracted using OpenCV
- FPS dynamically read from each video
- Each frame passed into detection + tracking pipeline

---

## 4. Detection & Tracking

### Detection Model
- YOLOv8 (person class only)
- Confidence threshold applied to reduce noise

### Tracking
- ByteTrack assigns track IDs per person
- Helps maintain identity across frames

---

## 5. Re-Identification Layer

### Problem
Tracking IDs reset frequently, especially across cameras.

### Solution
A custom `ReIDTracker` was implemented to:
- Maintain persistent visitor IDs
- Detect re-entry
- Track session sequence

### Limitation
- Cross-camera identity matching is not fully reliable
- ID switches observed during crowded scenes

---

## 6. Spatial Logic (Core of System)

### Entry Detection
- Based on line-crossing logic
- A horizontal line is placed in entry camera
- Movement direction determines:
  - ENTRY
  - EXIT

### Zone Mapping
- Each camera corresponds to a zone
- First detection → ZONE_ENTER
- Leaving → ZONE_EXIT

### Dwell & Loitering
- Time tracked using frame difference
- Periodic events emitted:
  - ZONE_DWELL (heartbeat)
  - LOITER_ALERT (after threshold)

---

## 7. Event System

### Design
All outputs are converted into structured events.

### Example Events
- ENTRY / EXIT / REENTRY
- ZONE_ENTER / ZONE_EXIT
- ZONE_DWELL
- BILLING_QUEUE_JOIN
- CROWD_ALERT

### Storage
- Stored as JSONL (append-only)
- Each line = one event

---

## 8. Backend Layer (FastAPI)

### Responsibilities
- Read event file
- Compute metrics
- Serve API endpoints

### Metrics Computed
- Footfall
- Conversion rate
- Zone popularity
- Average dwell time
- Queue statistics
- Hourly traffic

---

## 9. Dashboard Layer

### Technology
- HTML + CSS + Chart.js

### Features
- KPI cards (Visitors, Conversion, Queue, Events)
- Funnel visualization
- Zone popularity chart
- Traffic trends
- Insights / anomaly detection

### Enhancements Added
- Animations
- Auto-refresh
- Interactive charts

---

## 10. Issues Faced During Development

Some real challenges encountered:

- No events generated initially due to wrong entry line placement
- cv2.imshow not working in Colab → switched to cv2_imshow
- Encoding issues while loading HTML dashboard
- Dashboard crashing due to missing DOM elements
- Staff detection giving unrealistic counts (100+ instead of ~9)
- Low model confidence (~55%)

All issues were debugged step-by-step.

---

## 11. Limitations

- Model accuracy is low (~55%)
- Staff detection is heuristic-based
- ReID is not robust across cameras
- JSONL not scalable for large systems

---

## 12. Future Improvements

- Train custom classification model (staff vs customer)
- Improve ReID using embeddings
- Replace JSONL with streaming pipeline (Kafka)
- Add camera calibration
- Real-time deployment
