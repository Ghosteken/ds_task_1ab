import os


class CNNService:
    def __init__(self, model_path: str = "models/product_cnn.h5"):
        self.model_path = model_path
        self.model = None
        if os.path.exists(self.model_path):
            try:
                from tensorflow.keras.models import load_model
                self.model = load_model(self.model_path)
            except Exception:
                self.model = None

    def build(self, input_shape=(128, 128, 3), num_classes: int = 2):
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
        model = Sequential()
        model.add(Conv2D(32, (3, 3), activation="relu", input_shape=input_shape))
        model.add(MaxPooling2D((2, 2)))
        model.add(Conv2D(64, (3, 3), activation="relu"))
        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        model.add(Dense(128, activation="relu"))
        model.add(Dropout(0.3))
        model.add(Dense(num_classes, activation="softmax"))
        model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
        self.model = model

    def train_from_dir(self, data_dir: str, epochs: int = 5, batch_size: int = 32):
        from tensorflow.keras.preprocessing.image import ImageDataGenerator
        train_gen = datagen.flow_from_directory(
            data_dir,
            target_size=(128, 128),
            batch_size=batch_size,
            class_mode="sparse",
            subset="training",
        )
        val_gen = datagen.flow_from_directory(
            data_dir,
            target_size=(128, 128),
            batch_size=batch_size,
            class_mode="sparse",
            subset="validation",
        )
        self.build(num_classes=len(train_gen.class_indices))
        self.model.fit(train_gen, validation_data=val_gen, epochs=epochs)
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        self.model.save(self.model_path)

    def predict_class(self, image_path: str) -> str:
        if self.model is None:
            return ""
        from tensorflow.keras.preprocessing.image import load_img, img_to_array
        import numpy as np
        img = load_img(image_path, target_size=(128, 128))
        arr = img_to_array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)
        preds = self.model.predict(arr)
        idx = int(np.argmax(preds, axis=1)[0])
        return str(idx)
