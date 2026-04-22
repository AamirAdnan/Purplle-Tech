
---

# ⚙️ ✅ `CHOICES.md` (USE THIS)

```md
# ⚙️ Design Choices & Tradeoffs

This document explains the reasoning behind major decisions taken during development.

---

## 1. Choice: YOLOv8 for Detection

### Why?
- Easy to use with Python
- Fast inference
- Good enough for detecting people

### Tradeoff
- Not highly accurate in crowded scenes
- Cannot differentiate staff vs customers

---

## 2. Choice: ByteTrack for Tracking

### Why?
- Works well with YOLO outputs
- Handles multiple objects efficiently

### Tradeoff
- Track ID switches occur
- Impacts ReID accuracy

---

## 3. Choice: Custom ReIDTracker

### Why?
- Needed persistent identity across frames
- Helps detect re-entry and sessions

### Tradeoff
- Simplified logic → not robust
- Cross-camera identity tracking is weak

---

## 4. Choice: Event-Based Architecture

### Why?
- Converts raw video into meaningful business insights
- Easier to debug and analyze

### Tradeoff
- Requires careful event design
- Errors propagate into analytics

---

## 5. Choice: JSONL for Storage

### Why?
- Simple append-only format
- Easy to inspect manually
- Works well during development

### Tradeoff
- Not scalable
- No indexing or querying optimization

---

## 6. Choice: FastAPI Backend

### Why?
- Lightweight and fast
- Easy to build APIs

### Tradeoff
- No built-in frontend support
- Requires separate dashboard

---

## 7. Choice: Chart.js Dashboard

### Why?
- Quick to implement
- Lightweight

### Tradeoff
- Limited flexibility compared to modern frameworks
- Manual DOM handling caused initial bugs

---

## 8. Choice: Heuristic Staff Detection

### Why?
- No labeled dataset available
- Needed quick approximation

### Approach
- Backstore camera = staff
- Black outfit detection heuristic

### Tradeoff
- Major overcounting issue (observed in results)

---

## 9. Decision: Focus on Pipeline Over Accuracy

### Why?
- Assignment emphasizes system thinking
- Building end-to-end flow was prioritized

### Result
- Functional system with imperfect outputs

---

## 10. Debugging Learnings

During development, multiple real-world issues were encountered:

- Dependency installation failures (Rust, watchfiles)
- Path issues in Windows vs Colab
- Encoding errors in HTML loading
- Dashboard crashes due to missing elements
- No events generated due to incorrect entry line

These were resolved step-by-step and improved system stability.

---

## 🧠 Final Thought

This project is not a perfect AI system, but a realistic prototype demonstrating:
- System design
- Event-driven architecture
- Debugging and problem-solving

The focus was on building something complete and explainable rather than achieving perfect accuracy.
