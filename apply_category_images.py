import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

cat_images = {
    'Spices': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_spices_1780398567314.png",
    'Handicrafts': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_handicrafts_1780398582700.png",
    'Clothing & Textiles': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_textiles_1780398595893.png",
    'Cultural Products': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_cultural_1780398610513.png",
    'Eco-Friendly Products': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_ecofriendly_1780398622973.png",
    'Traditional Foods': r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf\cat_food_1780398636682.png"
}

# Add fallbacks for other potential categories
fallback_mapping = {
    'Dry Fruits': cat_images['Spices'],
    'Wellness Products': cat_images['Eco-Friendly Products'],
    'Kitchen Essentials': cat_images['Handicrafts']
}

skip_ids = [153, 152, 151, 150, 149, 148, 147, 146]

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    products = Product.objects.all()
    
    for p in products:
        if p.id in skip_ids:
            continue
            
        cat_name = p.category.name if p.category else 'Spices'
        
        if cat_name in cat_images:
            src_image = cat_images[cat_name]
        elif cat_name in fallback_mapping:
            src_image = fallback_mapping[cat_name]
        else:
            # Default to cultural or food
            src_image = cat_images['Cultural Products']
            
        dest_filename = f"prod_{p.id}.png"
        dest_path = media_dir / dest_filename
        
        # Copy the file
        shutil.copy2(src_image, dest_path)
        
        # Update the database URL
        p.image_url = f"/media/products/{dest_filename}"
        p.save()
            
    print("Successfully assigned category-specific images to all remaining products!")

if __name__ == '__main__':
    main()
