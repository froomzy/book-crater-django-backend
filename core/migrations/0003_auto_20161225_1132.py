# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-24 22:32
from __future__ import unicode_literals

from django.db import migrations, models  # type: ignore


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_user_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.FileField(blank=True, max_length=250, null=True, upload_to='avatars'),
        ),
    ]
