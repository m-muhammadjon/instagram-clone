from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
import uuid
import os

from post.models import Post


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('profile', filename)


class Profile(models.Model):
    CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('not_say', 'Prefer Not To Say')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')
    photo = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    website = models.URLField(max_length=100, null=True, blank=True)
    website_name = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=CHOICES, default='not_say')
    joined = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    follows = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='follows', blank=True)
    saved = models.ManyToManyField(Post, related_name='saved', blank=True)

    def __str__(self):
        return f"Profile for user {self.user.username}"


class Contact(models.Model):
    user_from = models.ForeignKey('auth.User', related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey('auth.User', related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"{self.user_from} follows {self.user_to}"


# Add following field to User dynamically
user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                                               through=Contact,
                                               related_name='followers',
                                               symmetrical=False))
