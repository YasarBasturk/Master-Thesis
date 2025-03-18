# Master-Thesis

# OCR Pipeline:

# The pipeline is as follows: Apply preprocesing steps 
# --> use the preprocessed image with a OCR model 
# --> Use the extracted data which comes from a txt/JSON file after running the OCR model 
# -------------------------------- Above the line of work has been achieved so far
# Later on:
# --> Document aligner
# ... to be dediced 

# A more specific pipeline which follows the names of the scripts etc:
#image_preprocess --> paddle_OCR_detection --> res_0.txt (the created txt file from the extracted data)


# These scripts do not provide additional information to the OCR model but helped me to get to where I am now: 
# --> Doc_Scanner_Static + utlis script does work fine but the results are not in good quality. The Document scanner program is a good alternative to overcome the preprocessing steps if necessary.
# --> microsoft_table_transformer does not work well with the images I have, it works very good on pdf files etc, where the tables a constructed very well and its data inside is alligned well.
# --> detr-layout-detection does work well with the images I have, but there is not extraction element. I did'nt know how to use this model for my case, but led me to the next model etc.
# --> crop_model1 does crop any tables it detects, which can be used later (maybe), if I find out that cropping the image makes the OCR model work better because the tables and its data is zoomed in.
# --> I did have a paddle_X script which is actually based on the advanced version of the paddle_OCR_detection script, but did not provide any difference than the other scripts. It detects and that is it and therefore I did not use it.