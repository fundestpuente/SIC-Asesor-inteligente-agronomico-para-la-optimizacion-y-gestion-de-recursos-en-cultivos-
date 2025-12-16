import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

# --- CONFIGURACIÓN ---
IMG_SIZE = (224, 224)
# Ajusta estos nombres a lo que realmente quieras detectar
CLASS_NAMES = ['Saludable', 'Enfermedad_A', 'Enfermedad_B']

# --- CARGA DEL MODELO ---
# Usamos rutas relativas para que no falle en Windows
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "mi_modelo.h5")

print(f"Buscando modelo en: {MODEL_PATH}")
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("¡Modelo cargado exitosamente!")
    else:
        print(" Error: No encuentro el archivo .h5")
except Exception as e:
    print(f"Error fatal cargando el modelo: {e}")

def predict_disease(image_bytes):
    if model is None:
        return {"error": "El modelo no está cargado en el servidor."}

    try:
        # Procesar imagen
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image = image.resize(IMG_SIZE)
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0

        # Predecir
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0])) # Convertir a float nativo
        
        return {
            "diagnostico": CLASS_NAMES[predicted_index],
            "confianza": round(confidence * 100, 2),
            "mensaje": f"Detectado: {CLASS_NAMES[predicted_index]}"
        }
    except Exception as e:
        return {"error": f"Error procesando imagen: {str(e)}"}