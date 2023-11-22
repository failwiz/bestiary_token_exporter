"""A pdf image parser.

Usage:
    python3 pdf_image_exporter.py /path/to/pdf_file.pdf
Exports images from a pdf file to a directory. Duplicates are discarded.
"""

import asyncio
from datetime import datetime
import io
import logging
import sys
from pathlib import Path

import imagehash
from PIL import Image
from pypdf import PdfReader


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)


class ExportedImageFile:
    """Image, exported from pdf file."""

    def __init__(self, image_data: bytes, name: str) -> None:
        self.name = name + '.webp'
        image = Image.open(io.BytesIO(image_data))
        bounds = image.getbbox()
        self.image = image.crop(bounds)
        logger.debug(f'Found image: {self.name}')

    async def async_init(self):
        return self

    @property
    def hash(self):
        return str(imagehash.average_hash(self.image))

    def __await__(self):
        return self.async_init().__await__()

    def __str__(self) -> str:
        return f'{self.name}'

    def save_image(self, path: Path) -> None:
        """Save image to a file."""

        self.image.save(
            str(path) + '/' + self.name
        )
        logger.debug(f'Image saved: {self.name}')


def blocking_get_image(pdf_file: Path):
    """Extract images from pdf file."""

    count: int = 0
    reader: PdfReader = PdfReader(pdf_file)
    for page in reader.pages:
        for image in page.images:
            count += 1
            yield ExportedImageFile(image.data, str(count))
    logger.debug(f'Found {count-1} images')


async def save_images(pdf_file, save_dir):
    """Save extracted images to folder."""

    hashes = set()
    coro = asyncio.to_thread(
        blocking_get_image,
        pdf_file
    )
    saving_tasks = set()
    for image in await asyncio.create_task(coro):
        if image.hash not in hashes:
            save_coro = asyncio.to_thread(image.save_image, save_dir)
            saving_tasks.add(asyncio.create_task(save_coro))
            hashes.add(image.hash)
        else:
            logger.debug(f'{image.name} is a duplicate')
    await asyncio.gather(*saving_tasks)


async def main():
    """Main function."""

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    )

    try:
        pdf_file = Path(sys.argv[1])
    except IndexError:
        print('No pdf file!')
        print(__doc__)
        sys.exit()

    save_dir = Path(str(pdf_file.parent / pdf_file.stem) + '_export')
    print('Saving images in', save_dir)
    try:
        save_dir.mkdir(exist_ok=True)
    except FileNotFoundError:
        print('Can\'t create dir', save_dir)
        sys.exit()

    await save_images(pdf_file, save_dir)

if __name__ == '__main__':
    start = datetime.now()
    asyncio.run(main())
    duration = datetime.now() - start
    print(f'Took time: {duration.total_seconds():.2f} seconds.')
