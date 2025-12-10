#!/usr/bin/env python3
"""
VisioNar – Visual-Audio Assistance using YOLOv8 + Async TTS
Adds: circular history buffer (JSONL export), proximity, movement, environmental messages.
"""

import cv2
import pyttsx3
from ultralytics import YOLO
import time
import queue
import threading
import json
from collections import defaultdict, deque
from datetime import datetime, timezone


# ===========================
# CONFIG
# ===========================
TTS_INTERVAL = 3
STABLE_FRAMES = 10
STABLE_DECAY = 1
CONF_THRESHOLD = 0.50

# History buffer
HISTORY_SIZE = 1000  # circular buffer length
history = deque(maxlen=HISTORY_SIZE)

# ===========================
# ASYNC TTS
# ===========================
tts_queue = queue.Queue()

def tts_worker():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # selecciona la voz 1
    engine.setProperty('rate', 140)

    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()

tts_thread = threading.Thread(target=tts_worker, daemon=True)
tts_thread.start()

def speak_async(text):
    tts_queue.put(text)

# ===========================
# HELPERS
# ===========================
def get_position(x_center, width):
    if x_center < width * 0.33:
        return "on your left"
    elif x_center > width * 0.66:
        return "on your right"
    else:
        return "in front of you"

def get_proximity(area, frame_area):
    rel_area = area / frame_area if frame_area > 0 else 0.0
    if rel_area > 0.15:
        return "very close"
    elif rel_area > 0.05:
        return "nearby"
    else:
        return "far away"

irregular = {"person": "people"}
def plural(label, count):
    if count == 1:
        return label
    if label in irregular:
        return irregular[label]
    return label + "s"

# ===========================
# STABILITY & MOVEMENT TRACKERS
# ===========================
stable_counter = defaultdict(int)
prev_areas = defaultdict(float)  # previous area per label (simple per-class approx)

# ===========================
# BUILD SCENE DESCRIPTION (returns text + metadata)
# ===========================
def build_scene_description_and_meta(detections, frame_w, frame_area):
    """
    detections: list of dict with keys: label, area, x, conf
    returns: (description_str, metadata_list)
    metadata_list: [{'label', 'conf', 'area', 'x', 'proximity', 'movement'}...]
    """

    if len(detections) == 0:
        # environmental message as metadata empty
        return "The area is clear. Move slowly and stay alert.", []

    # sort by area descending
    detections = sorted(detections, key=lambda d: d["area"], reverse=True)

    counts = defaultdict(int)
    positions = defaultdict(list)
    proximity_info = {}
    movement_info = {}
    metadata = []

    # compute proximity & movement and build per-detection metadata
    for d in detections:
        lbl = d["label"]
        counts[lbl] += 1
        positions[lbl].append(get_position(d["x"], frame_w))

        prox = get_proximity(d["area"], frame_area)
        prev_area = prev_areas.get(lbl, d["area"])
        move = None
        if d["area"] > prev_area * 1.1:
            move = "approaching"
        elif d["area"] < prev_area * 0.9:
            move = "moving away"

        proximity_info[lbl] = prox
        movement_info[lbl] = move
        # store metadata per detection (we'll dedupe counts later)
        metadata.append({
            "label": lbl,
            "conf": d.get("conf", None),
            "area": d["area"],
            "x": d["x"],
            "proximity": prox,
            "movement": move
        })

        # update prev_areas so movement is relative frame-to-frame across iterations
        prev_areas[lbl] = d["area"]

    # Build textual description
    main = detections[0]
    main_label = main["label"]
    main_count = counts[main_label]
    main_pos = get_position(main["x"], frame_w)
    main_prox = proximity_info[main_label]
    main_move = movement_info[main_label]

    if main_count == 1:
        desc = f"I see a {main_label} {main_pos}, {main_prox}"
    else:
        desc = f"I see {main_count} {plural(main_label, main_count)} {main_pos}, {main_prox}"

    if main_move:
        desc += f", {main_move}"

    # other objects summary
    remaining = {k: v for k, v in counts.items() if k != main_label}
    if len(remaining) > 0:
        parts = []
        for lbl, cnt in remaining.items():
            poslist = positions[lbl]
            pos = max(set(poslist), key=poslist.count)
            prox = proximity_info.get(lbl)
            move = movement_info.get(lbl)
            part = f"{cnt} {plural(lbl, cnt)} {pos}, {prox}"
            if move:
                part += f", {move}"
            parts.append(part)
        desc += ". Also " + ", ".join(parts)

    desc += "."

    return desc, metadata

