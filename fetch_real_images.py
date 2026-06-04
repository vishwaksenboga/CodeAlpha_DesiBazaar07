import os
import django
import urllib.request
import urllib.parse
import json
import uuid
import time
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch_wiki_image(search_term):
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(search_term)}&gsrlimit=1&prop=pageimages&format=json&piprop=thumbnail&pithumbsize=600"
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read())
        pages = data.get('query', {}).get('pages', {})
        if pages:
            return list(pages.values())[0].get('thumbnail', {}).get('source')
    except Exception as e:
        print(f"  [!] Error searching {search_term}: {e}")
    return None

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    products = Product.objects.all()
    
    # Skip the 8 products we already custom-generated images for
    skip_ids = [153, 152, 151, 150, 149, 148, 147, 146]
    products_to_process = [p for p in products if p.id not in skip_ids]
    
    total = len(products_to_process)
    print(f"Found {total} products to fetch images for. Starting...")
    
    fallback_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Spices_in_an_Indian_market.jpg/600px-Spices_in_an_Indian_market.jpg"
    
    for i, product in enumerate(products_to_process, 1):
        print(f"[{i}/{total}] Fetching image for: {product.name}")
        
        image_url = fetch_wiki_image(product.name)
        
        if not image_url and product.category:
            image_url = fetch_wiki_image(product.category.name)
            
        if not image_url:
            image_url = fallback_image
            
        try:
            req = urllib.request.Request(image_url, headers={'User-Agent': UA})
            img_data = urllib.request.urlopen(req, timeout=10).read()
                
            filename = f"prod_{uuid.uuid4().hex[:8]}.jpg"
            dest_path = media_dir / filename
            
            with open(dest_path, 'wb') as f:
                f.write(img_data)
                
            product.image_url = f"/media/products/{filename}"
            product.save()
            print(f"  -> Saved as {filename}")
        except Exception as e:
            print(f"  [X] Failed to download {image_url}: {e}")
            
        time.sleep(1.0)
        
    print("All products updated successfully!")

if __name__ == '__main__':
    main()
