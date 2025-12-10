import joblib
import numpy as np
import tensorflow as tf
import pandas as pd

from weather_api import get_weather
from fertilizer_recommendation import recommend_fertilizer

# Cargar artefactos
preprocessor_X = joblib.load("model/preprocessor_X.joblib")
scaler_y = joblib.load("model/scaler_y.joblib")
categories = joblib.load("model/categories.joblib")

# Cargar modelo
model = tf.keras.models.load_model(
    "model/agromind_best.keras",
    custom_objects={'r2_keras': lambda y, p: y}  # Dummy para que cargue
)


def prepare_input(crop, temperature, humidity, ph, rainfall):
    X = np.array([[temperature, humidity, ph, rainfall, crop]])
    X_df = {
        "temperature": [temperature],
        "humidity": [humidity],
        "ph": [ph],
        "rainfall": [rainfall],
        "label": [crop]
    }
    X_processed = preprocessor_X.transform(pd.DataFrame(X_df))
    return X_processed


def run_system():
    city = input("Ciudad donde sembrarás: ")
    crop = input("Cultivo que deseas sembrar: ").lower()
    ph = float(input("pH del suelo: "))

    weather = get_weather(city)
    print("\nClima actual:")
    print(weather)

    X = prepare_input(
        crop=crop,
        temperature=weather["temperature"],
        humidity=weather["humidity"],
        ph=ph,
        rainfall=weather["rainfall"]
    )

    y_scaled = model.predict(X)
    y_pred = scaler_y.inverse_transform(y_scaled)[0]

    N, P, K = y_pred

    print("\nPredicción de Nutrientes Necesarios (kg/ha):")
    print(f"Nitrogeno (N): {N:.2f}")
    print(f"Fósforo (P): {P:.2f}")
    print(f"Potasio (K): {K:.2f}")

    print("\nRecomendación de Fertilizantes:")
    print(recommend_fertilizer(crop, N, P, K))


if __name__ == "__main__":
    run_system()
