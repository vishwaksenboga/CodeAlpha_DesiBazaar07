import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    
    # 1. Coconut Milk Powder (145)
    src1 = r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\coconut_milk_powder_1780400326398.png"
    if os.path.exists(src1):
        dest1 = media_dir / "prod_145.png"
        shutil.copy2(src1, dest1)
        p1 = Product.objects.get(id=145)
        p1.image_url = f"/media/products/prod_145.png"
        p1.save()
        print("Updated product 145")
        
    # 2. Raw Cacao Powder (144)
    src2 = r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\raw_cacao_powder_1780400338905.png"
    if os.path.exists(src2):
        dest2 = media_dir / "prod_144.png"
        shutil.copy2(src2, dest2)
        p2 = Product.objects.get(id=144)
        p2.image_url = f"/media/products/prod_144.png"
        p2.save()
        print("Updated product 144")

if __name__ == '__main__':
    main()
