import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# --- 1. CONFIGURACIÓN DE RUTAS ---
# Detectamos dónde está este archivo (back-end/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas exactas basadas en tu estructura
DATASET_DIR = os.path.join(BASE_DIR, "imagenes_entrenamiento")
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "model", "detector_de_imagen.h5")

# Configuración de imagen
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 5  # Entrenará 5 veces (tardará unos 3-5 mins)

# --- 2. CARGAR IMÁGENES ---
print(f"Buscando imágenes en: {DATASET_DIR}")

train_datagen = ImageDataGenerator(
    rescale=1./255,       # Normalizar colores
    validation_split=0.2  # 20% para validar
)

print("--- Cargando datos de ENTRENAMIENTO ---")
train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

print("--- Cargando datos de VALIDACIÓN ---")
validation_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# Guardar los nombres de las clases
class_names = list(train_generator.class_indices.keys())

# --- 3. CREAR EL CEREBRO (MobileNetV2) ---
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False # Congelamos el cerebro base

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.2)(x)
predictions = Dense(len(class_names), activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# --- 4. ENTRENAR ---
print("\nINICIANDO ENTRENAMIENTO... (Esto tomará unos minutos)")
model.fit(
    train_generator,
    epochs=EPOCHS,
    validation_data=validation_generator
)

# --- 5. GUARDAR ---
model.save(MODEL_SAVE_PATH)
print("\n" + "="*40)
print(f"¡LISTO! Modelo guardado en: {MODEL_SAVE_PATH}")
print("COPIA ESTA LISTA Y PÉGALA EN 'plant_classifier.py':")
print(f"CLASS_NAMES = {class_names}")
print("="*40)