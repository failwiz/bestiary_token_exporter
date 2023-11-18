"""A pdf image parser.

Usage:
    python3 pdf_image_exporter.py /path/to/pdf_file.pdf
Exports images from a pdf file to a directory. Duplicates are discarded.
"""
import asyncio
import io
import sys
from pathlib import Path
from typing import Optional

import imagehash
from PIL import Image
from pypdf import PdfReader


class ExportedImageFile:
    """Image, exported from pdf file."""

    def __init__(self, image_data: bytes, name: str) -> None:
        self.name = name
        image: Image.Image = Image.open(io.BytesIO(image_data))
        bounds: Optional[tuple[int, int, int, int]] = image.getbbox()
        self.image = image.crop(bounds)

    def get_hash(self) -> str:
        """Get the hash of the image."""
        return str(imagehash.average_hash(self.image))

    async def save_image(self, path: Path) -> None:
        """Save image to a file."""
        self.image.save(
            str(path) + '/' + self.name.split('.')[0] + '.webp'
        )


def extract_images(pdf_file: Path, save_dir: Path):
    """Extract images from pdf file."""
    hashes: set[str] = set()
    count: int = 0
    reader: PdfReader = PdfReader(pdf_file)
    for page_num, page in enumerate(reader.pages):
        for image_file_object in page.images:
            temp_name: str = (str(page_num) + '_' + str(count)
                              + image_file_object.name)
            temp_image = ExportedImageFile(image_file_object.data, temp_name)
            temp_hash = temp_image.get_hash()
            if temp_hash not in hashes:
                hashes.add(temp_hash)
                asyncio.run(temp_image.save_image(save_dir))
            count += 1
    print(f'Saved {len(hashes)} unique images.')


if __name__ == '__main__':
    """Main function."""

    try:
        pdf_file: Path = Path(sys.argv[1])
    except IndexError:
        print('No pdf file!')
        print(__doc__)
        sys.exit()

    save_dir: Path = Path(str(pdf_file.parent / pdf_file.stem) + '_export')
    print('Saving images in', save_dir)
    try:
        save_dir.mkdir(exist_ok=True)
    except FileNotFoundError:
        print('Can\'t create dir', save_dir)

    extract_images(pdf_file, save_dir)
