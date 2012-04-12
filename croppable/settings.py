from django.conf import settings

IMAGE_FIELD_DELIMITER = getattr(settings, 'CROPPABLE_IMAGE_FIELD_DELIMITER', '--_') 
