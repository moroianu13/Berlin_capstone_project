from django.db import migrations
from django.utils.text import slugify

def populate_slugs(apps, schema_editor):
    Neighborhood = apps.get_model('neighborhoods', 'Neighborhood')
    for neighborhood in Neighborhood.objects.all():
        # Generate a slug based on the name
        slug = slugify(neighborhood.name)
        # Ensure slug uniqueness by appending the ID if a duplicate exists
        unique_slug = slug
        counter = 1
        while Neighborhood.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{counter}"
            counter += 1
        neighborhood.slug = unique_slug
        neighborhood.save()

class Migration(migrations.Migration):

    dependencies = [
        ('neighborhoods', '0007_alter_neighborhood_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs),
    ]
