import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

# --- IMPORTACIONES PROPIAS ---
# Asegúrate de que estos archivos existan y funcionen
from weather_api import get_weather 
from fertilizer_recommendation import recommend_fertilizer
# Importamos la función de predicción de imagen que creamos antes
from model.plant_classifier import predict_disease 

# Inicializar la aplicación FastAPI
app = FastAPI(title="AgroMind API", description="API para recomendación de fertilizantes y detección de enfermedades")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False, 
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# ==========================================
# 1. CARGA ROBUSTA DE MODELOS (FERTILIZANTES)
# ==========================================
print("--- Iniciando Carga de Modelos ---")

# Detectar la carpeta donde está ESTE archivo api.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Definir la ruta a la carpeta 'model'
MODEL_DIR = os.path.join(BASE_DIR, "model")

try:
    # Construir rutas absolutas para evitar errores de "File not found"
    path_preprocessor = os.path.join(MODEL_DIR, "preprocessor_X.joblib")
    path_scaler = os.path.join(MODEL_DIR, "scaler_y.joblib")
    path_categories = os.path.join(MODEL_DIR, "categories.joblib")
    path_keras_model = os.path.join(MODEL_DIR, "agromind_best.keras")

    print(f"Cargando preprocesadores desde: {MODEL_DIR}")
    
    preprocessor_X = joblib.load(path_preprocessor)
    scaler_y = joblib.load(path_scaler)
    categories = joblib.load(path_categories)

    # Cargar modelo Keras
    model_fert = tf.keras.models.load_model(
        path_keras_model,
        custom_objects={'r2_keras': lambda y, p: y} 
    )
    print("✅ ¡Modelos de FERTILIZANTES cargados correctamente!")
except Exception as e:
    print(f"❌ Error CRÍTICO cargando modelos de fertilizantes: {e}")
    # No detenemos la app, pero las predicciones de fertilizantes fallarán
    model_fert = None

# ==========================================
# 2. CONFIGURACIÓN AUXILIAR
# ==========================================

CROP_TRANSLATION = {
    "cafe": "coffee", "arroz": "rice", "maiz": "maize", 
    "banano": "banana", "platano": "banana", "manzana": "apple",
    "frijol": "kidneybeans", "frijoles": "kidneybeans",
    "papaya": "papaya", "sandia": "watermelon", "uvas": "grapes",
    "mango": "mango", "naranja": "orange", "limon": "orange",
    "algodon": "cotton", "coco": "coconut"
}

class PredictionRequest(BaseModel):
    crop: str
    ph: float
    latitud: float
    longitud: float

def prepare_input(crop, temperature, humidity, ph, rainfall):
    X_df = pd.DataFrame({
        "temperature": [temperature],
        "humidity": [humidity],
        "ph": [ph],
        "rainfall": [rainfall],
        "label": [crop]
    })
    return preprocessor_X.transform(X_df)

# ==========================================
# 3. ENDPOINT 1: RECOMENDACIÓN DE FERTILIZANTES
# ==========================================
@app.post("/predict")
def predict_fertilizer(request: PredictionRequest):
    if model_fert is None:
        raise HTTPException(status_code=500, detail="El modelo de fertilizantes no está cargado.")

    try:
        print(f"📡 Recibido Fertilizante: {request.crop}, pH={request.ph}")

        # A. Obtener clima
        weather_data = get_weather(request.latitud, request.longitud)
        if not weather_data:
             weather_data = {"temperature": 25.0, "humidity": 60.0, "rainfall": 50.0}
        
        # B. Traducir cultivo
        crop_input = request.crop.lower().strip()
        crop_model_name = CROP_TRANSLATION.get(crop_input, crop_input)

        # C. Preparar datos
        X = prepare_input(
            crop=crop_model_name,
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            ph=request.ph,
            rainfall=weather_data["rainfall"]
        )

        # D. Predecir
        y_scaled = model_fert.predict(X)
        y_pred = scaler_y.inverse_transform(y_scaled)[0]
        
        N_val, P_val, K_val = float(y_pred[0]), float(y_pred[1]), float(y_pred[2])

        # E. Respuesta
        recomendacion_texto = recommend_fertilizer(crop_model_name, N_val, P_val, K_val)

        return {
            "success": True,
            "nutrientes_requeridos": {"N": round(N_val, 2), "P": round(P_val, 2), "K": round(K_val, 2)},
            "datos_clima": weather_data,
            "recomendacion": recomendacion_texto
        }

    except Exception as e:
        print(f"Error en predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# ==========================================
# 4. ENDPOINT 2: DETECCIÓN DE ENFERMEDADES (NUEVO)
# ==========================================
@app.post("/predict-image")
async def predict_image_endpoint(file: UploadFile = File(...)):
    """
    Recibe una imagen desde el celular, la guarda temporalmente,
    la analiza con la IA y devuelve el resultado.
    """
    try:
        print(f" Recibiendo imagen: {file.filename}")
        
        # 1. Guardar la imagen temporalmente en el disco
        temp_filename = f"temp_{file.filename}"
        temp_path = os.path.join(BASE_DIR, temp_filename)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Llamar a tu función de IA (la que está en plant_classifier.py)
        #    Esta función carga el modelo .h5 y predice
        resultado = predict_disease(temp_path)
        
        # 3. Borrar la imagen temporal para no llenar el disco
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        # 4. Devolver respuesta JSON
        return {
            "success": True,
            "prediccion": resultado["class"],    # Ej: "Papa_Tizon"
            "confianza": resultado["confidence"] # Ej: "98.5%"
        }

    except Exception as e:
        print(f"❌ Error analizando imagen: {e}")
        return {"success": False, "error": str(e)}

# ==========================================
# 5. ARRANQUE
# ==========================================
if __name__ == "__main__":
    import uvicorn
    # Usamos host 0.0.0.0 para que sea accesible en la red local
    uvicorn.run(app, host="0.0.0.0", port=8000)