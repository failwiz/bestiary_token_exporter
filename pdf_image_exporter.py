"""A pdf image parser.

Usage:
    python3 pdf_image_exporter.py /path/to/pdf_file.pdf
Exports images from a pdf file to a directory. Duplicates are discarded.
"""

import io
import sys
from pathlib import Path

import imagehash
from PIL import Image
from pypdf import PdfReader


class ExportedImageFile:
    """Image, exported from pdf file."""

    def __init__(self, image_data: Image.Image, name: str) -> None:
        self.name = name
        image: Image.Image = Image.open(io.BytesIO(image_data))
        bounds: tuple(int, int, int, int) = image.getbbox()
        self.image = image.crop(bounds)

    def get_hash(self) -> str:
        """Get the hash of the image."""
        return imagehash.average_hash(self.image)

    def save_image(self, path: Path) -> None:
        """Save image to a file."""
        self.image.save(str(path) + '/' + self.name.split('.')[0] + '.png')


def extract_images(pdf_file: Path) -> dict[str: ExportedImageFile]:
    """Extract images from pdf file."""
    images: dict[str: ExportedImageFile] = {}
    count: int = 0
    reader: PdfReader = PdfReader(pdf_file)
    for page_num, page in enumerate(reader.pages):
        for image_file_object in page.images:
            temp_name: str = (str(page_num) + '_' + str(count)
                              + image_file_object.name)
            temp = ExportedImageFile(image_file_object.data, temp_name)
            images[temp.get_hash()] = temp
            count += 1
    return images


def main():
    """Main function."""
    try:
        pdf_file: Path = Path(sys.argv[1])
    except IndexError:
        print('No pdf file!')
        print(__doc__)
        sys.exit()
    # directory for images, 'pdf file name' + _export
    save_dir: Path = Path(str(pdf_file.parent / pdf_file.stem) + '_export')
    print('Saving images in', save_dir)
    try:
        save_dir.mkdir(exist_ok=True)
    except FileNotFoundError:
        print('Can\'t create dir', save_dir)

    exported_images: dict[str: ExportedImageFile] = extract_images(pdf_file)

    for image in exported_images.values():
        image.save_image(save_dir)
    print(f'Saved {len(exported_images)} unique images.')


main()
