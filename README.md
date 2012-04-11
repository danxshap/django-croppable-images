django-croppable-images
=======================
django-croppable-images is a reusable app that helps you easily add image cropping functionality to your Django projects.

When you use this app, your original images as well as their corresponding cropped versions will be saved to your default storage.  The crop coordinates are also saved so that they can be displayed to and adjusted by your end-users via a seamless front-end interface implemented as a custom Django form field + widget (using [Jcrop](http://deepliquid.com/content/Jcrop.html))

To use django-croppable-images, you will need to install [django-imagekit](https://github.com/jdriscoll/django-imagekit) which is used to manage the actual cropping of image files.

How to Use
----------
Add a `CroppableImageField` to your model where you would otherwise have a stock Django `ImageField`.

Also add an `ImageSpecField` (from django-imagekit) to your model and set its `image_field` argument to the name of the `CroppableImageField` you created above.  For the processors argument (the first positional argument in the `ImageSpecField` constructor), use the provided `get_crop_processor()` utility function and pass in the same `image_field` argument as before.

Here's an example:

    from django.db import models
    from imagekit.models import ImageSpecField
    from croppable.fields import CroppableImageField
    from croppable.utils import get_crop_processor

    class MyCoolModel(models.Model):
        name = models.CharField(max_length=200)
        some_other_field = models.CharField(max_length=200)
        my_image = CroppableImageField(invalidate_on_save=['my_image_cropped'], upload_to='my_image_folder', blank=True)
        my_image_cropped = ImageSpecField(get_crop_processor(image_field='my_image'), image_field='my_image')

`CroppableImageField` is just a subclass of Django's `ImageField`, so it takes all of the arguments supported by its superclass (e.g. `upload_to` and `blank` in the example above)

In most cases, you'll want to pass in the optional `invalidate_on_save` argument to your `CroppableImageField` and set it to a list containing just the name of your corresponding `ImageSpecField` (as is done in the above example).  This tells django-image-kit to re-process the image modifications associated with each `ImageSpecField` in the list whenever your model is saved.  This is necessary so that the cropped image file is made up-to-date if the crop coordinates are changed.

If you're familiar with ImageKit, by "re-process" above, we are just calling invalidate() on the corresponding `ImageSpecField`.
