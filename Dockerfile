# Dockerfile

# 1. Используем базовый образ Python
FROM python:3.10

# 2. Устанавливаем рабочую директорию
WORKDIR /workspace

# 3. Устанавливаем системные зависимости для OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# 4. Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем код приложения в контейнер
COPY . .

# 6. Открываем порт, на котором работает Flask
EXPOSE 5310

# 7. Запускаем приложение
CMD ["python", "app.py"]
