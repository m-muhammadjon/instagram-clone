from taggit.managers import TaggableManager
from django.conf import settings
from django.db import models
import uuid
import os

from .validators import validate_post


def get_file_path_post(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('post', filename)


class Post(models.Model):
    CHOICES = (
        ('image', 'image'),
        ('video', 'video')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='posts',
                             on_delete=models.CASCADE)
    post = models.FileField(upload_to=get_file_path_post, validators=[validate_post])
    caption = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='likes',
                                   blank=True)
    type = models.CharField(max_length=10, choices=CHOICES, null=True, default='image')
    tags = TaggableManager(blank=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comments',
                             on_delete=models.CASCADE)
    body = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)



