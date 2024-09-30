# Generated by Django 5.1.1 on 2024-09-26 11:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0002_lifestyle_borough_slug_remove_borough_lifestyles_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Amenity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amenity_type', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.neighborhood')),
            ],
        ),
        migrations.CreateModel(
            name='CrimeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crime_rate', models.FloatField()),
                ('crime_type', models.CharField(max_length=50)),
                ('date_collected', models.DateField()),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.neighborhood')),
            ],
        ),
        migrations.CreateModel(
            name='Demographics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_friendly_percentage', models.FloatField()),
                ('foreign_residents_percentage', models.FloatField()),
                ('median_income', models.FloatField()),
                ('age_distribution', models.JSONField()),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.neighborhood')),
            ],
        ),
        migrations.CreateModel(
            name='RentData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_rent', models.FloatField()),
                ('median_rent', models.FloatField()),
                ('min_rent', models.FloatField()),
                ('max_rent', models.FloatField()),
                ('date_collected', models.DateField()),
                ('neighborhood', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='neighborhoods.neighborhood')),
            ],
        ),
    ]