# bestiary_token_exporter
Currently:
 - takes a pdf file name as an input: python3 pdf_image_exporter.py Test.pdf
 - creates a folder with pdf name + _export: Test_export
 - gets all the images in pdf file
 - while getting images, crops to content and converts them to png (if they are not already)
 - checks if the same image was pulled already, using hash
 - saves the non-duplicate images to the _export folder
 - some duplicates still slip past, if they are technically different (due to *initial* cropping)

# Dependencies:
- imagehash, pypdf, PIL
