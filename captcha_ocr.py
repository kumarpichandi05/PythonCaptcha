import os
import cv2
import numpy as np
import json
from paddleocr import PaddleOCR
import tempfile

def log(message):
    print(f"[LOG] {message}")  # Blue Prism console logging

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

def get_image_files(folder_path, extensions):
    return [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in extensions]

def read_image(image_path):
    if not os.path.exists(image_path):
        log(f"File not found: {image_path}")
        return None
    image = cv2.imread(image_path)
    if image is None:
        log(f"OpenCV failed to read: {image_path}")
    return image

def remove_isolated_pixels(binary_image):
    h, w = binary_image.shape
    cleaned_image = binary_image.copy()
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            neighborhood = binary_image[i-1:i+2, j-1:j+2]
            if binary_image[i, j] == 255 and np.sum(neighborhood) <= 255:
                cleaned_image[i, j] = 0
    return cleaned_image

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised_1 = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=4, searchWindowSize=21)
    denoised_2 = cv2.fastNlMeansDenoising(denoised_1, None, 31, 12, 21)
    denoised_3 = cv2.fastNlMeansDenoising(denoised_2, h=10, templateWindowSize=6, searchWindowSize=21)
    _, binary = cv2.threshold(denoised_3, 128, 255, cv2.THRESH_BINARY_INV)
    cleaned = remove_isolated_pixels(binary)
    kernel = np.ones((3, 3), np.uint8)
    closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
    return closed

def save_temp_image(image, suffix=".png"):
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    cv2.imwrite(temp_file.name, image)
    return temp_file.name  # For logging/debug if needed

def extract_text(image_array, ocr_model):
    try:
        result = ocr_model.ocr(image_array, det=False)
        if result and result[0] and result[0][0]:
            return result[0][0][0].replace(" ", "")
        return "no_text_detected"
    except Exception as e:
        log(f"OCR failed: {e}")
        return "ocr_error"

def save_to_json(data, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        #log(f"OCR text saved to: {filename}")
    except Exception as e:
        log(f"Failed to save JSON: {e}")

def main():
    ocr = PaddleOCR()
    script_dir = get_script_directory()
    folder_path = os.path.join(script_dir, "Inp_images")
    image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

    if not os.path.exists(folder_path):
        log(f"Image folder not found: {folder_path}")
        return

    image_files = get_image_files(folder_path, image_extensions)

    if not image_files:
        log("No image files found.")
        return

    for image_file in image_files:
        try:
            image_path = os.path.join(folder_path, image_file)
            log(f"Processing image: {image_path}")
            image = read_image(image_path)
            if image is None:
                continue

            processed_image = preprocess_image(image)
            text = extract_text(processed_image, ocr)

            log(f"Extracted Text: {text}")
            json_filename = os.path.join(script_dir, f"{text}.json")
            save_to_json(text, json_filename)

        except Exception as e:
            log(f"Error processing {image_file}: {e}")

if __name__ == "__main__":
    main()
