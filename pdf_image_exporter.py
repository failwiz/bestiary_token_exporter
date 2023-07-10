'''
A pdf image parser.

Usage:
    python3 pdf_image_exporter.py /path/to/pdf_file.pdf
Exports images from a pdf file to a directory. Duplicates are discarded.
'''

import sys
import io
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import imagehash


class ExportedImageFile:
    """Image, exported from pdf file."""

    def __init__(self, image_data: Image.Image, name: str):
        self.name = name
        image = Image.open(io.BytesIO(image_data))
        bounds = image.getbbox()
        self.image = image.crop(bounds)

    def get_hash(self) -> str:
        """Get the hash of the image."""
        return imagehash.average_hash(self.image)

    def save_image(self):
        """Save image to a file."""
        self.image.save(self.name.split('.')[0] + '.png')


images = {}


def extract_images():
    """Extract images from"""
    count = 0
    reader = PdfReader("Pawns.pdf")
    for page_num, page in enumerate(reader.pages):
        for image_file_object in page.images:
            temp_name = (str(page_num) + '_' + str(count)
                         + image_file_object.name)
            temp = ExportedImageFile(image_file_object.data, temp_name)
            images[temp.get_hash()] = temp
            count += 1
    print(len(images))
    for image in images.values():
        image.save_image()


extract_images()
