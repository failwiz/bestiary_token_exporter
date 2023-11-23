# bestiary_token_exporter
Rips all the images from a PDF file. Useful for getting tokens for TTRPG from digital bestiaries.

# Dependencies
- python3 (obviously), imagehash, pypdf, PIL

#  Install
Clone or download and extract, then in that folder
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Usage
Currently:
 - takes a pdf file name as an input: `python3 pdf_image_exporter.py some.pdf`
    * filename can be a full path: `python3 pdf_image_exporter.py /path/to/some.pdf`
 - creates a folder with pdf name + _export: Test_export
    * if filename is a path, then folder is created in the same parent folder as the pdf file
 - gets *all* the images in pdf file
 - while getting images, crops to content and converts them to webp (if they are not already)
 - checks if the same image was pulled already, using hash
    * it is possible to tune duplicate detection with **HASH_SIZE** constant (less is more strict, more leaves more dupes)
 - saves the non-duplicate images to the _export folder
 - some duplicates still slip past, if they are technically different (due to *initial* cropping)
 - filenames just numbered in the order of pulling; getting text from pdf is too much of a pain to bother trying to implement it

 # TODO
  - probably some way to explicitly point to a specific page or a range of pages
  - fiddle with the versions of dependencies