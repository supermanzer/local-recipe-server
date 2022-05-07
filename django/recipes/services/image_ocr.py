"""
    services/image_ocr.py
    
    Define functions to extract text from images using OCR.
"""
from PIL import Image
import pytesseract

from logging import getLogger

logger = getLogger(__name__)


def load_images_return_text(files: list) -> str:
    """
        Load images from a list of image paths.
    """
    text_list = build_text_list(files)
    logger.info('Text list: {}'.format(text_list))
    # full_text = compile_text(text_list)

    # return full_text


def build_text_list(files: list) -> list:
    """
        Build a list of text snippets from a list of image paths.
    """
    text_list = []

    for file in files:
        text = extract_text_from_image(file)
        text_list.append(text)
    return text_list


def compile_text(text_list):
    """
        Compile text from a list of text snippets.
    """
    return '\n'.join(text_list)


def extract_text_from_image(file):
    """
        Extract text from an image using OCR.
    """
    # logger.info('Extracting text from image: {}'.format(image_path))

    image = Image.open(file)
    return pytesseract.image_to_string(image)
