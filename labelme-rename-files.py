import os
import json


# def rename_json_and_image_files_in_directory(directory_path, start=1):
#     json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
#
#     # Sort files by creation time to ensure consistent renaming order
#     json_files.sort(key=lambda x: os.path.getctime(os.path.join(directory_path, x)))
#     for i, filename in enumerate(json_files, start=start):
#         old_json_path = os.path.join(directory_path, filename)
#         new_json_filename = f"{i}.json"
#         new_json_path = os.path.join(directory_path, new_json_filename)
#
#         # Rename the JSON file
#         os.rename(old_json_path, new_json_path)
#
#         # Update the internal content of the JSON
#         with open(new_json_path, 'r') as file:
#             data = json.load(file)
#
#         # Assuming the content should have an "imagePath" field updated
#         if 'imagePath' in data:
#             new_image_filename = f"{i}.png"  # or use the appropriate extension
#             data['imagePath'] = new_image_filename
#
#         with open(new_json_path, 'w') as file:
#             json.dump(data, file, indent=4)
#
#         # Rename the corresponding image file if it exists
#         old_image_path = os.path.join(directory_path, filename.replace('.json', '.png'))
#         if os.path.exists(old_image_path):
#             new_image_path = os.path.join(directory_path, new_image_filename)
#             os.rename(old_image_path, new_image_path)
#             print(
#                 f"Renamed {filename} to {new_json_filename} and {filename.replace('.json', '.png')} to {new_image_filename}")
#         else:
#             print(f"Renamed {filename} to {new_json_filename} (no corresponding image file found)")
#
#
# # Define the path to the directory containing your JSON and image files
# directory_path = 'datasets/train2'
# rename_json_and_image_files_in_directory(directory_path, start=149)


# from PIL import Image
# import os
#
# # Путь к папке с изображениями и разметкой
# folder_path = './train'
#
# # Проход по всем файлам в папке
# for filename in os.listdir(folder_path):
#     # Проверка на PNG файлы
#     if filename.endswith('.png'):
#         print(filename)
#         img_path = os.path.join(folder_path, filename)
#
#         # Открытие и сжатие изображения
#         with Image.open(img_path) as img:
#             img = img.convert("RGB")  # Перекодируем в RGB для оптимизации
#             compressed_img_path = os.path.join(folder_path, filename)
#             img.save(compressed_img_path, "JPEG", quality=85)  # Сохраняем с качеством
#
# print("Сжатие PNG файлов завершено.")
