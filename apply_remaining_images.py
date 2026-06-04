import os
import django
import urllib.request
import urllib.parse
import json
import time
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

# Recommended User-Agent header to avoid rate limiting
UA = 'DesiBazaarBot/1.0 (vishwesh@desibazaar.com) Python-urllib/3.9'

wiki_products = {
    74: ("Soapnut", "Sapindus mukorossi"),
    73: ("Tragacanth gum", "Gond Katira"),
    68: ("Kolhapuri chappal", "Kolhapuri leather chappal"),
    66: ("Neem wood", "Azadirachta indica"),
    65: ("Copper vessel", "Copper water bottle"),
    64: ("Pattachitra", "Pattachitra art"),
    63: ("Ganesha statue", "Ganesha idol"),
}

def fetch_wiki_image(search_terms):
    for term in search_terms:
        print(f"  Searching Wikipedia for: {term}")
        url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(term)}&gsrlimit=1&prop=pageimages&format=json&piprop=thumbnail&pithumbsize=640"
        
        retries = 2
        while retries >= 0:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            try:
                res = urllib.request.urlopen(req, timeout=8)
                data = json.loads(res.read())
                pages = data.get('query', {}).get('pages', {})
                if pages:
                    source = list(pages.values())[0].get('thumbnail', {}).get('source')
                    if source:
                        return source
                break  # If search returned empty page, stop retrying for this term
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"    [!] Rate limited (429). Retrying in 10 seconds...")
                    time.sleep(10)
                    retries -= 1
                else:
                    print(f"    [!] HTTP Error {e.code} for {term}")
                    break
            except Exception as e:
                print(f"    [!] Connection error: {e}")
                break
        time.sleep(3.0)  # Sleep after each term search
    return None

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    fallback_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Spices_in_an_Indian_market.jpg/640px-Spices_in_an_Indian_market.jpg"
    
    for pid, search_terms in wiki_products.items():
        print(f"Processing Wikipedia image for product {pid}...")
        image_url = fetch_wiki_image(search_terms)
        
        if not image_url:
            image_url = fallback_image
            print(f"  No image found for {search_terms[0]}. Using general Indian market fallback image.")
            
        ext = ".jpg"
        if ".png" in image_url.lower():
            ext = ".png"
        elif ".jpeg" in image_url.lower():
            ext = ".jpeg"
            
        dest_filename = f"prod_{pid}{ext}"
        dest_path = media_dir / dest_filename
        
        try:
            req = urllib.request.Request(image_url, headers={'User-Agent': UA})
            img_data = urllib.request.urlopen(req, timeout=12).read()
            
            with open(dest_path, 'wb') as f:
                f.write(img_data)
                
            p = Product.objects.get(id=pid)
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"  Successfully saved {dest_filename} and updated product {pid} ({p.name}) in database.")
        except Exception as e:
            print(f"  [X] Failed to download/update for product {pid}: {e}")
            
        time.sleep(4.0)  # Moderate sleep between products

if __name__ == '__main__':
    main()
