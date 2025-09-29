import cv2
import pyttsx3
from ultralytics import YOLO
import time

# Cargar el modelo YOLO
print("Cargando modelo YOLOv8...")
model = YOLO('yolov8n.pt')
print("Modelo cargado.")

# Inicializar el motor de Texto a Voz (TTS)
print("Inicializando motor de TTS...")
tts_engine = pyttsx3.init()
print("Motor de TTS inicializado.")

# Iniciar la captura de video
print("Iniciando captura de video...")
window_name = "Asistencia Visual Auditiva"
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

cv2.namedWindow(window_name)

# Variables para cálculo de FPS
prev_time = 0
fps = 0
frame_count = 0

print("Presiona 'q' o cierra la ventana para salir.")

while True:
    success, frame = cap.read()
    if not success:
        break

    frame_count += 1

    # Medición de FPS
    current_time = time.time()
    if (current_time - prev_time) > 0:
        fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Detección de Objetos
    results = model(frame, verbose=False)
    result = results[0]

    # Anuncio de Voz
    detected_objects_names = set()
    for box in result.boxes:
        class_id = int(box.cls[0])
        object_name = model.names[class_id]
        detected_objects_names.add(object_name)

    if detected_objects_names:
        announcement = "I see a " + ", ".join(detected_objects_names)
        print(announcement)
        tts_engine.say(announcement)
        tts_engine.runAndWait()

    # Visualización
    frame_with_boxes = result.plot()
    cv2.putText(frame_with_boxes, f'FPS: {int(fps)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow(window_name, frame_with_boxes)

    # Lógica de salida
    try:
        if cv2.waitKey(1) & 0xFF == ord('q') or (frame_count > 1 and cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1):
            break
    except cv2.error:
        break

# Limpieza
print("Cerrando aplicación...")
cap.release()
cv2.destroyAllWindows()
print("Recursos liberados.")