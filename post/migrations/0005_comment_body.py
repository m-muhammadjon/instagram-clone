# Generated by Django 3.2.5 on 2021-08-02 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0004_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='body',
            field=models.TextField(null=True),
        ),
    ]
