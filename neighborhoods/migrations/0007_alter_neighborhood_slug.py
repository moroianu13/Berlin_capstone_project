# Generated by Django 5.1.1 on 2024-09-30 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0006_neighborhood_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neighborhood',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
