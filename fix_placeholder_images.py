"""
fix_placeholder_images.py
Replaces all small placeholder PNGs (products 1-62) with real Wikipedia images.
Uses the REST /page/summary API which returns accessible thumbnail URLs.
"""
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

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
MEDIA_DIR = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")

# Map each product to best Wikipedia article title for REST summary API
WIKI_MAP = {
    1:  "Mango pickle",
    2:  "Saffron",
    3:  "Darjeeling tea",
    4:  "Madhubani art",
    5:  "Arabica coffee",
    6:  "Banarasi silk",
    7:  "Mysore Sandal Soap",
    8:  "Coconut oil",
    9:  "Assam tea",
    10: "Channapatna toys",
    11: "Indian gooseberry",
    12: "Blue pottery of Jaipur",
    13: "Gathiya",
    14: "Dhokra",
    15: "Shahi tukda",
    16: "Cashew",
    17: "Kantha",
    18: "Withania somnifera",
    19: "Bamboo toothbrush",
    20: "Lac bangle",
    21: "Guntur chilli",
    22: "Cinnamon",
    23: "Cardamom",
    24: "Turmeric",
    26: "Almond",
    27: "Medjool",
    28: "Walnut",
    29: "Raisin",
    30: "Ghee",
    31: "Jaggery",
    32: "Honey",
    33: "Kondapalli toys",
    34: "Warli painting",
    35: "Diya (lamp)",
    36: "Phulkari",
    37: "Triphala",
    38: "Brahmi",
    39: "Neem",
    40: "Terracotta",
    41: "Rajasthan",
    42: "Bidriware",
    43: "Shilajit",
    44: "Moringa",
    45: "Handi",
    46: "Rolling pin",
    47: "Nippattu",
    48: "Khakhra",
    49: "Kodubale",
    50: "Murukku",
    51: "Mysore pak",
    52: "Kaju katli",
    53: "Peda (sweet)",
    54: "Ikat",
    55: "Pashmina",
    57: "Jute",
    58: "Coconut",
    59: "Macrame",
    60: "Soy candle",
    61: "Journal (book)",
    62: "Pen",
}

def get_wiki_image(title):
    """Fetch thumbnail from Wikipedia REST API for a given article title."""
    encoded = urllib.parse.quote(title.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read())
        # Prefer a medium-size thumbnail (~640px) over original (could be huge)
        thumb = data.get('thumbnail', {}).get('source')
        return thumb, data.get('title', title)
    except urllib.error.HTTPError as e:
        print(f"    [!] HTTP {e.code} for '{title}'")
        return None, None
    except Exception as e:
        print(f"    [!] Error: {e}")
        return None, None

def download(img_url, dest_path):
    headers = {
        'User-Agent': UA,
        'Referer': 'https://en.wikipedia.org/',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    }
    try:
        req = urllib.request.Request(img_url, headers=headers)
        data = urllib.request.urlopen(req, timeout=15).read()
        if len(data) < 5000:
            print(f"    [!] Too small ({len(data)} bytes), skipping")
            return False
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [!] Download failed: {e}")
        return False

def main():
    ok = 0
    failed = 0
    
    for pid, wiki_title in WIKI_MAP.items():
        p = Product.objects.filter(id=pid).first()
        if not p:
            print(f"[{pid}] Not found in DB")
            continue
        
        print(f"[ID {pid}] {p.name}  ->  searching '{wiki_title}'")
        img_url, found_title = get_wiki_image(wiki_title)
        
        if not img_url:
            print(f"  [FAIL] No image found on Wikipedia")
            failed += 1
            time.sleep(1)
            continue
        
        print(f"  Found: {found_title} | {img_url[:80]}...")
        
        ext = ".png" if ".png" in img_url.lower() else ".jpg"
        dest_filename = f"prod_{pid}{ext}"
        dest_path = MEDIA_DIR / dest_filename
        
        if download(img_url, dest_path):
            # Remove old .png if we saved as .jpg (or vice versa)
            old_ext = ".png" if ext == ".jpg" else ".jpg"
            old_path = MEDIA_DIR / f"prod_{pid}{old_ext}"
            if old_path.exists():
                old_path.unlink()
            
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"  [OK] Saved {dest_filename} ({dest_path.stat().st_size // 1024} KB) -> DB updated")
            ok += 1
        else:
            failed += 1
        
        time.sleep(1.5)
    
    print(f"\n{'='*55}")
    print(f"Done!  Fixed: {ok}  |  Failed: {failed}")

if __name__ == '__main__':
    main()
