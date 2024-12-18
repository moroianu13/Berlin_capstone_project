# Generated by Django 5.1.1 on 2024-11-22 13:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0003_remove_borough_coat_of_arms_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cultural',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('borough', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.borough')),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.neighborhood')),
            ],
        ),
    ]
