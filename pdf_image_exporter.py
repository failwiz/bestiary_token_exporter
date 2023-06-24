from pypdf import PdfReader
from PIL import Image, ImageFile
#ImageFile.LOAD_TRUNCATED_IMAGES = True
#import hashlib
from io import BytesIO
import imagehash
import sys,os
from pathlib import Path


HASHES = set()


#def make_hash(file):                #make hash using hashlib
#    with open(file, 'rb') as f:
#        image_hash = hashlib.sha1()     #hashing
#        while chunk := f.read():
#            image_hash.update(chunk)
#    return image_hash.hexdigest()       #returning hash string

def make_hash(file):                                        #hash using imagehash module; less duplicates due to crop
    image_hash = imagehash.average_hash(Image.open(file))
    return image_hash

def check_hash(hash_string):            #checking hash against the HASHES set
    if hash_string in HASHES:
        return True
    else:
        HASHES.add(hash_string)         #if not in it, add and return False
        return False

def save_temp_file(data, extension):                #save temp file
    fp = open('temp_file.' + extension, "wb")
    fp.write(data)
    fp.close()

def convert_image_to_png(name, extension):
    im = Image.open(name + '.' + extension)           #convertation to png
    im.save(name + '.png')
    im.close()

def crop_image(filename, extension):                    #crop image
    if extension != 'png':                              #if it's not png it will be
        convert_image_to_png(filename, extension)
        os.remove(filename + '.' + extension)
        extension = 'png'
    file = filename + '.' + extension                   #cropping
    image = Image.open(file)
    imageBox = image.getbbox()
    cropped = image.crop(imageBox)
    cropped.save(file)

def extract_images(pdf_file, save_dir):                           #main function
    count = 0
    reader = PdfReader(pdf_file)
    for page_num,page in enumerate(reader.pages):
        for image_file_object in page.images:
            full_filename = str(page_num) + '_' + str(count) + image_file_object.name
            filename,extension = full_filename.split('.')                               #splitting filename and extension
            save_temp_file(image_file_object.data, extension)                           #temp file
            crop_image('temp_file', extension)                                          #crop + convert
            if check_hash(make_hash('temp_file.png')) == True:                          #checking if there's a same image processed already
                pass                                                                    #if so, skip the image
            else:
                im = Image.open('temp_file.png')                                        #save the resulting non-duplicate png file
                im.save(save_dir + '/' + filename + '.' + 'png')
                im.close()
                count += 1
            os.remove('temp_file.png')

pdf_file = Path(sys.argv[1])                          #pdf file name

save_dir = Path(pdf_file.stem + '_export')     #directiry for the resulting images, 'pdf file name' + _export
print('Saving images in', save_dir)
try:
    save_dir.mkdir(exist_ok=True)
except:
    print('Can\'t create dir', save_dir)

extract_images(pdf_file, str(save_dir))      #do the thing