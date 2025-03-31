import os
import cv2
import argparse
import traceback
import json
import numpy as np

# Add a custom JSON encoder to handle numpy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super(NumpyEncoder, self).default(obj)

# Try different import paths for PaddleOCR
try:
    from paddleocr import PPStructure, draw_structure_result, save_structure_res
    print("Successfully imported PPStructure from paddleocr")
except ImportError:
    try:
        # Alternative import path
        from paddleocr import PaddleOCR as PPStructure
        from paddleocr import draw_ocr as draw_structure_result
        
        # Create a compatibility function for save_structure_res
        def save_structure_res(result, save_folder, image_name):
            os.makedirs(os.path.join(save_folder, image_name), exist_ok=True)
            with open(os.path.join(save_folder, image_name, 'res_0.json'), 'w', encoding='utf-8') as f:
                import json
                json.dump({'res': result}, f, ensure_ascii=False, indent=4)
            print(f"Results saved to {os.path.join(save_folder, image_name, 'res_0.json')}")
        
        print("Using PaddleOCR with compatibility layer instead of PPStructure")
    except ImportError as e:
        print(f"Failed to import PaddleOCR modules: {e}")
        raise

from PIL import Image

# Helper function to sanitize OCR results for JSON serialization
def sanitize_for_json(obj):
    """
    Recursively convert PaddleOCR objects to JSON-serializable types.
    Handles numpy arrays, complex objects, and removes non-serializable fields.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        # Create a new dict without non-serializable items
        sanitized = {}
        for key, value in obj.items():
            # Skip specific problematic fields
            if key in ['img', 'image', '_PlaceholderType']:
                continue
            try:
                # Test if the value is JSON serializable
                json.dumps({key: value})
                sanitized[key] = value
            except (TypeError, OverflowError):
                # If not serializable, try to convert it
                sanitized[key] = sanitize_for_json(value)
        return sanitized
    else:
        # For other types, convert to string representation
        try:
            return str(obj)
        except:
            return "UNSERIALIZABLE_OBJECT"

# Custom save function to ensure consistent file structure
def enhanced_save_structure_res(result, save_folder, image_name):
    """Save OCR results to multiple paths for redundancy"""
    # Make sure the output directories exist
    os.makedirs(save_folder, exist_ok=True)
    os.makedirs(os.path.join(save_folder, image_name), exist_ok=True)
    
    # Sanitize the result for JSON serialization
    sanitized_result = sanitize_for_json(result)
    
    # Save to the standard PaddleOCR path
    standard_path = os.path.join(save_folder, image_name, 'res_0.json')
    with open(standard_path, 'w', encoding='utf-8') as f:
        json.dump({'res': sanitized_result}, f, ensure_ascii=False, indent=4)
    print(f"Results saved to {standard_path}")
    
    # Save to an alternative path directly in the output folder
    alt_path = os.path.join(save_folder, 'res_0.json')
    with open(alt_path, 'w', encoding='utf-8') as f:
        json.dump({'res': sanitized_result}, f, ensure_ascii=False, indent=4)
    print(f"Results also saved to {alt_path}")
    
    # Save with the image name prefix for easier identification
    prefixed_path = os.path.join(save_folder, f"{image_name}_res_0.json")
    with open(prefixed_path, 'w', encoding='utf-8') as f:
        json.dump({'res': sanitized_result}, f, ensure_ascii=False, indent=4)
    print(f"Results also saved to {prefixed_path}")
    
    return standard_path

# Function to run OCR with input and output parameters
def run_paddle_ocr(image_path, output_folder):
    """Run PaddleOCR on an image and save results to the specified folder."""
    # Make sure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Initialize the OCR engine
        print("Initializing OCR engine...")
        table_engine = PPStructure(show_log=True, image_orientation=False)
        print("OCR engine initialized successfully")
        
        # Read the image
        print(f"Reading image from {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image from {image_path}")
        print(f"Image loaded successfully: shape={img.shape}")
        
        # Run OCR
        print("Running OCR processing...")
        result = table_engine(img)
        print(f"OCR processing completed for {image_path}")
        
        # Sanitize the results to ensure they are JSON serializable
        sanitized_result = sanitize_for_json(result)
        
        # Process results - extract the text elements from the structure
        processed_results = []
        
        # Log some results
        print(f"Found {len(sanitized_result)} text regions")
        for i, line in enumerate(sanitized_result):
            print(f"Text region {i}: {line}")
            
            # Extract text entries from the "res" field if it exists
            if 'res' in line:
                # These are the actual text entries
                for item in line['res']:
                    # Ensure each item has a text value
                    if 'text' not in item or item['text'] is None:
                        item['text'] = ""
                    # Add the item to processed results
                    processed_results.append(item)
        
        # Save results using our enhanced save function
        base_name = os.path.basename(image_path).split('.')[0]
        print(f"Saving results to {output_folder} with base name {base_name}")
        try:
            enhanced_save_structure_res(sanitized_result, output_folder, base_name)
        except Exception as e:
            print(f"Error saving OCR results to JSON: {e}")
            # We'll continue even if saving fails, as we'll return the results directly
        
        # Create a visualization
        print("Creating visualization...")
        font_path = '/System/Library/Fonts/Times.ttc'  # Adjust for your system
        if not os.path.exists(font_path):
            # Try alternate font path
            font_path = None
            print("Default font not found, using system default")
            
        image = Image.open(image_path).convert('RGB')
        im_show = draw_structure_result(image, result, font_path=font_path)
        im_show = Image.fromarray(im_show)
        
        # Save the visualization
        os.makedirs(os.path.join(output_folder, base_name), exist_ok=True)
        result_path = os.path.join(output_folder, base_name, 'result.jpg')
        im_show.save(result_path)
        print(f"OCR results and visualization saved to {output_folder}")
        
        # Return the processed OCR results
        if processed_results:
            print(f"Returning {len(processed_results)} extracted text entries")
            return processed_results
        else:
            # If no text entries were extracted, return the original results
            print("No text entries extracted, returning original sanitized results")
            return sanitized_result
    except Exception as e:
        print(f"Error in run_paddle_ocr: {e}")
        traceback.print_exc()
        raise

# Keep the original code
if __name__ == "__main__":
    # Check if arguments are provided
    if len(os.sys.argv) > 1:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Run PaddleOCR on an image.')
        parser.add_argument('--image', type=str, help='Path to input image')
        parser.add_argument('--output', type=str, help='Path to save OCR results')
        
        args = parser.parse_args()
        
        # If both image and output are provided, run OCR
        if args.image and args.output:
            run_paddle_ocr(args.image, args.output)
        else:
            print("Both --image and --output arguments are required.")
    else:
        # Original code
        save_folder = 'output/paddle-ocr-detection'
        img_path = 'inputs/IMG_5069_template.png'
        img = cv2.imread(img_path)
        
        # Initialize the OCR engine
        table_engine = PPStructure(show_log=True, image_orientation=False)
        
        # Run OCR
        result = table_engine(img)
        print(result)
        # Use our enhanced save function instead of the standard one
        enhanced_save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])

        for line in result:
            if 'img' in line:
                line.pop('img')
            print(line)

        # Create a visualization
        font_path = '/System/Library/Fonts/Times.ttc'
        image = Image.open(img_path).convert('RGB')
        im_show = draw_structure_result(image, result, font_path=font_path)
        im_show = Image.fromarray(im_show)

        # Save the result image
        base_name = os.path.basename(img_path).split('.')[0]
        result_path = os.path.join(save_folder, base_name, 'result.jpg')
        im_show.save(result_path)