django-croppable-images
=======================
django-croppable-images is a reusable app that helps you easily add image cropping functionality to your Django projects.

When you use this app, your original images as well as their corresponding cropped versions will be saved to your default storage.  The crop coordinates are also saved so that they can be displayed to and adjusted by your end-users via a seamless front-end interface implemented as a custom Django form field + widget (using [Jcrop](http://deepliquid.com/content/Jcrop.html)).

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

    class MyFavoriteModel(models.Model):
        name = models.CharField(max_length=200)
        some_other_field = models.CharField(max_length=200)
        my_image = CroppableImageField(invalidate_on_save=['my_image_cropped'], upload_to='my_image_folder', blank=True)
        my_image_cropped = ImageSpecField(get_crop_processor(image_field='my_image'), image_field='my_image')

`CroppableImageField` is a _model field_ that is just a subclass of Django's `ImageField`, so it takes all of the arguments supported by its superclass (e.g. `upload_to` and `blank` in the example above)

In most cases, you'll want to pass in the optional `invalidate_on_save` argument to your `CroppableImageField` and set it to a list containing just the name of your corresponding `ImageSpecField` (as is done in the above example).  This tells django-image-kit that it needs to re-process the image modifications associated with each `ImageSpecField` in the list at some point after (or at the same time as) your model is saved.  This is necessary so that the cropped image file is changed if the crop coordinates are changed.

If you're familiar with ImageKit, by "re-process" above, we are just calling invalidate() on the corresponding `ImageSpecField`.  We recommend using ImageKit's non-default `NonValidatingImageCacheBackend `.  In the context of django-croppable-images, all this does is make it so your cropped images are updated each time your model is saved.  Simply add the following line to your settings:

    IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'

Finally, to hook up the front-end interface all you need to do is use the included `CroppableImageField` _form field_ (as opposed to the model field above) to your `ModelForm`.

In the context of the Django Admin, you would just create your own `ModelForm` and have it use a `CroppableImageField` for the field that corresponds to your image.  Then simply tell your `ModelAdmin` to use that form.  Here's a full example:

    from django import forms
    from django.contrib import admin
    from myapp.models import MyFavoriteModel
    from croppable.forms import CroppableImageField

    class MyFavoriteModelAdminForm(forms.ModelForm):
        my_image = CroppableImageField()

        class Meta:
            model = MyFavoriteModel

    class MyFavoriteModelAdmin(admin.ModelAdmin):
        form = MyFavoriteModelAdminForm

    admin.site.register(MyFavoriteModel, MyFavoriteModelAdmin)

Now on the Admin site for `MyFavoriteModel` you'll have an awesome Jcrop-powered widget that lets you define a crop region for your image.  When you press save, your original image will be uploaded and a new image file will be saved that contains the cropped version.  

To display the cropped image in a template, just use the attribute on your model that contains the `ImageSpecField`:

    <img src="{% my_favorite_model_instance.my_image_cropped.url %}">

How it Works
------------
The `CroppableImageField` _model field_ subclasses the Django `ImageField` and uses its own `CroppableImageFieldFile` (a subclass of `ImageFieldFile` which overrides the file-saving functionality).  Instead of saving just the filename to the database, `CroppableImageFieldFile` saves both the filename as well as the crop coordinates (in CSV format), separated by a configurable delimiter.  To change the default, just set `CROPPABLE_IMAGE_FIELD_DELIMITER` to whatever you want it to be in your settings (note that this must contain only valid characters for use in UNIX filenames).  

The `CroppableImageField` _form field_ subclasses the Django `MultiValueField` form field and uses both an `ImageField` and `CharField` (for the crop coordinates).  This form field appends the crop coordinates to the image's filename (along with the delimiter) and passes it off to the model field / field file which knows how to parse it.  
