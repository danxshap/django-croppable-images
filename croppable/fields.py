import os

from django.db.models.fields.files import ImageField, ImageFieldFile
from croppable.settings import IMAGE_FIELD_DELIMITER
from croppable.widgets import CroppableImageWidget

class CroppableImageFieldFile(ImageFieldFile):

    def __init__(self, instance, field, name):
        # stash the filename on the model instance - if we are just updating coordinates, the original filename would not be available otherwise
        if not hasattr(instance, field.name + '_stashed_name'):
            setattr(instance, field.name + '_stashed_name', name)

        super(CroppableImageFieldFile, self).__init__(instance, field, name)

        # update self.name to the actual filename and save crop coordinates in another attribute
        if name != None and IMAGE_FIELD_DELIMITER in name:
            name_components = name.split(IMAGE_FIELD_DELIMITER)
            self.original_name = name
            self.filename = name_components[0]
            self.coords_csv = name_components[1]
            self.name = self.filename

    def save(self, name, content, save=True):
        # if the _committed attribute (form super-class) is True, there is no new image to upload
        # that means we are either just changing coordinates (in which case name = coordinates) or not changing anything at all (use self.coords_csv)
        if self._committed:
            coords_csv = self.coords_csv if hasattr(self, 'coords_csv') else name
            stashed_filepath = getattr(self.instance, self.field.name + '_stashed_name').split(IMAGE_FIELD_DELIMITER)[0]
            compound_name = IMAGE_FIELD_DELIMITER.join([stashed_filepath, coords_csv])

            # get imagekit spec field names --> spec files
            spec_dict = dict(zip(self.instance._ik.spec_fields, self.instance._ik.spec_files))

            # invalidate imagekit spec files
            if self.field.invalidate_on_save:
                self.name = self.filename if hasattr(self, 'filename') else stashed_filepath
                self.coords_csv = self.coords_csv if hasattr(self, 'coords_csv') else coords_csv
                for spec_name in self.field.invalidate_on_save:
                    if spec_name in spec_dict:
                        spec_dict.get(spec_name).invalidate()       
        else:
            # create compound filename to save to the model (basically prepends upload_to relative directory)
            compound_name = os.path.join(self.field.get_directory_name(), os.path.normpath(os.path.basename(self.original_name)))

            # call the super's save() which will save to storage with the proper filename
            # explicitly set the "save" arg to False so that model isn't saved (we don't want to save with actual filename)
            super(CroppableImageFieldFile, self).save(self.filename, content, save=False)

        # update name on both self & model instance to compound_name which is what we want to save to the database
        setattr(self.instance, self.field.name, compound_name) 
        self.name = compound_name

        # if we were supposed to save the model, now we should actually do it since the filename was reverted above
        # (the below 2 lines are also the last 2 lines in the super.save() from Django)
        if save:
            self.instance.save()

class CroppableImageField(ImageField):
    attr_class = CroppableImageFieldFile
    invalidate_on_save = []

    # override this to allow saves even if the image file doesn't change (to update crop coordinates)
    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)

        if file:
            file.save(file.name, file, save=False)

        return file

    def __init__(self, invalidate_on_save=None, crop_widget=None, *args, **kwargs):
        if invalidate_on_save:
            self.invalidate_on_save = invalidate_on_save

        if not crop_widget:
            crop_widget = CroppableImageWidget

        self.crop_widget = crop_widget

        super(CroppableImageField, self).__init__(*args, **kwargs)


# Need to tell South about CroppableImageField 
# the is_value parameter in the rule just says to use the value "from south" for the crop_widget/invalidate_on_save arguments
# south needs a value for this argument even though it has nothing to do with the database though
from south.modelsinspector import add_introspection_rules
rules = [
    (
        (CroppableImageField, ),
        [],
        {
            'crop_widget': ['from south', {'is_value': True}],
            'invalidate_on_save': ['from south', {'is_value': True}]
        }
    )
]
add_introspection_rules(rules, ['^croppable\.fields\.CroppableImageField'])
