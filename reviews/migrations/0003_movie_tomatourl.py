# Generated by Django 3.2.16 on 2022-12-02 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_movie_ratingrt'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='tomatoURL',
            field=models.URLField(blank=True, default=''),
        ),
    ]