import os
import django
import shutil
import urllib.request
import urllib.parse
import json
import time
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Custom generated images for first 7 products
generated_images = {
    94: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\lemon_rice_mix_1780470696230.png",
    89: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\kokum_syrup_1780470711595.png",
    84: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\ludo_board_1780470726848.png",
    83: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\golu_doll_set_1780470749715.png",
    82: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\multani_mitti_1780470766159.png",
    81: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\kumkumadi_tailam_1780470781161.png",
    80: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\rose_water_toner_1780470796936.png",
}

# Products to fetch from Wikipedia
wiki_products = {
    77: ("Pichwai Painting", "Pichhwai"),
    76: ("Dhokla", "Gujarati Dhokla"),
    75: ("Tanjore doll", "Thanjavur Golu Doll"),
    74: ("Soapnut", "Sapindus mukorossi"),
    73: ("Tragacanth gum", "Gond Katira"),
    71: ("Bamboo rice", "Bamboo seed rice"),
    70: ("Nilgiri tea", "Green tea"),
    69: ("Masala chai", "Indian Chai"),
    68: ("Kolhapuri Chappal", "Kolhapuri leather chappal"),
    66: ("Neem wood comb", "Neem wood"),
    65: ("Copper water bottle", "Copper vessel"),
    64: ("Pattachitra", "Pattachitra art"),
    63: ("Ganesha statue", "Ganesha idol white marble"),
}

def fetch_wiki_image(search_terms):
    for term in search_terms:
        print(f"  Trying Wikipedia search for: {term}")
        url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(term)}&gsrlimit=1&prop=pageimages&format=json&piprop=thumbnail&pithumbsize=600"
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        try:
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read())
            pages = data.get('query', {}).get('pages', {})
            if pages:
                source = list(pages.values())[0].get('thumbnail', {}).get('source')
                if source:
                    return source
        except Exception as e:
            print(f"    [!] Error searching {term}: {e}")
    return None

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Process custom generated images
    for pid, src_path in generated_images.items():
        if not os.path.exists(src_path):
            print(f"Error: Source image not found for product {pid}: {src_path}")
            continue
            
        dest_filename = f"prod_{pid}.png"
        dest_path = media_dir / dest_filename
        
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied custom image for product {pid} to {dest_path}")
            
            p = Product.objects.get(id=pid)
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"Updated product {pid} ({p.name}) in database.")
        except Product.DoesNotExist:
            print(f"Product with ID {pid} not found in database.")
        except Exception as e:
            print(f"Error processing custom product {pid}: {e}")
            
    # 2. Process Wikipedia images
    fallback_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Spices_in_an_Indian_market.jpg/600px-Spices_in_an_Indian_market.jpg"
    
    for pid, search_terms in wiki_products.items():
        print(f"Processing Wikipedia image for product {pid}...")
        image_url = fetch_wiki_image(search_terms)
        
        if not image_url:
            image_url = fallback_image
            print(f"  No Wikipedia image found. Using fallback.")
            
        # Determine extension from url
        ext = ".jpg"
        if ".png" in image_url.lower():
            ext = ".png"
        elif ".jpeg" in image_url.lower():
            ext = ".jpeg"
            
        dest_filename = f"prod_{pid}{ext}"
        dest_path = media_dir / dest_filename
        
        try:
            req = urllib.request.Request(image_url, headers={'User-Agent': UA})
            img_data = urllib.request.urlopen(req, timeout=10).read()
            
            with open(dest_path, 'wb') as f:
                f.write(img_data)
                
            p = Product.objects.get(id=pid)
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"  Successfully saved {dest_filename} and updated product {pid} ({p.name}) in database.")
        except Exception as e:
            print(f"  [X] Failed to download/update for product {pid}: {e}")
            
        time.sleep(1.0)

if __name__ == '__main__':
    main()
