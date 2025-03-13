import cv2
import numpy as np

def find_multiple_cards_and_crop(image_path, output_dir=None):
    # 1) Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read {image_path}")
        return []

    # 2) Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    # 3) Edge detection
    edges = cv2.Canny(gray, 30, 200)

    # 4) Morphological close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # 5) Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = img.shape[:2]
    img_area = w * h

    # 6) Sort contours by area descending (so we see biggest first if we want)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Instead of keeping only the "best_crop," let's keep *all* valid crops
    all_crops = []
    debug_img = img.copy()

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        # Adjust threshold
        if area < 0.05 * img_area:
            continue

        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)  # 0.04 * peri

        # If we have 4 corners, it might be a table/card
        if len(approx) == 4:
            # Draw contour for debugging
            cv2.drawContours(debug_img, [approx], -1, (0, 255, 0), 3)

            # Reorder corners
            pts = approx.reshape((4,2))
            rect = order_points(pts)

            # (Optional) Check aspect ratio if you only want certain shapes
            width = max(np.linalg.norm(rect[0] - rect[1]),
                        np.linalg.norm(rect[2] - rect[3]))
            height = max(np.linalg.norm(rect[0] - rect[3]),
                         np.linalg.norm(rect[1] - rect[2]))
            aspect_ratio = width / height

            # If this ratio check is too strict, remove or relax it
            if 0.3 <= aspect_ratio <= 2.0:
                cropped = four_point_transform(img, rect)
                all_crops.append(cropped)

                # Optionally save each crop to a folder
                if output_dir:
                    outpath = f"{output_dir}/crop_{i}.jpg"
                    cv2.imwrite(outpath, cropped)
                    print(f"Saved: {outpath}")

    # Debug image: see all 4-corner contours drawn
    cv2.imwrite("debug_contours.jpg", debug_img)

    return all_crops  # return a list of all cropped rectangles

def order_points(pts):
    """Order rectangle corners: [top-left, top-right, bottom-right, bottom-left]."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left
    rect[2] = pts[np.argmax(s)]   # bottom-right
    rect[1] = pts[np.argmin(diff)]# top-right
    rect[3] = pts[np.argmax(diff)]# bottom-left
    return rect

def four_point_transform(image, rect):
    """Warp the image to get a top-down view."""
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

# Example usage:
all_tables = find_multiple_cards_and_crop("inputs/IMG_5056.png", output_dir="output")
print(f"Found {len(all_tables)} rectangular tables.")
