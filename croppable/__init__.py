from imagekit.models import ImageSpec
from imagekit.processors import Crop

from croppable.fields import CroppableImageField

def get_crop_processor(instance, file, field_name):
    processor = []
    crop_coords = getattr(instance, field_name + '_coords_csv').split(',')
    if len(crop_coords) == 4:
        w, h, x, y = map(int, crop_coords)
        processor = [Crop(width=w, height=h, x=-x, y=-y)] 
    return processor

def generate_processor(name):
    def call_this(instance, file):
        return get_crop_processor(instance, file, name)

    return call_this

def setup_ik(sender, instance, **kwargs):
    # set up imagekit
    for fn in instance._meta.get_all_field_names():
        if isinstance(instance._meta.get_field(fn), CroppableImageField):
            image_cropped = ImageSpec(generate_processor(fn), image_field=fn)  
            image_cropped.contribute_to_class(instance.__class__, fn + '_cropped')
            image_cropped._update_source_hashes(instance)
