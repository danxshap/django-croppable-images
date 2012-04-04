from django.conf import settings

IMAGES_UPLOAD_TO = getattr(settings, 'CROPPABLE_IMAGES_UPLOAD_TO', 'croppable')
IMAGE_FIELD_DELIMITER = getattr(settings, 'CROPPABLE_IMAGE_FIELD_DELIMITER', '--_') 
