import os
import django
import urllib.parse
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

def main():
    skip_ids = [153, 152, 151, 150, 149, 148, 147, 146]
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    
    # 1. Update database to use placehold.co
    products = Product.objects.all()
    for p in products:
        if p.id in skip_ids:
            continue
            
        # URL encode the product name so it's safe for a URL
        safe_name = urllib.parse.quote(p.name)
        p.image_url = f"https://placehold.co/400x400/FFF8E7/FF6B35?text={safe_name}"
        p.save()
        
    print("Database updated to use clean text-based placeholder URLs.")

    # 2. Delete all files in media/products except the top 8 custom AI generated ones
    if media_dir.exists():
        for file_path in media_dir.iterdir():
            if file_path.is_file():
                # Extract numeric ID if possible
                filename = file_path.stem
                # Typical filename: "prod_153" or "prod_153_real"
                is_safe = False
                for safe_id in skip_ids:
                    if f"prod_{safe_id}" in filename and "real" not in filename and "gen" not in filename:
                        is_safe = True
                        break
                
                if not is_safe:
                    try:
                        file_path.unlink()
                        print(f"Deleted: {file_path.name}")
                    except Exception as e:
                        print(f"Could not delete {file_path.name}: {e}")

if __name__ == '__main__':
    main()
