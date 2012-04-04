from django import forms
from croppable.widgets import CroppableImageWidget
from croppable.settings import IMAGE_FIELD_DELIMITER

class CroppableImageField(forms.MultiValueField):

    def __init__(self, widget=None, *args, **kwargs):
        kwargs.update({'required': False})

        if not widget:
            widget = CroppableImageWidget

        self.widget = widget

        fields = (
            forms.ImageField(),
            forms.CharField(),
        )

        super(CroppableImageField, self).__init__(fields, *args, **kwargs)

    # you need to implement compress() in a MultiValueField subclass to return a single value for the form's cleaned_data
    def compress(self, data_list):
        if data_list:
            # if the widget returns False as opposed to None, the "clear" checkbox was checked (this is a Django thing)
            if data_list[0] is False:
                return False

            image_file = data_list[0]
            coords_csv = data_list[1]

            # an image won't exist here if the image field is being cleared by the user
            if image_file:
                if IMAGE_FIELD_DELIMITER in image_file.name:
                    raise forms.ValidationError('You cannot upload image files containing the image field delimiter: \"' + \
                                                IMAGE_FIELD_DELIMITER + '\".  You can configure this with the \
                                                IMAGE_FIELD_DELIMITER setting')

                image_file.name = IMAGE_FIELD_DELIMITER.join([image_file.name, coords_csv])
            
                return image_file

            if coords_csv:
                return coords_csv

        return None
