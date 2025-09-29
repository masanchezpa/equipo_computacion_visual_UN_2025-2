import pyttsx3

# Inicializar el motor de TTS
engine = pyttsx3.init()

print("Probando la salida de audio...")

# Texto que se convertirá a voz
text_to_say = "La prueba de Texto a Voz funciona. The text to speech test works."

# Pasar el texto al motor
engine.say(text_to_say)

# Procesar y reproducir el audio.
engine.runAndWait()

print("Prueba de audio finalizada.")