import os
import django
import urllib.request
import urllib.parse
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

try:
    p = Product.objects.get(id=59)
    print(f"Fixing product 59: {p.name}")
    
    # Use clean ASCII tags
    tags = "handmade,macrame,wall,art,indian,india"
    url1 = f"https://loremflickr.com/600/600/{tags}?random=59"
    url2 = f"https://loremflickr.com/600/600/{tags}?random=1059"
    url3 = f"https://loremflickr.com/600/600/{tags}?random=2059"
    
    MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'products')
    file1 = os.path.join(MEDIA_DIR, "prod_59_1.jpg")
    file2 = os.path.join(MEDIA_DIR, "prod_59_2.jpg")
    file3 = os.path.join(MEDIA_DIR, "prod_59_3.jpg")
    
    def download(url, filepath):
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read()
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
            
    success1 = download(url1, file1)
    success2 = download(url2, file2)
    success3 = download(url3, file3)
    
    if success1:
        p.image_url = "/media/products/prod_59_1.jpg"
    if success2:
        p.image_url_2 = "/media/products/prod_59_2.jpg"
    if success3:
        p.image_url_3 = "/media/products/prod_59_3.jpg"
        
    p.save()
    print("Product 59 fixed successfully!")
except Exception as e:
    print(f"Failed to fix: {e}")
