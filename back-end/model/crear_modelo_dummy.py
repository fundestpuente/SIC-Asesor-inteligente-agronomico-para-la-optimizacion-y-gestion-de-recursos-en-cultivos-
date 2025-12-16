import tensorflow as tf
from tensorflow.keras import layers, models
import os

# 1. Detectar dónde estamos (estamos en back-end/model)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Definir ruta (Directamente aquí, SIN crear subcarpeta 'model')
SAVE_PATH = os.path.join(BASE_DIR, "mi_modelo.h5")

# 3. Crear modelo
print("Creando modelo de prueba...")
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),
    layers.GlobalAveragePooling2D(),
    layers.Dense(3, activation='softmax')
])
model.compile(optimizer='adam', loss='categorical_crossentropy')

# 4. Guardar
model.save(SAVE_PATH, save_format='h5')
print(f"✅ LISTO: Modelo guardado en: {SAVE_PATH}")