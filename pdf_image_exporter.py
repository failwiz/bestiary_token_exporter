'''
A pdf image parser.
'''

import sys
import os
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
    else:
        HASHES.add(hash_string) #if not in it, add and return False
        return False

def save_temp_file(data, extension):
    '''Save temp file.
    '''
    temp = open('temp_file.' + extension, "wb")
    temp.write(data)
    temp.close()

def convert_image_to_png(name, extension):
    '''Convertation to png.
    '''
    image = Image.open(name + '.' + extension)
    image.save(name + '.png')
    image.close()

def crop_image(filename, extension):
    '''Crop image.
    '''
    if extension != 'png': #if it's not png it will be
        convert_image_to_png(filename, extension)
        os.remove(filename + '.' + extension)
        extension = 'png'
    file = filename + '.' + extension
    image = Image.open(file)
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
            filename,extension = full_filename.split('.')       #splitting filename and extension
            save_temp_file(image_file_object.data, extension)   #temp file
            crop_image('temp_file', extension)                  #crop + convert
            #checking for duplicate
            #if so, skip the images
            if check_hash(make_hash('temp_file.png')):
                pass
            else:
                #save the resulting non-duplicate png file
                final_image = Image.open('temp_file.png')
                final_image.save(result_dir + '/' + filename + '.' + 'png')
                final_image.close()
                count += 1
            os.remove('temp_file.png')

#pdf file name
pdf_file = Path(sys.argv[1])
#directory for images, 'pdf file name' + _export
save_dir = Path(pdf_file.stem + '_export')
print('Saving images in', save_dir)

try:
    save_dir.mkdir(exist_ok=True)
except FileNotFoundError:
    print('Can\'t create dir', save_dir)

#Calling the main function
extract_images(pdf_file, str(save_dir))
