# CHOICES.md 

This document outlines key architectural decisions made during the development of the Store Intelligence system.

---

## 1. Detection Model: YOLOv8 Nano

Options Considered:
- YOLOv8n (Nano)
- YOLOv8s (Small)
- RT-DETR

AI Suggestion:
Gemini suggested YOLOv8s for better accuracy in crowded scenes.

My Choice:
YOLOv8n (Nano)

Rationale:
The primary requirement was real-time or near real-time processing on limited hardware. YOLOv8n provides significantly faster inference (~25–30 FPS on CPU), which allows the system to handle multiple cameras and additional processing like tracking and event generation.

While YOLOv8s offers better accuracy, YOLOv8n was sufficient for detecting people in a typical retail environment and ensured system responsiveness.

Tradeoff:
Lower accuracy → observed confidence ~55% and occasional missed detections.

---

## 2. Tracking Algorithm: ByteTrack

Options Considered:
- SORT
- DeepSORT
- ByteTrack

AI Suggestion:
ByteTrack recommended for handling occlusion better.

My Choice:
ByteTrack

Rationale:
ByteTrack performs well in crowded scenes and integrates easily with YOLO outputs. It was chosen for its balance between speed and tracking stability.

Tradeoff:
Track ID switches occur, which affects ReID accuracy.

---

## 3. Event Schema: Flat vs Nested

Options Considered:

Nested:
{
  visitor: { id: 1, type: "staff" },
  event: { ... }
}

Flat:
{
  visitor_id: 1,
  is_staff: true,
  ...
}

AI Suggestion:
Claude suggested a nested JSON structure for flexibility.

My Choice:
Flat schema

Rationale:
The system frequently filters and aggregates data (e.g., excluding staff). A flat schema allows faster access and simpler aggregation logic without nested traversal.

Tradeoff:
Less flexible for deeply structured metadata.

---

## 4. Storage Format: JSONL

Options Considered:
- JSON file
- CSV
- Database

My Choice:
JSONL (JSON Lines)

Rationale:
- Append-only → perfect for streaming events
- Easy to debug manually
- Simple to integrate with pipeline

Tradeoff:
- Not scalable
- No indexing

---

## 5. API Architecture: FastAPI

Options Considered:
- Flask
- FastAPI
- Node.js (Express)

AI Suggestion:
FastAPI recommended for async support and validation.

My Choice:
FastAPI

Rationale:
- Lightweight and fast
- Built-in validation using Pydantic
- Easy API creation

Tradeoff:
- No frontend → required separate dashboard

---

## 6. Dashboard Technology: Chart.js

Options Considered:
- React dashboard
- Streamlit
- Chart.js

My Choice:
Chart.js with plain HTML

Rationale:
- Quick to implement
- Lightweight
- Sufficient for visualization

Tradeoff:
- Manual DOM handling caused bugs (e.g., null element errors)
- Less scalable than full frontend frameworks

---

## 7. Staff Detection Approach

Options Considered:
- Trained classification model
- Heuristic-based detection

My Choice:
Heuristic approach

Implementation:
- Backstore camera → staff
- Black outfit detection

Rationale:
No labeled dataset was available, so heuristic rules were used for quick implementation.

Tradeoff:
Significant overcounting observed (100+ vs actual ~9 staff)

---

## 8. Event-Based Architecture

My Choice:
Convert all outputs into structured events

Rationale:
- Easier debugging
- Decouples detection from analytics
- Enables flexible metric computation

Tradeoff:
Errors in early stages propagate to final metrics

---

## 9. Anomaly Detection Strategy

My Choice:
Threshold-based logic

Rationale:
Machine learning-based anomaly detection requires historical data. For a fresh deployment, simple rules (e.g., low conversion, high queue) provide immediate insights.

Enhancement:
Added `suggested_action` to convert analytics into actionable insights.

---

## 10. Development Approach

Key Decision:
Focus on building a complete pipeline rather than perfect accuracy

Rationale:
The goal was to demonstrate:
- System design
- Event-driven architecture
- Debugging ability

Outcome:
A fully working system with imperfect but explainable results

---

## Final Thought

This project is intentionally not optimized for perfect accuracy. Instead, it demonstrates how raw video data can be transformed into structured insights through a complete, end-to-end pipeline.
