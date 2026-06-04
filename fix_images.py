import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product
import store.management.commands.seed_products as sp

count = 0
for p_data in sp.PRODUCTS:
    try:
        p = Product.objects.get(name=p_data['name'])
        p.image_url = p_data['image_url']
        p.save()
        count += 1
    except Product.DoesNotExist:
        pass

print(f"Restored {count} product images to their original Unsplash URLs.")
