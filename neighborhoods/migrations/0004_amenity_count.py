# Generated by Django 5.1.1 on 2024-09-26 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0003_amenity_crimedata_demographics_rentdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='amenity',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
