#After debugging, you’ll have a pipeline that only uses the steps that actually help.

import cv2
import numpy as np

def final_preprocess(img_path):
    image = cv2.imread(img_path)
    # Step 1: Deskew
    image = deskew_image(image)

    # Step 2: Possibly skip dewarp if not needed
    # image = dewarp_image(image, min_area_ratio=0.4)

    # Step 3: Light contrast enhancement
    image = clahe_enhance(image)

    # Step 4: Mild gamma if needed
    image = gamma_correction(image, gamma=1.1)
    return image

#Then call it from your main code
from image_preprocess import final_preprocess

processed_img = final_preprocess("my_image.jpg")
# Pass processed_img to OCR, etc.


