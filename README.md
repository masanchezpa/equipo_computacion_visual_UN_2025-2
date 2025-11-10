# Proyecto Computación Visual

## Entrega 1

### Ingeniería de Sistemas y Computación  

**Nombres:**  
- Laura Daniela Agudelo Cruz  
- Jesus David Giraldo Gomez  
- María Camila Sánchez Páez 
- John Andres Rua Cortes 

**Universidad Nacional de Colombia**  
Facultad de Ingeniería  
Departamento de Ingeniería de Sistemas e Industrial  
Computación Visual  
Profesora  
Bogotá, D.C.  Colombia  
2025 - 2S  

---

## Equipo
El equipo está conformado por:  
- Laura Daniela Agudelo Cruz  
- Jesus David Giraldo Gomez  
- María Camila Sánchez Páez  
- John Andres Rua Cortes

---

## Definición
Este proyecto consiste en el desarrollo de un prototipo de asistente visual auditivo que utilizará una cámara conectada a un dispositivo de procesamiento (**Jetson Nano**) para capturar video en tiempo real, procesarlo con un modelo de detección de objetos y anunciar en voz alta los nombres de los objetos identificados en el entorno.  

El objetivo principal es proporcionar a las personas con discapacidad visual una mayor conciencia de su entorno inmediato, mejorando su independencia y seguridad.  

### Alcance
- Implementación de un modelo de detección de objetos entrenado con el dataset **COCO** (80 categorías, más de 1.5M instancias).  
- Integración de una fuente de video en vivo con **OpenCV**.  
- Incorporación de una librería de Texto a Voz (TTS), como **pyttsx3** o **gTTS**.  
- Lógica de anuncio inteligente para evitar repeticiones y priorizar objetos nuevos o importantes.  
- Interfaz mínima que muestre el video (para desarrollo y depuración), pero con funcionamiento principalmente auditivo.  

### Límites
- Es un prototipo, no un dispositivo médico certificado.  
- La efectividad depende de la cámara, iluminación y oclusiones.  
- Solo reconoce las ~80 clases del dataset COCO.  
- Se desarrollará en una plataforma específica, no como app móvil completa.  

---

## Justificación
Este proyecto es una demostración integral de un sistema de **computación visual de ciclo completo**:  
- Adquisición de datos (video en vivo).  
- Procesamiento (detección de objetos).  
- Salida en modalidad diferente (audio).  

### Desafíos clave
- **Inferencia en tiempo real:** mantener altos FPS.  
- **Procesamiento de flujo de video:** manejar datos continuos.  
- **Interacción Humano-Computadora (HCI):** comunicación eficaz con el usuario.  

El aprendizaje incluye dominar técnicas avanzadas como la detección de objetos, la integración de visión, audio y procesamiento en tiempo real, además de un diseño centrado en la **empatía y accesibilidad**.  

A nivel social, responde a un desafío humanitario: según la OMS, cientos de millones de personas tienen discapacidad visual. Este tipo de tecnología aporta a los ODS 3 (Bienestar) y ODS 10 (Reducción de desigualdades).  

---

## Cronograma

### Semana 1
- Finalizar este documento y asignar tareas.  
- Configurar entorno de desarrollo.  
- Descargar modelo pre-entrenado.  

### Semana 2
- Detectar objetos en una imagen estática.  
- Script para capturar video de webcam.  
- Script de prueba TTS ("Hola Mundo").  

### Semana 3
- Integrar detección en tiempo real.  
- Medir FPS.  
- Conectar detector con TTS (primer prototipo).  

### Semana 4
- Analizar problemas (ej. repetición de anuncios).  
- Lógica de enfriamiento (anunciar cada 5s).  

### Semana 5
- Lógica de anuncio solo para objetos nuevos.  
- Probar en distintos entornos.  
- Redactar documentación técnica.  

### Semana 6
- Añadir priorización de anuncios.  
- Usar confianza >70%.  
- Pruebas de usabilidad.  

### Semana 7
- Optimizar FPS y reducir latencia.  
- Interfaz gráfica simple (Start/Stop).  
- Refinar lógica con feedback.  

### Semana 8
- Congelar funcionalidades.  
- Pruebas exhaustivas en distintos escenarios.  
- Documentar resultados.  

### Semana 9
- Grabar video demostrativo.  
- Preparar diapositivas.  
- Escribir resultados y conclusiones.  

### Semana 10
- Pulir código y limpiar repositorio.  
- Finalizar informe.  
- Ensayo presentación final.  

### Semana 11
- Recibir feedback.  
- Ajustes finales.  
- Preparar paquete de entrega.  

### Semana 12
- Ensayo general de la presentación.  
- Verificar entregables.  

### Semana 13
- Presentación final y demo en vivo.  
- Entrega del material completo.  

---

## Uso

### Interfaz Gráfica

El proyecto incluye una interfaz gráfica completa desarrollada con **tkinter** que permite controlar todas las funcionalidades del asistente visual auditivo.

#### Ejecutar la Interfaz Gráfica

**Opción 1: Usando el script de ayuda (Recomendado)**

En Windows, puedes usar el script batch:
```bash
run_gui.bat
```

O el script PowerShell:
```bash
.\run_gui.ps1
```

**Opción 2: Usando directamente el Python del entorno virtual**

Si tienes problemas con la política de ejecución de PowerShell, usa directamente:
```bash
.venv\Scripts\python.exe gui_app.py
```

**Opción 3: Activando el entorno virtual primero**

Si prefieres activar el entorno virtual primero, puedes cambiar la política de ejecución de PowerShell temporalmente:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.venv\Scripts\Activate.ps1
python gui_app.py
```

O usar el método alternativo sin cambiar la política:
```bash
.venv\Scripts\python.exe gui_app.py
```

#### Características de la Interfaz

- **Panel de Video en Tiempo Real**: Muestra el video de la cámara con las detecciones de objetos dibujadas
- **Controles de Detección**:
  - Botón Iniciar/Detener para controlar la detección
  - Configuración de confianza mínima (0.1 a 1.0)
  - Tiempo de enfriamiento entre anuncios (1 a 15 segundos)
- **Configuración de Voz (TTS)**:
  - Velocidad de voz ajustable (50 a 300 palabras por minuto)
  - Volumen ajustable (0.0 a 1.0)
- **Panel de Información**:
  - FPS en tiempo real
  - Lista de objetos detectados con timestamps
  - Botón para limpiar la lista de detecciones

#### Funcionalidades Implementadas

- ✅ Detección de objetos en tiempo real con YOLOv8
- ✅ Anuncio de voz solo para objetos nuevos (evita repeticiones)
- ✅ Sistema de enfriamiento configurable entre anuncios
- ✅ Filtro de confianza mínima configurable
- ✅ Visualización de FPS y rendimiento
- ✅ Historial de objetos detectados
- ✅ Interfaz responsive y fácil de usar

### Script Original (Línea de Comandos)

Para usar el script original sin interfaz gráfica:

```bash
python main_prototype.py
```

Presiona 'q' para salir.

---

## Referencias
- **Repositorio del equipo:**  
  [GitHub - equipo_computacion_visual_UN_2025-2](https://github.com/masanchezpa/equipo_computacion_visual_UN_2025-2.git)  

- **Detección de Objetos y Datasets:**  
  - [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)  
  - [Microsoft COCO Dataset](https://cocodataset.org/)  

- **Librerías:**  
  - [OpenCV](https://docs.opencv.org/)  
  - [pyttsx3](https://pyttsx3.readthedocs.io/)  
  - [gTTS](https://gtts.readthedocs.io/)  
