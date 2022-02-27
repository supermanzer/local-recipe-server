"""
    services/image_ocr.py
    
    Define functions to extract text from images using OCR.
"""
from logging import getLogger

logger = getLogger(__name__)


def load_images_return_text(image_paths: list) -> str:
    """
        Load images from a list of image paths.
    """
    text_list = build_text_list(image_paths)

    full_text = compile_text(text_list)

    return full_text


def build_text_list(image_paths: list) -> list:
    """
        Build a list of text snippets from a list of image paths.
    """
    text_list = []
    for image_path in image_paths:
        text = extract_text_from_image(image_path)
        text_list.append(text)
    return text_list


def compile_text(text_list):
    """
        Compile text from a list of text snippets.
    """
    return '\n'.join(text_list)


def extract_text_from_image(image_path):
    """
        Extract text from an image using OCR.
    """
    logger.info('Extracting text from image: {}'.format(image_path))

    return 'This is a test.'
