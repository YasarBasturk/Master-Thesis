# Master-Thesis

## OCR Pipeline Overview

The pipeline consists of the following steps:

1. Apply preprocessing steps to the input images
2. Use the preprocessed images with an OCR model
3. Extract data from the resulting txt/JSON files

**Current Status:** All steps above have been implemented successfully.

### Future Work
- Document aligner
- Additional steps to be determined

## Implementation Details

The specific pipeline follows this workflow:
1. `image_preprocess.py` → 
2. `paddle_OCR_detection.py` → 
3. `res_0.txt` (output file containing extracted data)

## Related Scripts and Experiments

The following scripts were explored during development but are not part of the main pipeline:

- **Doc_Scanner_Static + utils**: Works but produces lower quality results. Could serve as an alternative preprocessing approach if needed.
- **microsoft_table_transformer**: Works well with structured PDF files but not with our image dataset. Tables need to be well-constructed with properly aligned data.
- **detr-layout-detection**: Effective with our images for detection, but lacks extraction capabilities.
- **crop_model1**: Detects and crops tables, which might be useful if zooming in on tables improves OCR accuracy.
- **paddle_X**: Based on an advanced version of `paddle_OCR_detection`, but provided no significant advantages over the current implementation.