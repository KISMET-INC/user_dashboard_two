# Generated by Django 2.2.4 on 2020-12-30 00:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_one', '0019_user_img'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='img',
            new_name='user_img',
        ),
    ]