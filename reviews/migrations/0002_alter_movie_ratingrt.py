# Generated by Django 3.2.16 on 2022-12-02 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='ratingRT',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=3),
        ),
    ]