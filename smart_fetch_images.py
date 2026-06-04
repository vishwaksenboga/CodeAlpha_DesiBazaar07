"""
smart_fetch_images.py  (v3)
Uses the Wikipedia REST /page/summary API to get CDN-accessible thumbnails.
Validates relevance before saving & updating DB.
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

UA = 'Mozilla/5.0 (compatible; DesiBazaarBot/1.0; +https://desibazaar.example.com/bot)'
MEDIA_DIR = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# All 60 products that still need proper images
PRODUCT_IDS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41,
    42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    52, 53, 54, 55, 57, 58, 59, 60, 61, 62
]

STOP_WORDS = {'of', 'the', 'a', 'an', 'and', 'in', 'on', 'for', 'with',
              'set', 'mix', 'powder', 'oil', 'gel', 'juice', 'syrup',
              'sticks', 'piece', 'pack', 'bag', 'jar', 'bottle', 'hand',
              'handmade', 'organic', 'premium', 'wild', 'raw', 'pure'}

def keywords(text):
    words = text.lower().replace('(', ' ').replace(')', ' ').replace('&', ' ').split()
    return set(w.strip('.,') for w in words if w not in STOP_WORDS and len(w) > 2)

def is_relevant(product_name, page_title, page_description=''):
    prod_kws = keywords(product_name)
    haystack = (page_title + ' ' + page_description).lower()
    for kw in prod_kws:
        if kw in haystack:
            return True
    return False

def wiki_search_titles(query):
    """Use OpenSearch to find up to 5 candidate article titles."""
    url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=opensearch&search={urllib.parse.quote(query)}"
        f"&limit=5&namespace=0&format=json"
    )
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        res = urllib.request.urlopen(req, timeout=8)
        data = json.loads(res.read())
        return data[1] if len(data) > 1 else []
    except Exception as e:
        print(f"    [!] OpenSearch error: {e}")
        return []

def wiki_rest_summary(title):
    """Fetch page summary from REST API — returns (title, description, thumbnail_url) or Nones."""
    encoded = urllib.parse.quote(title.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'})
        res = urllib.request.urlopen(req, timeout=8)
        data = json.loads(res.read())
        title_out = data.get('title', title)
        description = data.get('description', '') + ' ' + data.get('extract', '')
        thumbnail = data.get('originalimage', {}).get('source') or data.get('thumbnail', {}).get('source')
        return title_out, description, thumbnail
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"    [!] REST API HTTP {e.code} for '{title}'")
        return None, None, None
    except Exception as e:
        print(f"    [!] REST API error for '{title}': {e}")
        return None, None, None

def download_image(img_url, dest_path):
    """Download image to dest_path. Returns True on success."""
    try:
        headers = {
            'User-Agent': UA,
            'Referer': 'https://en.wikipedia.org/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        }
        req = urllib.request.Request(img_url, headers=headers)
        data = urllib.request.urlopen(req, timeout=15).read()
        if len(data) < 1000:   # suspiciously small → likely an error page
            print(f"    [!] Downloaded file too small ({len(data)} bytes), skipping.")
            return False
        with open(dest_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"    [!] Download failed: {e}")
        return False

def find_image_for_product(name):
    """
    Search Wikipedia for a relevant image for the product.
    Returns (page_title, img_url) if a relevant match is found, else (None, None).
    """
    query = name.replace('(', '').replace(')', '').replace('&', 'and')
    candidate_titles = wiki_search_titles(query)

    for title in candidate_titles:
        time.sleep(0.5)
        page_title, description, img_url = wiki_rest_summary(title)
        if not img_url:
            continue
        if is_relevant(name, page_title or title, description or ''):
            return page_title or title, img_url

    return None, None

def main():
    products = {p.id: p for p in Product.objects.filter(id__in=PRODUCT_IDS)}

    matched = 0
    skipped = 0
    no_image = 0

    for pid in PRODUCT_IDS:
        p = products.get(pid)
        if not p:
            print(f"[{pid}] Not found in DB, skipping.")
            continue

        name = p.name
        print(f"\n[ID {pid}] {name}")

        page_title, img_url = find_image_for_product(name)

        if not img_url:
            print(f"  -> No relevant Wikipedia image found.")
            no_image += 1
            time.sleep(1)
            continue

        print(f"  [OK] Matched: '{page_title}'")

        ext = ".png" if ".png" in img_url.lower() else ".jpg"
        dest_filename = f"prod_{pid}{ext}"
        dest_path = MEDIA_DIR / dest_filename

        if download_image(img_url, dest_path):
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"  [OK] Saved '{dest_filename}' -> DB updated.")
            matched += 1
        else:
            print(f"  [FAIL] Could not download image for '{page_title}'.")
            skipped += 1

        time.sleep(2.0)

    print(f"\n{'='*55}")
    print(f"Done!  Applied: {matched}  |  Download failed: {skipped}  |  No match: {no_image}")

if __name__ == '__main__':
    main()
