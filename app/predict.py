import numpy as np
from PIL import Image
import cv2
from utils import resize_image, normalize, cvtColor
from model import INPUT_SHAPE

# Dictionary for class labels
label_dict = {
    "background": 0,
    "bubble": 1
}

model = None  # Placeholder for the model

# Color mapping for different labels (only two labels here, so simplified)
colors = [(0, 0, 0), (255, 255, 255)]  # Black for background, white for bubble


def image_predictions(image, ori_size):
    ori_h, ori_w = ori_size

    # Resize and normalize the image
    image_data, nw, nh = resize_image(image, (INPUT_SHAPE[1], INPUT_SHAPE[0]))
    image_data = normalize(np.array(image_data, np.float32))
    image_data = np.expand_dims(image_data, 0)

    # Get predictions from the model
    pr = model.predict(image_data)[0]

    # Resize prediction to original image size
    pr = pr[int((INPUT_SHAPE[0] - nh) // 2): int((INPUT_SHAPE[0] - nh) // 2 + nh),
            int((INPUT_SHAPE[1] - nw) // 2): int((INPUT_SHAPE[1] - nw) // 2 + nw)]
    pr = cv2.resize(pr, (ori_w, ori_h), interpolation=cv2.INTER_LINEAR)

    # Take the index with the highest probability as the class prediction
    pr = pr.argmax(axis=-1)

    return pr


def filter_by_label(pr, label_name):
    # Validate label name
    if label_name not in label_dict:
        raise ValueError(f"Label '{label_name}' not recognized. Available labels: {list(label_dict.keys())}")

    # Filter mask for the specified label
    target_label_index = label_dict[label_name]
    target_mask = (pr == target_label_index)

    return target_mask


def predict_mask(img):
    img = cvtColor(img)  # Convert image to RGB if needed

    # Get original image dimensions
    ori_h, ori_w = img.size[1], img.size[0]

    # Get prediction mask for the image
    pr = image_predictions(img, (ori_h, ori_w))

    # Label to isolate in prediction (only "bubble" class here)
    label_name = 'bubble'

    # Apply filter to get only the target mask
    target_mask = filter_by_label(pr, label_name)

    # Create color image array for the mask
    seg_img = np.full((ori_h, ori_w, 3), colors[0], dtype=np.uint8)
    seg_img[target_mask] = colors[1]  # White for the "bubble" label

    # Convert to Image object
    return Image.fromarray(seg_img)


def train_predict(_model, image_path):
    global model
    model = _model

    # Open image and predict mask
    image = Image.open(image_path)
    return predict_mask(image)
