from PIL import Image, ImageOps

class ThumbnailProcessor:

    SUFFIX = '.thumbnail'

    def build_thumbnail_filename(self, filename):
        return filename + self.SUFFIX
    
    def process(self, file_path):
        img = ImageOps.fit(Image.open(file_path), (100, 100), Image.ANTIALIAS)
        img.save(file_path + self.SUFFIX, 'JPEG')
