import os
import cv2
from paddleocr import PPStructure,draw_structure_result,save_structure_res

table_engine = PPStructure(show_log=True, image_orientation=False)

save_folder = 'output/paddle-ocr-detection'
img_path = 'inputs/IMG_5063.png'
img = cv2.imread(img_path)
result = table_engine(img)
print(result)
save_structure_res(result, save_folder,os.path.basename(img_path).split('.')[0])

for line in result:
    line.pop('img')
    print(line)

from PIL import Image

font_path = '/System/Library/Fonts/Times.ttc' # PaddleOCR下提供字体包
image = Image.open(img_path).convert('RGB')
im_show = draw_structure_result(image, result, font_path=font_path)
im_show = Image.fromarray(im_show)

# Save the result image in the same folder as other output files
base_name = os.path.basename(img_path).split('.')[0]
result_path = os.path.join(save_folder, base_name, 'result.jpg')
im_show.save(result_path)