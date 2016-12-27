# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-26 03:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='books',
            options={'verbose_name_plural': 'books'},
        ),
        migrations.AlterModelOptions(
            name='prices',
            options={'verbose_name_plural': 'prices'},
        ),
        migrations.AddField(
            model_name='prices',
            name='cz_koruna',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='Kč'),
        ),
        migrations.AlterField(
            model_name='books',
            name='isbn',
            field=models.CharField(max_length=13, primary_key=True, serialize=False, verbose_name='ISBN'),
        ),
        migrations.AlterField(
            model_name='prices',
            name='uk_pounds',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name='£'),
        ),
    ]
