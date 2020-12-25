# Generated by Django 2.2.4 on 2020-12-25 00:26

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('app_one', '0011_auto_20201222_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='pet_img',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='png', keep_meta=True, quality=100, size=[400, 400], upload_to='images/'),
        ),
    ]
