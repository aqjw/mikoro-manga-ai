from app.predict import predict


# Функция для предсказания и отображения результата
def predict_and_show(image_path):
    # Передбачення маски
    segmented_mask = predict(image_path)

    # Збереження сегментованої маски
    segmented_mask.save("/Users/antonshever/Desktop/mask.png")


# Путь к вашему изображению
image_path = "/Users/antonshever/Desktop/12.png"
predict_and_show(image_path)
