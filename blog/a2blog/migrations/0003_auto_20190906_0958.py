# Generated by Django 2.2.5 on 2019-09-06 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a2blog', '0002_post_front_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='front_image',
            field=models.ImageField(blank=True, upload_to='posts'),
        ),
    ]
