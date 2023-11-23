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

HASH_SIZE = 6

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)


def generator_get_image(pdf_file: Path):
    """Extract images from pdf file."""

    reader: PdfReader = PdfReader(pdf_file)
    for page in reader.pages:
        for count, image in enumerate(page.images):
            with Image.open(io.BytesIO(image.data)) as ex_image:
                filename = f'{str(page.page_number)}_{str(count)}.webp'
                yield ex_image, filename


async def save_images(pdf_file, save_dir):
    """Save extracted images to folder."""

    hashes = set()
    saving_tasks = []
    coro_get_image = asyncio.to_thread(generator_get_image, pdf_file)
    task_get_image = asyncio.create_task(coro_get_image)
    for image, filename in await task_get_image:
        im_hash = str(imagehash.average_hash(image, HASH_SIZE))
        if im_hash not in hashes:
            hashes.add(im_hash)
            save_coro = asyncio.to_thread(image.save, f'{save_dir}/{filename}')
            save_task = asyncio.create_task(save_coro)
            saving_tasks.append(save_task)
        else:
            logger.debug(f'{filename} is a duplicate')
    await asyncio.gather(*saving_tasks)
    logger.debug(f'Saved {len(saving_tasks)} images')


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
