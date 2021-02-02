# Generated by Django 2.2.4 on 2021-02-01 19:07

from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_name', models.CharField(max_length=30)),
                ('user_img', django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='png', keep_meta=True, quality=100, size=[200, 200], upload_to='images/')),
                ('password', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('user_level', models.IntegerField()),
                ('followers', models.ManyToManyField(related_name='being_followed', to='app_one.User')),
                ('following', models.ManyToManyField(related_name='is_following', to='app_one.User')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pet_img', django_resized.forms.ResizedImageField(crop=['middle', 'center'], force_format='gif', keep_meta=True, quality=100, size=[500, 500], upload_to='images/')),
                ('name', models.CharField(max_length=25)),
                ('desc', models.CharField(max_length=5)),
                ('likes', models.ManyToManyField(related_name='likes', to='app_one.User')),
                ('loves', models.ManyToManyField(related_name='loves', to='app_one.User')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app_one.User')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=255)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app_one.Image')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app_one.User')),
            ],
        ),
    ]
