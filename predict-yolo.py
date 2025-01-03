from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# Path to the image and the model
image_path = "/Users/antonshever/Desktop/008.jpg"
model_path = "/Users/antonshever/Desktop/yolo-seg-frame-best2.pt"

# Create output directory
output_dir = Path("/Users/antonshever/Desktop/output")
output_dir.mkdir(exist_ok=True)

m = YOLO(model_path)
res = m.predict(image_path)

# Iterate detection results
for r in res:
    img = np.copy(r.orig_img)
    img_name = Path(r.path).stem

    # Iterate each object contour
    for ci, c in enumerate(r):
        label = c.names[c.boxes.cls.tolist().pop()]

        b_mask = np.zeros(img.shape[:2], np.uint8)

        # Create contour mask
        contour = c.masks.xy.pop().astype(np.int32).reshape(-1, 1, 2)
        _ = cv2.drawContours(b_mask, [contour], -1, (255, 255, 255), cv2.FILLED)

        # Isolate object with transparent background (when saved as PNG)
        isolated = np.dstack([img, b_mask])

        # OPTIONAL: detection crop (from either OPT1 or OPT2)
        x1, y1, x2, y2 = c.boxes.xyxy.cpu().numpy().squeeze().astype(np.int32)
        iso_crop = isolated[y1:y2, x1:x2]

        # Save cropped result
        crop_filename = output_dir / f"{img_name}_{ci}.png"
        cv2.imwrite(str(crop_filename), iso_crop)
