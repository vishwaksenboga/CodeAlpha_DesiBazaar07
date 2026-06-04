import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

def main():
    products = Product.objects.all()
    count = 0
    
    for p in products:
        updated = False
        
        # Check main image just in case
        if 'loremflickr' in p.image_url or 'cat' in p.image_url.lower():
            import urllib.parse
            safe_name = urllib.parse.quote(p.name)
            p.image_url = f"https://placehold.co/400x400/FFF8E7/FF6B35?text={safe_name}"
            updated = True
            count += 1
            
        # Wipe secondary and tertiary images completely
        if p.image_url_2:
            p.image_url_2 = ''
            updated = True
            count += 1
            
        if p.image_url_3:
            p.image_url_3 = ''
            updated = True
            count += 1
            
        if updated:
            p.save()
            
    print(f'Wiped {count} unwanted images from the database!')

if __name__ == '__main__':
    main()
