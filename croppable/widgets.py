from django.forms.widgets import MultiWidget, HiddenInput
from django.contrib.admin.widgets import AdminFileWidget

class JCropWidget(AdminFileWidget):

    class Media:
        js = ('croppable/js/jquery-1.4.4.min.js', 'croppable/js/cropped_image_admin.js', 'croppable/js/jquery.Jcrop.js',)
        css = { 'all': ('croppable/css/jquery.Jcrop.css', ) }

    def __init__(self, initial_crop_width=160, initial_crop_height=90, min_crop_width=None, min_crop_height=None, \
            max_crop_width=None, max_crop_height=None, min_image_width=None, min_image_height=None, \
            fix_aspect_ratio=False, attrs=None):

        # make sure the jcrop_file class is added to attrs
        if not attrs:
            attrs = {'class' : 'jcrop_file'}
        elif attrs.has_key('class'):
            attrs['class'] = attrs['class'] + ' jcrop_file'

        # add some data attributes to the file input element to configure JCrop
        attrs['data-initial-crop-width'] = int(initial_crop_width) 
        attrs['data-initial-crop-height'] = int(initial_crop_height)
        attrs['data-fix-aspect-ratio'] = int(fix_aspect_ratio)
        attrs['data-min-crop-width'] = min_crop_width if min_crop_width != None else 'null'
        attrs['data-min-crop-height'] = min_crop_height if min_crop_height != None else 'null'
        attrs['data-max-crop-width'] = max_crop_width if max_crop_width != None else 'null'
        attrs['data-max-crop-height'] = min_crop_width if min_crop_width != None else 'null'
        attrs['data-min-image-width'] = min_image_width if min_image_width != None else 'null'
        attrs['data-min-image-height'] = min_image_height if min_image_height != None else 'null'

        super(JCropWidget, self).__init__(attrs)

    def render(self, name, value, attrs):
        # used throughout JS code to consistently refer to target image element
        attrs['data-target-img-id'] = 'jcrop_img_' + name

        # if an image is already uploaded, add the url so that it can be displayed for cropping
        if value and hasattr(value, 'url'):
            attrs['data-existing-img-url'] = value.url

        return super(JCropWidget, self).render(name, value, attrs)

class CroppableImageWidget(MultiWidget):

    def __init__(self, file_widget=JCropWidget, coords_widget=HiddenInput, attrs=None):
        widgets = (
            file_widget,
            coords_widget
        )                                           
        super(CroppableImageWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            croppable_image_file = value

            return [croppable_image_file, croppable_image_file.coords_csv]

        return [value, '']

    def render(self, name, value, attrs):
        attrs['data-coords-field-id'] = attrs['id'] + '_1'
        return super(CroppableImageWidget, self).render(name, value, attrs)