# ===========================
# SAVE HISTORY TO JSONL + SUMMARY
# ===========================
def export_history_jsonl(path=None, top_n=5):
    """
    Export history buffer to JSONL and generate a summary of top detected classes.
    """
    if path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"logs/visionar_history_date_{ts}.jsonl"
    try:
        # Write full history
        with open(path, "w", encoding="utf-8") as f:
            for entry in history:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"History exported to {path}")

        # Generate summary
        class_counts = defaultdict(int)
        frames_per_class = defaultdict(int)

        for entry in history:
            labels_in_frame = set()
            for d in entry["detections"]:
                lbl = d["label"]
                class_counts[lbl] += 1
                labels_in_frame.add(lbl)
            for lbl in labels_in_frame:
                frames_per_class[lbl] += 1

        # Top-N classes by total occurrences
        top_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

        summary = {
            "total_entries": len(history),
            "top_classes": top_classes,
            "frames_per_class": dict(frames_per_class)
        }

        summary_path = path.replace("history_", "summary_").replace(".jsonl", ".json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"Summary exported to {summary_path}")

    except Exception as e:
        print("Failed to export history or summary:", e)


# ===========================
# LOAD MODEL
# ===========================
print("Loading YOLOv8n.pt...")
model = YOLO("models/yolov8n.pt")
print("Model loaded.")

# ===========================
# CAMERA
# ===========================
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: camera not accessible.")
    exit()

cv2.namedWindow("Visual Computing Project - VisioNar (Visual Assistance")
prev_time = 0
last_tts_time = 0
last_description = ""

print("Press 'q' to quit.")

# ===========================
# WELCOME MESSAGE
# ===========================
welcome_message = ( "Welcome to VisioNar, a visual computing project designed to support " 
                   "people with visual impairments by providing real time audio descriptions " 
                   "of their surroundings. This prototype uses object detection, live video " 
                   "processing and intelligent speech feedback to enhance environmental "
                    "awareness, independence, and safety... Press q to quit VisioNar... Starting system now." )

print(welcome_message)
speak_async(welcome_message)
time.sleep(20)

# ===========================
# MAIN LOOP
# ===========================
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_h, frame_w = frame.shape[:2]
        frame_area = float(frame_w * frame_h)
        current_time = time.time()

        fps = 1 / (current_time - prev_time) if prev_time else 0
        prev_time = current_time

        # YOLO inference
        results = model(frame, imgsz=640, verbose=False)
        result = results[0]

        frame_dets = []
        seen_in_frame = set()

        for box in result.boxes:
            conf = float(box.conf[0])
            if conf < CONF_THRESHOLD:
                continue
            cls = int(box.cls[0])
            label = model.names[cls]
            x1, y1, x2, y2 = box.xyxy[0]
            area = float((x2 - x1) * (y2 - y1))
            x_center = int((x1 + x2) / 2)
            frame_dets.append({"label": label, "area": area, "x": x_center, "conf": conf})
            seen_in_frame.add(label)

        # Stability update
        for lbl in seen_in_frame:
            stable_counter[lbl] += 1
        for lbl in list(stable_counter.keys()):
            if lbl not in seen_in_frame:
                stable_counter[lbl] -= STABLE_DECAY
                if stable_counter[lbl] <= 0:
                    del stable_counter[lbl]

        # Keep only stable detections
        stable_detections = [d for d in frame_dets if stable_counter[d["label"]] >= STABLE_FRAMES]

        # TTS interval
        if current_time - last_tts_time >= TTS_INTERVAL:
            description, meta = build_scene_description_and_meta(stable_detections, frame_w, frame_area)
            if description != last_description:
                print("[VISIONAR SAYS:]", description)
                speak_async(description)
                last_description = description

            # push to history buffer (one entry per spoken interval)
            history_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "description": description,
                "detections": meta,  # list of detection dicts
                "frame_w": frame_w,
                "frame_h": frame_h,
                "fps_est": round(fps, 2)
            }
            history.append(history_entry)

            last_tts_time = current_time

        # Draw
        frame_disp = result.plot()
        cv2.putText(frame_disp, f"FPS: {int(fps)}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Visual Assistance", frame_disp)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # CLEAN EXIT
    cap.release()
    cv2.destroyAllWindows()

    # Export history on exit
    export_history_jsonl()  # saves to current folder with timestamped filename

    # stop TTS thread
    tts_queue.put(None)
    tts_thread.join()
    print("Done.")
