import os
import json
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk


def show_points_with_image(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    current_file_index = 0

    # Инициализация переменных
    image = None
    image_tk = None
    current_point = [0, 0]
    image_width = 1
    image_height = 1
    x_offset = 0
    y_offset = 0
    shape = {"points": []}
    point_index = 0

    def load_next_file():
        nonlocal current_file_index
        if current_file_index < len(json_files):
            display_file(json_files[current_file_index])
            current_file_index += 1
        else:
            print("All files processed.")
            root.quit()

    def adjust_point(dx, dy):
        nonlocal current_point, shape, point_index
        x, y = current_point
        x += dx
        y += dy
        x = max(0, min(x, image_width))
        y = max(0, min(y, image_height))
        shape['points'][point_index] = [x, y]
        draw_point(x, y)

    def draw_point(x, y):
        canvas.delete("all")
        canvas.create_image(-x_offset, -y_offset, image=image_tk)
        canvas.create_oval(
            x - 5 - x_offset, y - 5 - y_offset,
            x + 5 - x_offset, y + 5 - y_offset,
            fill="red"
        )

    def display_file(json_file):
        nonlocal image, image_tk, current_point, image_width, image_height, x_offset, y_offset, shape, point_index

        # Загрузка JSON файла
        json_path = os.path.join(folder_path, json_file)
        print(f"Processing: {json_path}")
        with open(json_path, 'r') as file:
            data = json.load(file)

        # Путь к изображению
        image_path = os.path.join(folder_path, data['imagePath'])
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            load_next_file()
            return

        # Загрузка изображения
        try:
            original_image = Image.open(image_path)
        except Exception as e:
            print(f"Error loading image: {e}")
            load_next_file()
            return

        image_width, image_height = original_image.size
        print(f"Image size: {image_width}x{image_height}")

        # Обработка первой точки
        for shape in data['shapes']:
            for i, point in enumerate(shape['points']):
                current_point = point
                point_index = i
                x, y = point
                x_offset = max(0, x - 250)
                y_offset = max(0, y - 250)
                cropped_image = original_image.crop((
                    x_offset, y_offset,
                    min(x_offset + 500, image_width),
                    min(y_offset + 500, image_height)
                ))
                image_tk = ImageTk.PhotoImage(cropped_image)

                draw_point(x, y)
                return  # Обрабатываем одну точку за раз

        # Сохраняем изменённый JSON
        output_path = os.path.join(output_folder, json_file)
        with open(output_path, 'w') as output_file:
            json.dump(data, output_file, indent=4)

        load_next_file()

    # Создание GUI
    root = tk.Tk()
    root.geometry("500x500")

    canvas = Canvas(root, width=500, height=500)
    canvas.pack()

    btn_frame = tk.Frame(root)
    btn_frame.pack()

    tk.Button(btn_frame, text="←", command=lambda: adjust_point(-1, 0)).grid(row=0, column=0)
    tk.Button(btn_frame, text="→", command=lambda: adjust_point(1, 0)).grid(row=0, column=2)
    tk.Button(btn_frame, text="↑", command=lambda: adjust_point(0, -1)).grid(row=0, column=1)
    tk.Button(btn_frame, text="↓", command=lambda: adjust_point(0, 1)).grid(row=1, column=1)
    tk.Button(btn_frame, text="Skip", command=load_next_file).grid(row=2, column=1)

    load_next_file()
    root.mainloop()

# Укажите папку с JSON и изображениями
input_folder = "/Users/antonshever/Desktop/dataset/frame-new"
output_folder = "/Users/antonshever/Desktop/dataset/frame-new-points"

show_points_with_image(input_folder, output_folder)
