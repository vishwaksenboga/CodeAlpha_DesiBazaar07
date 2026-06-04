import os
import django
import shutil
import glob
import time
from pathlib import Path
from icrawler.builtin import BingImageCrawler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

def fetch_image_for_product(product_id, product_name):
    # Temp directory for this specific crawl
    temp_dir = Path(f"temp_img_{product_id}")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Use bing image search (avoids DDG 403 and Wiki limits)
        crawler = BingImageCrawler(storage={'root_dir': str(temp_dir)})
        # Add "product photography" to get cleaner images
        crawler.crawl(keyword=f"{product_name} high quality", max_num=1)
        
        # Find downloaded file
        downloaded_files = glob.glob(f"{temp_dir}/*")
        if not downloaded_files:
            return False
            
        file_path = downloaded_files[0]
        ext = os.path.splitext(file_path)[1]
        if not ext:
            ext = '.jpg'
            
        dest_filename = f"prod_{product_id}_real{ext}"
        media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
        media_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = media_dir / dest_filename
        
        # Move the file
        shutil.move(file_path, dest_path)
        
        # Update db
        p = Product.objects.get(id=product_id)
        p.image_url = f"/media/products/{dest_filename}"
        p.save()
        return True
        
    except Exception as e:
        print(f"Error for {product_name}: {e}")
        return False
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    skip_ids = [153, 152, 151, 150, 149, 148, 147, 146]
    products = Product.objects.exclude(id__in=skip_ids)
    
    total = products.count()
    print(f"Starting unique image fetch for {total} products using BingCrawler...")
    
    success_count = 0
    for i, p in enumerate(products, 1):
        print(f"[{i}/{total}] Fetching unique image for: {p.name}")
        if fetch_image_for_product(p.id, p.name):
            success_count += 1
            print(f"  -> Success")
        else:
            print(f"  -> Failed. Using category fallback.")
            
    print(f"Done! Successfully fetched {success_count}/{total} unique images.")

if __name__ == '__main__':
    main()
