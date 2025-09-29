from ultralytics import YOLO

# Cargar el modelo YOLOv8n pre-entrenado
model = YOLO('yolov8n.pt')

# Realizar la detección de objetos
results = model('test_image.jpg')

# Guardar la imagen con las cajas de detección dibujadas
# El resultado se guardará en una carpeta llamada 'runs/detect/predict/'
results[0].save(filename='result_image.jpg')

print("Detección completada. Revisar el Archivo 'result_image.jpg'.")