from imagekit.processors import Crop

# name on image field needs to be reverted to real filename before invalidate() or else this will never be called
def create_crop_processor(instance, file, field_name, after_processors):
    crop_coords = getattr(instance, field_name).coords_csv.split(',')
    crop_processor = []

    if len(crop_coords) == 4:
        w, h, x, y = map(int, crop_coords)
        crop_processor = [Crop(width=w, height=h, x=-x, y=-y)]
        
    return after_processors + crop_processor

def get_crop_processor(image_field, after_processors=[]):
    def call_this(instance, file):
        return create_crop_processor(instance, file, image_field, after_processors)

    return call_this
