# Generated by Django 5.1.1 on 2024-09-30 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0005_alter_amenity_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='neighborhood',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
