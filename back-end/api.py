import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from weather_api import get_weather 
from fertilizer_recommendation import recommend_fertilizer

# Inicializar la aplicación FastAPI
app = FastAPI(title="AgroMind API", description="API para recomendación de fertilizantes")

# --- 1. CARGA DE MODELOS (Se ejecuta al iniciar) ---
print("Cargando cerebro de la IA...")
try:
    preprocessor_X = joblib.load("model/preprocessor_X.joblib")
    scaler_y = joblib.load("model/scaler_y.joblib")
    categories = joblib.load("model/categories.joblib")

    # Cargar modelo Keras con la función dummy para r2_keras
    model = tf.keras.models.load_model(
        "model/agromind_best.keras",
        custom_objects={'r2_keras': lambda y, p: y} 
    )
    print("Sistema listo para recibir peticiones.")
except Exception as e:
    print(f"Error cargando los modelos: {e}")

# --- 2. DICCIONARIO DE TRADUCCIÓN (App Español -> IA Inglés) ---
CROP_TRANSLATION = {
    "cafe": "coffee", 
    "arroz": "rice", 
    "maiz": "maize", 
    "banano": "banana", 
    "platano": "banana", 
    "manzana": "apple",
    "frijol": "kidneybeans", 
    "frijoles": "kidneybeans",
    "papaya": "papaya",
    "sandia": "watermelon",
    "uvas": "grapes",
    "mango": "mango",
    "naranja": "orange",
    "limon": "orange",
    "algodon": "cotton",
    "coco": "coconut"
}

# --- 3. FORMATO EXACTO DEL JSON DE TU COMPAÑERO ---
class PredictionRequest(BaseModel):
    crop: str
    ph: float
    latitud: float
    longitud: float

# --- 4. FUNCIÓN AUXILIAR ---
def prepare_input(crop, temperature, humidity, ph, rainfall):
    X_df = pd.DataFrame({
        "temperature": [temperature],
        "humidity": [humidity],
        "ph": [ph],
        "rainfall": [rainfall],
        "label": [crop]
    })
    return preprocessor_X.transform(X_df)

# --- 5. EL ENDPOINT PRINCIPAL ---
@app.post("/predict")
def predict_fertilizer(request: PredictionRequest):
    try:
        print(f"Recibido: Cultivo={request.crop}, pH={request.ph}")
        print(f"Ubicacion: Lat {request.latitud}, Lon {request.longitud}")

        # A. Obtener datos del clima usando Lat/Lon
        weather_data = get_weather(request.latitud, request.longitud)
        
        # Validación de seguridad por si el clima falla
        if not weather_data:
             weather_data = {"temperature": 25.0, "humidity": 60.0, "rainfall": 50.0}
        
        print(f"Clima obtenido: {weather_data}")

        # B. Traducir el nombre del cultivo
        crop_input = request.crop.lower().strip()
        # Busca en el diccionario, si no encuentra, usa la palabra original
        crop_model_name = CROP_TRANSLATION.get(crop_input, crop_input)

        # C. Preparar los datos para la IA
        X = prepare_input(
            crop=crop_model_name,
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            ph=request.ph,
            rainfall=weather_data["rainfall"]
        )

        # D. Predicción (Cerebro)
        y_scaled = model.predict(X)
        y_pred = scaler_y.inverse_transform(y_scaled)[0]
        
        N_val, P_val, K_val = float(y_pred[0]), float(y_pred[1]), float(y_pred[2])

        # E. Generar recomendación de texto (Fórmula 15-15-15)
        recomendacion_texto = recommend_fertilizer(crop_model_name, N_val, P_val, K_val)

        # F. Enviar respuesta JSON limpia
        return {
            "success": True,
            "nutrientes_requeridos": {
                "N": round(N_val, 2),
                "P": round(P_val, 2),
                "K": round(K_val, 2)
            },
            "datos_clima": weather_data,
            "recomendacion": recomendacion_texto
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        # Enviar error 500 pero con detalles
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

# --- BLOQUE PARA EJECUTAR CON 'python api.py' ---
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" permite que tu compañero se conecte por Wi-Fi
    uvicorn.run(app, host="0.0.0.0", port=8000)