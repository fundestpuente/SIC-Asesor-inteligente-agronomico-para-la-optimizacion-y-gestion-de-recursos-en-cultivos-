import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# 1. Configuración básica
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "detector_de_imagen.h5")

# --- LISTA ORIGINAL (NO LA TOQUES, debe coincidir con las carpetas) ---
CLASS_NAMES = ['Papa_Sana', 'Papa_Tizon', 'Pimiento_Bacteria', 'Pimiento_Sano', 'Tomate_Bacteria', 'Tomate_Sano']

# --- DICCIONARIO TRADUCTOR (¡AQUÍ CAMBIAS LOS NOMBRES!) ---
# A la izquierda: El nombre de la carpeta
# A la derecha: Lo que quieres que vea el usuario
NOMBRES_AMIGABLES = {
    "Papa_Sana": "Papa Saludable ",
    "Papa_Tizon": "Papa Enferma (Tizón) ",
    "Pimiento_Sano": "Pimiento Saludable",
    "Pimiento_Bacteria": "Pimiento Enfermo (Bacteriosis) ",
    "Tomate_Sano": "Tomate Saludable",
    "Tomate_Bacteria": "Tomate Enfermo (Bacteriosis) "
}

# 2. Cargar el modelo
print(f"Cargando modelo de visión desde: {MODEL_PATH}")
try:
    model = load_model(MODEL_PATH)
    print(" Modelo de visión cargado.")
except Exception as e:
    print(f" Error cargando modelo .h5: {e}")
    model = None

def predict_disease(image_path):
    if model is None:
        return {"class": "Error: Modelo no cargado", "confidence": "0%"}

    try:
        # Procesar imagen
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predecir
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions[0])
        confidence_score = np.max(predictions[0])

        # Obtener el nombre técnico
        nombre_tecnico = CLASS_NAMES[predicted_index]
        
        # TRADUCIR AL NOMBRE AMIGABLE
        # Si encuentra el nombre en el diccionario, lo usa. Si no, usa el técnico.
        nombre_final = NOMBRES_AMIGABLES.get(nombre_tecnico, nombre_tecnico)

        return {
            "class": nombre_final, 
            "confidence": f"{confidence_score * 100:.2f}%"
        }

    except Exception as e:
        print(f"Error prediciendo imagen: {e}")
        return {"class": "Error en predicción", "confidence": "0%"}