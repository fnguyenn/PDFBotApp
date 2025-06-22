# ocr_utils.py
# Handles OCR processing using Tesseract and image extraction from PDFs

from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import os
import shutil

# Extract text from an image using Tesseract OCR
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)            # opens image file using PIL
        return pytesseract.image_to_string(image) # passes the image to Tesseract and returns the detected text as a string
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from image {image_path}: {e}")

# Extract images from each page of a PDF and save them
def extract_images_from_pdf(pdf_path, output_folder="temp_images"):
    image_paths = []                            # a list to store the paths of the saved image files
    try:
        os.makedirs(output_folder, exist_ok=True)
        doc = fitz.open(pdf_path)                   # opens the PDF document using Fitz
        # for each page in the pdf, render each page as a pixmap
        # and saves the rendered page to the folder
        for page_index in range(len(doc)):
            page = doc.load_page(page_index)
            pix = page.get_pixmap()
            image_path = os.path.join(output_folder, f"page_{page_index}.png")
            pix.save(image_path)
            image_paths.append(image_path)
        return image_paths                          # returns list of image paths of all pages of pdf
    except Exception as e:
        raise RuntimeError(f"Failed to extract images from PDF: {e}")

# Apply OCR to a scanned PDF by converting pages to images
def extract_text_from_pdf(pdf_path):
    output_folder = "temp_images"
    try:
        # calls function above to extract images from the PDF and stores the returned image paths
        images = extract_images_from_pdf(pdf_path, output_folder=output_folder)
        # loops through the image paths, extracts text from each image, and joins all the text together with newline characters
        text = "\n".join([extract_text_from_image(img) for img in images])

        return text     # returns the final OCR-extracted text from the entire PDF
    except Exception as e:
        raise RuntimeError(f"OCR failed for PDF {pdf_path}: {e}")
    finally:
        try:
            shutil.rmtree(output_folder, ignore_errors=True)    # clean up temporary images folder
        except Exception:
            pass