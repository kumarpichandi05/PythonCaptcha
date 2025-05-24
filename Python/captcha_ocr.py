import cv2
import os
import numpy as np
from IPython.display import Image, display
import tempfile
import json
from paddleocr import PaddleOCR

ocr = PaddleOCR()

folder_path = "Inp_images/"
image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
image_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]

for image_file in image_files:
    try:
        # Attempt to read the image
        image = cv2.imread("Inp_images/" + image_file)
        if image is None:
            print(f"Error: Unable to read image {image_file}. Skipping...")
            continue

        # Display original image
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, image)
        display(Image(filename=temp_file.name))

        # Step 2: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, gray)
        display(Image(filename=temp_file.name))

        # Apply fastNlMeansDenoising
        denoised_Stage1 = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=4, searchWindowSize=21)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, denoised_Stage1)
        display(Image(filename=temp_file.name))

        # Denoising Stage 2
        denoised_Stage2 = cv2.fastNlMeansDenoising(denoised_Stage1, None, 31, 12, 21)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, denoised_Stage2)
        display(Image(filename=temp_file.name))

        # Denoising Stage 3
        denoised_Stage3 = cv2.fastNlMeansDenoising(denoised_Stage2, h=10, templateWindowSize=6, searchWindowSize=21)

        # Step 3: Apply binary thresholding
        _, binary = cv2.threshold(denoised_Stage3, 128, 255, cv2.THRESH_BINARY_INV)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, binary)
        display(Image(filename=temp_file.name))

        # Custom function to remove isolated pixels
        def remove_isolated_pixels(binary_image):
            h, w = binary_image.shape
            cleaned_image = binary_image.copy()
            for i in range(1, h - 1):
                for j in range(1, w - 1):
                    neighborhood = binary_image[i-1:i+2, j-1:j+2]
                    if binary_image[i, j] == 255 and np.sum(neighborhood) <= 255:
                        cleaned_image[i, j] = 0
            return cleaned_image

        # Apply to binary image
        cleaned_image = remove_isolated_pixels(binary)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, cleaned_image)
        display(Image(filename=temp_file.name))

        # Apply morphological closing
        kernel = np.ones((3, 3), np.uint8)
        cleaned_image1 = cv2.morphologyEx(cleaned_image, cv2.MORPH_CLOSE, kernel)
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        cv2.imwrite(temp_file.name, cleaned_image1)
        display(Image(filename=temp_file.name))

        # Step 4: Perform OCR to extract text from the processed image
        try:
            results = ocr.ocr(cleaned_image1, det=False)
            if results and results[0] and results[0][0]:
                cleaned_text = results[0][0][0].replace(' ', '')
            else:
                cleaned_text = "no_text_detected"
        except Exception as e:
            print(f"Error during OCR processing for {image_file}: {e}")
            continue

        # Print and save OCR results
        print(f"Extracted text: {cleaned_text}")
        
        try:
            # Save the extracted text data to a JSON file
            file_name = f"{cleaned_text}.json"
            with open(file_name, 'w') as json_file:
                json.dump(cleaned_text, json_file, indent=4)
            print(f"OCR text results have been saved to '{file_name}'")
        except Exception as e:
            print(f"Error saving OCR results for {image_file}: {e}")
    
    except Exception as e:
        print(f"An error occurred while processing {image_file}: {e}")
