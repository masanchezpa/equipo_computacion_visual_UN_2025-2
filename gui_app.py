import cv2
import pyttsx3
from ultralytics import YOLO
import time
import threading
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import queue

class VisualAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Asistente Visual Auditivo - Computación Visual UN")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2b2b2b')
        
        # Variables de control
        self.is_running = False
        self.cap = None
        self.model = None
        self.tts_engine = None
        self.video_thread = None
        self.frame_queue = queue.Queue(maxsize=2)
        
        # Variables de configuración
        self.min_confidence = 0.7
        self.cooldown_time = 5.0  # segundos entre anuncios
        self.tts_rate = 150  # velocidad de voz
        self.tts_volume = 0.8  # volumen (0.0 a 1.0)
        
        # Variables de estado
        self.last_announcement_time = 0
        self.last_detected_objects = set()
        self.current_fps = 0
        self.detected_objects_list = []
        
        # Inicializar componentes
        self.setup_ui()
        self.load_model()
        
    def setup_ui(self):
        # Frame principal
        main_frame = Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Video
        video_frame = Frame(main_frame, bg='#1e1e1e', relief=RAISED, bd=2)
        video_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        video_label = Label(video_frame, text="Video en Tiempo Real", 
                           bg='#1e1e1e', fg='white', font=('Arial', 14, 'bold'))
        video_label.pack(pady=10)
        
        self.video_canvas = Canvas(video_frame, bg='#000000', width=640, height=480)
        self.video_canvas.pack(padx=10, pady=10)
        
        # Panel derecho - Controles
        control_frame = Frame(main_frame, bg='#2b2b2b', width=350)
        control_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        control_frame.pack_propagate(False)
        
        # Título
        title_label = Label(control_frame, text="Controles", 
                           bg='#2b2b2b', fg='white', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Botón Start/Stop
        self.start_stop_btn = Button(control_frame, text="Iniciar Detección", 
                                     command=self.toggle_detection,
                                     bg='#4CAF50', fg='white', 
                                     font=('Arial', 12, 'bold'),
                                     relief=RAISED, bd=3, padx=20, pady=10)
        self.start_stop_btn.pack(pady=15)
        
        # Separador
        separator1 = ttk.Separator(control_frame, orient=HORIZONTAL)
        separator1.pack(fill=X, pady=10)
        
        # Configuración de Confianza
        confidence_frame = LabelFrame(control_frame, text="Confianza Mínima", 
                                     bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        confidence_frame.pack(fill=X, padx=10, pady=5)
        
        self.confidence_var = DoubleVar(value=self.min_confidence)
        confidence_scale = Scale(confidence_frame, from_=0.1, to=1.0, 
                                resolution=0.05, orient=HORIZONTAL,
                                variable=self.confidence_var,
                                command=self.update_confidence,
                                bg='#2b2b2b', fg='white', 
                                troughcolor='#404040', highlightthickness=0)
        confidence_scale.pack(padx=10, pady=5)
        
        self.confidence_label = Label(confidence_frame, 
                                     text=f"Valor: {self.min_confidence:.2f}",
                                     bg='#2b2b2b', fg='#4CAF50', font=('Arial', 9))
        self.confidence_label.pack(pady=5)
        
        # Configuración de TTS
        tts_frame = LabelFrame(control_frame, text="Configuración de Voz", 
                              bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        tts_frame.pack(fill=X, padx=10, pady=5)
        
        # Velocidad de voz
        speed_label = Label(tts_frame, text="Velocidad:", 
                           bg='#2b2b2b', fg='white', font=('Arial', 9))
        speed_label.pack(anchor=W, padx=10, pady=(5, 0))
        
        self.speed_var = IntVar(value=self.tts_rate)
        speed_scale = Scale(tts_frame, from_=50, to=300, 
                           resolution=10, orient=HORIZONTAL,
                           variable=self.speed_var,
                           command=self.update_tts_speed,
                           bg='#2b2b2b', fg='white', 
                           troughcolor='#404040', highlightthickness=0)
        speed_scale.pack(padx=10, pady=5, fill=X)
        
        # Volumen
        volume_label = Label(tts_frame, text="Volumen:", 
                            bg='#2b2b2b', fg='white', font=('Arial', 9))
        volume_label.pack(anchor=W, padx=10, pady=(5, 0))
        
        self.volume_var = DoubleVar(value=self.tts_volume)
        volume_scale = Scale(tts_frame, from_=0.0, to=1.0, 
                            resolution=0.1, orient=HORIZONTAL,
                            variable=self.volume_var,
                            command=self.update_tts_volume,
                            bg='#2b2b2b', fg='white', 
                            troughcolor='#404040', highlightthickness=0)
        volume_scale.pack(padx=10, pady=5, fill=X)
        
        # Tiempo de Enfriamiento
        cooldown_frame = LabelFrame(control_frame, text="Tiempo de Enfriamiento (seg)", 
                                   bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        cooldown_frame.pack(fill=X, padx=10, pady=5)
        
        self.cooldown_var = DoubleVar(value=self.cooldown_time)
        cooldown_scale = Scale(cooldown_frame, from_=1.0, to=15.0, 
                              resolution=0.5, orient=HORIZONTAL,
                              variable=self.cooldown_var,
                              command=self.update_cooldown,
                              bg='#2b2b2b', fg='white', 
                              troughcolor='#404040', highlightthickness=0)
        cooldown_scale.pack(padx=10, pady=5)
        
        # Separador
        separator2 = ttk.Separator(control_frame, orient=HORIZONTAL)
        separator2.pack(fill=X, pady=10)
        
        # Información de FPS
        fps_frame = LabelFrame(control_frame, text="Rendimiento", 
                              bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        fps_frame.pack(fill=X, padx=10, pady=5)
        
        self.fps_label = Label(fps_frame, text="FPS: 0", 
                              bg='#2b2b2b', fg='#4CAF50', font=('Arial', 12, 'bold'))
        self.fps_label.pack(pady=10)
        
        # Objetos Detectados
        detected_frame = LabelFrame(control_frame, text="Objetos Detectados", 
                                   bg='#2b2b2b', fg='white', font=('Arial', 10, 'bold'))
        detected_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar para la lista
        scrollbar = Scrollbar(detected_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.detected_listbox = Listbox(detected_frame, 
                                        bg='#1e1e1e', fg='white',
                                        font=('Arial', 9),
                                        yscrollcommand=scrollbar.set,
                                        height=8)
        self.detected_listbox.pack(fill=BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.detected_listbox.yview)
        
        # Botón para limpiar lista
        clear_btn = Button(control_frame, text="Limpiar Lista", 
                          command=self.clear_detected_list,
                          bg='#f44336', fg='white', 
                          font=('Arial', 9),
                          relief=RAISED, bd=2, padx=10, pady=5)
        clear_btn.pack(pady=5)
        
    def load_model(self):
        """Cargar el modelo YOLO"""
        try:
            status_label = Label(self.root, text="Cargando modelo YOLOv8...", 
                               bg='#2b2b2b', fg='yellow', font=('Arial', 10))
            status_label.pack()
            self.root.update()
            
            self.model = YOLO('yolov8n.pt')
            
            status_label.destroy()
            status_label = Label(self.root, text="Modelo cargado correctamente", 
                               bg='#2b2b2b', fg='#4CAF50', font=('Arial', 10))
            status_label.pack()
            self.root.after(2000, status_label.destroy)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el modelo: {str(e)}")
            
    def update_confidence(self, value):
        """Actualizar valor de confianza mínima"""
        self.min_confidence = float(value)
        self.confidence_label.config(text=f"Valor: {self.min_confidence:.2f}")
        
    def update_tts_speed(self, value):
        """Actualizar velocidad de TTS"""
        self.tts_rate = int(value)
        if self.tts_engine:
            self.tts_engine.setProperty('rate', self.tts_rate)
            
    def update_tts_volume(self, value):
        """Actualizar volumen de TTS"""
        self.tts_volume = float(value)
        if self.tts_engine:
            self.tts_engine.setProperty('volume', self.tts_volume)
            
    def update_cooldown(self, value):
        """Actualizar tiempo de enfriamiento"""
        self.cooldown_time = float(value)
        
    def clear_detected_list(self):
        """Limpiar la lista de objetos detectados"""
        self.detected_listbox.delete(0, END)
        self.detected_objects_list.clear()
        
    def toggle_detection(self):
        """Iniciar o detener la detección"""
        if not self.is_running:
            self.start_detection()
        else:
            self.stop_detection()
            
    def start_detection(self):
        """Iniciar la detección de objetos"""
        if not self.model:
            messagebox.showerror("Error", "El modelo no está cargado")
            return
            
        # Inicializar TTS
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', self.tts_rate)
            self.tts_engine.setProperty('volume', self.tts_volume)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo inicializar TTS: {str(e)}")
            return
            
        # Inicializar cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo abrir la cámara")
            return
            
        self.is_running = True
        self.start_stop_btn.config(text="Detener Detección", bg='#f44336')
        self.last_announcement_time = 0
        self.last_detected_objects = set()
        
        # Iniciar hilo de video
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        
        # Iniciar actualización de UI
        self.update_video_display()
        
    def stop_detection(self):
        """Detener la detección de objetos"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        if self.tts_engine:
            self.tts_engine.stop()
            
        self.start_stop_btn.config(text="Iniciar Detección", bg='#4CAF50')
        
        # Limpiar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_text(320, 240, text="Detección detenida", 
                                     fill='white', font=('Arial', 16))
        
    def video_loop(self):
        """Bucle principal de procesamiento de video (en hilo separado)"""
        prev_time = time.time()
        
        while self.is_running:
            if not self.cap:
                break
                
            success, frame = self.cap.read()
            if not success:
                break
                
            # Calcular FPS
            current_time = time.time()
            if (current_time - prev_time) > 0:
                self.current_fps = 1 / (current_time - prev_time)
            prev_time = current_time
            
            # Detección de objetos
            results = self.model(frame, verbose=False, conf=self.min_confidence)
            result = results[0]
            
            # Procesar detecciones
            detected_objects = set()
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                if confidence >= self.min_confidence:
                    object_name = self.model.names[class_id]
                    detected_objects.add(object_name)
            
            # Anunciar objetos nuevos
            new_objects = detected_objects - self.last_detected_objects
            current_time_announce = time.time()
            
            if new_objects and (current_time_announce - self.last_announcement_time) >= self.cooldown_time:
                self.announce_objects(new_objects)
                self.last_announcement_time = current_time_announce
                self.last_detected_objects = detected_objects.copy()
                
                # Actualizar lista de objetos detectados
                for obj in new_objects:
                    timestamp = time.strftime("%H:%M:%S")
                    self.detected_objects_list.append(f"[{timestamp}] {obj}")
                    if len(self.detected_objects_list) > 50:  # Limitar a 50 elementos
                        self.detected_objects_list.pop(0)
            
            # Dibujar resultados en el frame
            frame_with_boxes = result.plot()
            cv2.putText(frame_with_boxes, f'FPS: {int(self.current_fps)}', 
                       (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame_with_boxes, f'Conf: {self.min_confidence:.2f}', 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Convertir frame a formato para tkinter
            frame_rgb = cv2.cvtColor(frame_with_boxes, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            # Redimensionar si es necesario
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                frame_pil = frame_pil.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            frame_tk = ImageTk.PhotoImage(image=frame_pil)
            
            # Enviar frame a la cola
            try:
                self.frame_queue.put_nowait((frame_tk, detected_objects))
            except queue.Full:
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put_nowait((frame_tk, detected_objects))
                except queue.Empty:
                    pass
                    
            time.sleep(0.01)  # Pequeña pausa para no saturar
            
    def announce_objects(self, objects):
        """Anunciar objetos por voz"""
        if not self.tts_engine or not objects:
            return
            
        # Crear mensaje en español
        objects_list = list(objects)
        if len(objects_list) == 1:
            announcement = f"Veo un {objects_list[0]}"
        else:
            announcement = "Veo " + ", ".join(objects_list[:-1]) + f" y {objects_list[-1]}"
        
        # Anunciar en hilo separado para no bloquear
        def speak():
            try:
                self.tts_engine.say(announcement)
                self.tts_engine.runAndWait()
            except:
                pass
                
        threading.Thread(target=speak, daemon=True).start()
        
    def update_video_display(self):
        """Actualizar la visualización del video en la UI"""
        if not self.is_running:
            return
            
        # Obtener frame de la cola
        try:
            frame_tk, detected_objects = self.frame_queue.get_nowait()
            
            # Actualizar canvas
            self.video_canvas.delete("all")
            self.video_canvas.create_image(0, 0, anchor=NW, image=frame_tk)
            self.video_canvas.image = frame_tk  # Mantener referencia
            
            # Actualizar FPS
            self.fps_label.config(text=f"FPS: {int(self.current_fps)}")
            
            # Actualizar lista de objetos detectados
            if self.detected_objects_list:
                self.detected_listbox.delete(0, END)
                for item in self.detected_objects_list[-10:]:  # Mostrar últimos 10
                    self.detected_listbox.insert(END, item)
                self.detected_listbox.see(END)
                
        except queue.Empty:
            pass
            
        # Programar próxima actualización
        self.root.after(30, self.update_video_display)
        
    def on_closing(self):
        """Manejar cierre de la ventana"""
        self.stop_detection()
        self.root.destroy()

def main():
    root = Tk()
    app = VisualAssistantGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()

