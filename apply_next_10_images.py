import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

images_map = {
    140: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\bhopal_zardozi_pouch_1780470146991.png",
    137: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\khadi_notebook_set_1780470165381.png",
    110: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\indigo_dye_powder_1780470182473.png",
    106: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\ghee_rice_mix_1780470199709.png",
    105: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\marigold_agarbatti_1780470218706.png",
    103: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\spice_box_dabba_1780470241347.png",
    102: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\coconut_shell_ladle_1780470257589.png",
    101: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\aloe_vera_gel_1780470275771.png",
    100: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\giloy_juice_1780470293729.png",
    99: r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f\flaxseed_oil_1780470308524.png",
}

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    for pid, src_path in images_map.items():
        if not os.path.exists(src_path):
            print(f"Error: Source image not found for product {pid}: {src_path}")
            continue
            
        dest_filename = f"prod_{pid}.png"
        dest_path = media_dir / dest_filename
        
        try:
            shutil.copy2(src_path, dest_path)
            print(f"Copied image for product {pid} to {dest_path}")
            
            p = Product.objects.get(id=pid)
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"Updated product {pid} ({p.name}) in database.")
        except Product.DoesNotExist:
            print(f"Product with ID {pid} not found in database.")
        except Exception as e:
            print(f"Error processing product {pid}: {e}")

if __name__ == '__main__':
    main()
