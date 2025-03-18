import torch
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os

from transformers import AutoImageProcessor
from transformers.models.detr import DetrForSegmentation

# Load your image here
image_path = "inputs/IMG_5056.png"
img = Image.open(image_path)  # Load the image

# Convert image to RGB format to ensure compatibility
img = img.convert('RGB')

img_proc = AutoImageProcessor.from_pretrained(
    "cmarkea/detr-layout-detection"
)
model = DetrForSegmentation.from_pretrained(
    "cmarkea/detr-layout-detection"
)

with torch.inference_mode():
    input_ids = img_proc(img, return_tensors='pt')
    output = model(**input_ids)

threshold = 0.4

segmentation_mask = img_proc.post_process_segmentation(
    output,
    threshold=threshold,
    target_sizes=[img.size[::-1]]
)

bbox_pred = img_proc.post_process_object_detection(
    output,
    threshold=threshold,
    target_sizes=[img.size[::-1]]
)

# Function to visualize results
def visualize_results(image, segmentation_mask, bbox_pred, save_path=None):
    # Reduce figure size from 15,15 to 8,8
    plt.figure(figsize=(8, 8))
    
    # Convert image to numpy array
    image_np = np.array(image)
    
    # Display the image
    plt.imshow(image_np)
    
    # Plot segmentation mask
    if len(segmentation_mask) > 0:
        mask = segmentation_mask[0]['masks']  # Get the masks from the dictionary
        if len(mask) > 0:  # Check if there are any masks
            mask_array = mask[0].squeeze().numpy()  # Convert first mask tensor to numpy
            plt.imshow(mask_array, alpha=0.5)  # Overlay the mask
    
    # Plot bounding boxes
    for box in bbox_pred[0]['boxes']:
        x1, y1, x2, y2 = box.tolist()
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                        edgecolor='red', facecolor='none', linewidth=2))
    
    plt.axis('off')
    plt.title("Detected Tables and Segmentation Masks", fontsize=10)
    plt.tight_layout()
    
    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Visualization saved to {save_path}")
    else:
        plt.show()

# Create output path
output_dir = "output/detr-layout-detection"
os.makedirs(output_dir, exist_ok=True)

# Get the filename without extension
image_filename = os.path.basename(image_path)
image_name = os.path.splitext(image_filename)[0]
output_path = os.path.join(output_dir, f"{image_name}_detection.png")

# Call the visualization function with save path
visualize_results(img, segmentation_mask, bbox_pred, save_path=output_path)