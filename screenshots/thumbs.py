"""
django-thumbs by Antonio Melé
http://django.es
"""
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import Image


def generate_thumb(img, thumb_size, format):
    """
    Generates a thumbnail image and returns a ContentFile object with the thumbnail

    Parameters:
    ===========
    img         File object

    thumb_size  desired thumbnail size, ie: (200,120)

    format      format of the original image ('jpeg','gif','png',...)
                (this format will be used for the generated thumbnail, too)
    """

    img.seek(0)  # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(img)

    # Convert to RGB if necessary
    if image.mode not in ("L", "RGB", "RGBA"):
        image = image.convert("RGB")

    # get size
    thumb_w, thumb_h = thumb_size
    # If you want to generate a square thumbnail
    if thumb_w == thumb_h:
        # quad
        xsize, ysize = image.size
        # get minimum size
        minsize = min(xsize, ysize)
        # largest square possible in the image
        xnewsize = (xsize - minsize) / 2
        ynewsize = (ysize - minsize) / 2
        # crop it
        image2 = image.crop((xnewsize, ynewsize, xsize - xnewsize, ysize - ynewsize))
        # load is necessary after crop
        image2.load()
        # thumbnail of the cropped image (with ANTIALIAS to make it look better)
        image2.thumbnail(thumb_size, Image.ANTIALIAS)
    else:
        # not quad
        image2 = image
        image2.thumbnail(thumb_size, Image.ANTIALIAS)

    io = BytesIO()
    # PNG and GIF are the same, JPG is JPEG
    if format.upper() == "JPG":
        format = "JPEG"

    image2.save(io, format)
    return ContentFile(io.getvalue())


class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    See ImageWithThumbsField for usage example
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.field.sizes:

            def get_size(self, size):
                if not self:
                    return ""
                else:
                    split = self.url.rsplit(".", 1)
                    thumb_url = f"{split[0]}.{w}x{h}.{split[1]}"
                    return thumb_url

            for size in self.field.sizes:
                (w, h) = size
                setattr(self, f"url_{w}x{h}", get_size(self, size))

    def save(self, name, content, save=True):
        super().save(name, content, save)

        if self.field.sizes:
            for size in self.field.sizes:
                (w, h) = size
                split = self.name.rsplit(".", 1)
                thumb_name = f"{split[0]}.{w}x{h}.{split[1]}"

                # you can use another thumbnailing function if you like
                thumb_content = generate_thumb(content, size, split[1])

                thumb_name_ = self.storage.save(thumb_name, thumb_content)

                if not thumb_name == thumb_name_:
                    raise ValueError("There is already a file named %s" % thumb_name)

    def delete(self, save=True):
        name = self.name
        super().delete(save)
        if self.field.sizes:
            for size in self.field.sizes:
                (w, h) = size
                split = name.rsplit(".", 1)
                thumb_name = f"{split[0]}.{w}x{h}.{split[1]}"
                try:
                    self.storage.delete(thumb_name)
                except Exception:
                    pass


class ImageWithThumbsField(ImageField):
    """
    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=((125,125),(300,200),)

    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_125x125
        my_object.photo.url_300x200

    Note: The 'sizes' attribute is not required. If you don't provide it,
    ImageWithThumbsField will act as a normal ImageField

    How it works:
    =============
    For each size in the 'sizes' atribute of the field it generates a
    thumbnail with that size and stores it following this format:

    available_filename.[width]x[height].extension

    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.

    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)

    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg

    Note: django-thumbs assumes that if filename "any_filename.jpg" is available
    filenames with this format "any_filename.[widht]x[height].jpg" will be available, too.

    To do:
    ======
    Add method to regenerate thubmnails

    """

    attr_class = ImageWithThumbsFieldFile

    def __init__(
        self,
        verbose_name=None,
        name=None,
        width_field=None,
        height_field=None,
        sizes=None,
        **kwargs,
    ):
        self.verbose_name = verbose_name
        self.name = name
        self.width_field = width_field
        self.height_field = height_field
        self.sizes = sizes
        super().__init__(**kwargs)
