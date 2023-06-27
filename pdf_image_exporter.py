'''
A pdf image parser.
Usage:
python3 pdf_image_exporter.py /path/to/pdf_file.pdf
Exports images from a pdf file to a directory. Duplicates are discarded.
'''

import sys
from pathlib import Path
from pypdf import PdfReader
from PIL import Image
import imagehash

HASHES = set()

def make_hash(file):
    '''Hash using imagehash module.
    '''
    image_hash = imagehash.average_hash(Image.open(file))
    return image_hash

def check_hash(hash_string):
    '''Checking hash against the HASHES set.
    '''
    if hash_string in HASHES:
        return True
#if hash is not a duplicate, add hash and return False
    HASHES.add(hash_string)
    return False

def save_temp_file(data, extension):
    '''Save image to a temp file.
    '''
    with open('temp_file.' + extension, "wb") as temp:
        temp.write(data)

def convert_image_to_png(name, extension):
    '''Convert the image to png.
    '''
    with Image.open(name + '.' + extension) as image:
        image.save(name + '.png')

def crop_image(filename, extension):
    '''Crop the image.
    '''
#if it's not PNG already, it will be
    if extension != 'png':
        convert_image_to_png(filename, extension)
        Path.unlink(filename + '.' + extension)
        extension = 'png'
    file = filename + '.' + extension
    with Image.open(file) as image:
#crop to content
        image_bounds = image.getbbox()
        cropped = image.crop(image_bounds)
        cropped.save(file)

def extract_images(file, result_dir):
    '''Extracting images from a pdf file.
    '''
    count = 0
    reader = PdfReader(file)
    for page_num,page in enumerate(reader.pages):
        for image_file_object in page.images:
            full_filename = str(page_num) + '_' + str(count) + image_file_object.name
#splitting filename and extension
            filename,extension = full_filename.split('.')
#temp file
            save_temp_file(image_file_object.data, extension)
#crop + convert
            crop_image('temp_file', extension)
#checking for duplicates
#if so, skip the image
            if check_hash(make_hash('temp_file.png')):
                pass
            else:
#save the resulting non-duplicate png file
                with Image.open('temp_file.png') as final_image:
                    final_image.save(result_dir + '/' + filename + '.' + 'png')
                count += 1
            Path.unlink('temp_file.png')

#pdf file name
try:
    pdf_file = Path(sys.argv[1])
except IndexError:
    print('No pdf file!')
    print(__doc__)
    exit()
#directory for images, 'pdf file name' + _export
save_dir = Path(str(pdf_file.parent / pdf_file.stem) + '_export')

print('Saving images in', save_dir)

try:
    save_dir.mkdir(exist_ok=True)
except FileNotFoundError:
    print('Can\'t create dir', save_dir)

#Calling the main function
extract_images(pdf_file, str(save_dir))
print(f'Saved {len(HASHES)} unique images.')
