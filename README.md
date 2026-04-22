# 🛍️ Apex Retail Store Intelligence

## 🚀 Overview
AI-powered system to analyze in-store customer behavior using CCTV footage.

## 🎯 Features
- Entry/Exit tracking
- Zone dwell time analysis
- Billing queue detection
- Conversion funnel
- Real-time dashboard

## ⚙️ Tech Stack
- Python (OpenCV, YOLOv8)
- FastAPI
- Chart.js

## ▶️ How to Run

1. Install dependencies
pip install -r requirements.txt

2. Run backend
uvicorn app.main:app --reload

3. Open dashboard
http://127.0.0.1:8000/dashboard

## 📊 Notes
- Model accuracy ~55% (improvable)
- Staff detection heuristic-based
- Built for pipeline demonstration, not production accuracy

## 📌 Future Improvements
- Better ReID tracking
- Improved model training
- Camera calibration
