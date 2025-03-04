from paddlex import create_pipeline
import os

# Create output directory if it doesn't exist
output_dir = "output/IMG_5059/"
os.makedirs(output_dir, exist_ok=True)

pipeline = create_pipeline(pipeline="table_recognition")

output = pipeline.predict(
    input="inputs/IMG_5059.png",
    # Removing the unsupported parameters
    # use_doc_orientation_classify=False,
    # use_doc_unwarping=False,
)

for res in output:
    res.save_to_img(output_dir)

print(f"Results saved to {output_dir}")