import cv2

# Iniciar la captura de video desde la webcam
window_name = "Webcam"
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

print("Presiona 'q' o cierra la ventana para salir.")

# Bucle para leer frames de la cámara continuamente
while True:
    # Leer un frame
    success, frame = cap.read()
    if not success:
        print("No se pudo leer el frame. Saliendo...")
        break

    # Mostrar el frame en una ventana llamada "Webcam"
    cv2.imshow(window_name, frame)

    # Esperar por la tecla 'q' o se cierre la ventana para salir del bucle
    try:
        # Se intenta verificar el estado de la ventana y la tecla presionada
        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
    except cv2.error:
        # Si getWindowProperty falla (porque la ventana ya no existe),
        # se captura el error y simplemente se rompe el bucle.
        break

# Liberar la cámara y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()
print("Cámara liberada y ventanas cerradas.")