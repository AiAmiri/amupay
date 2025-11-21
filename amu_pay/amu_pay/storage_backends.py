"""
Custom storage backends for AWS S3
Separates static files and media files into different S3 locations
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files (CSS, JS, images)"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files (user uploads)"""
    location = 'media'
    file_overwrite = False
    # Get ACL from settings - None means bucket has ACLs disabled (use bucket policies instead)
    default_acl = getattr(settings, 'AWS_DEFAULT_ACL', None)

