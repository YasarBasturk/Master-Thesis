import os
import cv2
from paddleocr import PPStructure,save_structure_res

table_engine = PPStructure(layout=False, show_log=True)

save_folder = './output'
img_path = 'inputs/IMG_4985_sc.png'
img = cv2.imread(img_path)
result = table_engine(img)
save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

# Create a copy of the image for visualization
vis_img = img.copy()

# Draw boxes for each detected element
for line in result:
    box = line['bbox']
    # Convert box coordinates to integers
    box = [int(x) for x in box]
    # Draw rectangle around detected area
    cv2.rectangle(vis_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
    
    line.pop('img')
    print(line)

# Display the image with detected areas
cv2.imshow('Detected Tables', vis_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optionally save the visualization
cv2.imwrite(os.path.join(save_folder, 'visualization.jpg'), vis_img)