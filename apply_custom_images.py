import os
import django
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product

# Path to brain folders
brain_prev = r"C:\Users\vishw\.gemini\antigravity-ide\brain\4a891dbd-e5d4-43e6-a7a0-ee760f8ccdbf"
brain_curr = r"C:\Users\vishw\.gemini\antigravity-ide\brain\3fdf07a4-70d9-4270-a67d-79949316710f"

images_map = {
    # Previous session custom images
    153: os.path.join(brain_prev, "rangoli_powder_1780397896319.png"),
    152: os.path.join(brain_prev, "jute_yoga_bag_1780397911749.png"),
    151: os.path.join(brain_prev, "tamarind_candy_1780397924118.png"),
    150: os.path.join(brain_prev, "marble_box_1780397937752.png"),
    149: os.path.join(brain_prev, "khichdi_mix_1780397953206.png"),
    148: os.path.join(brain_prev, "pink_salt_1780397964356.png"),
    147: os.path.join(brain_prev, "mehndi_cone_1780397989876.png"),
    146: os.path.join(brain_prev, "biryani_masala_1780398002212.png"),
    145: os.path.join(brain_prev, "coconut_milk_powder_1780400326398.png"),
    144: os.path.join(brain_prev, "raw_cacao_powder_1780400338905.png"),

    # Current session custom images
    140: os.path.join(brain_curr, "bhopal_zardozi_pouch_1780470146991.png"),
    137: os.path.join(brain_curr, "khadi_notebook_set_1780470165381.png"),
    110: os.path.join(brain_curr, "indigo_dye_powder_1780470182473.png"),
    106: os.path.join(brain_curr, "ghee_rice_mix_1780470199709.png"),
    105: os.path.join(brain_curr, "marigold_agarbatti_1780470218706.png"),
    103: os.path.join(brain_curr, "spice_box_dabba_1780470241347.png"),
    102: os.path.join(brain_curr, "coconut_shell_ladle_1780470257589.png"),
    101: os.path.join(brain_curr, "aloe_vera_gel_1780470275771.png"),
    100: os.path.join(brain_curr, "giloy_juice_1780470293729.png"),
    99:  os.path.join(brain_curr, "flaxseed_oil_1780470308524.png"),
    94:  os.path.join(brain_curr, "lemon_rice_mix_1780470696230.png"),
    89:  os.path.join(brain_curr, "kokum_syrup_1780470711595.png"),
    84:  os.path.join(brain_curr, "ludo_board_1780470726848.png"),
    83:  os.path.join(brain_curr, "golu_doll_set_1780470749715.png"),
    82:  os.path.join(brain_curr, "multani_mitti_1780470766159.png"),
    81:  os.path.join(brain_curr, "kumkumadi_tailam_1780470781161.png"),
    80:  os.path.join(brain_curr, "rose_water_toner_1780470796936.png"),
    
    # Custom uploaded user image
    71:  os.path.join(brain_curr, "bamboo_rice_upload.png"),
}

def main():
    media_dir = Path(r"c:\Users\vishw\OneDrive\Documents\Desktop\DesiBazaar\media\products")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    # Update only the mapped products to preserve Wikipedia/pollinations images for others
    for pid, src_image in images_map.items():
        if not os.path.exists(src_image):
            print(f"Warning: File not found for ID {pid}: {src_image}")
            continue
            
        dest_filename = f"prod_{pid}.png"
        dest_path = media_dir / dest_filename
        
        # Copy the file
        shutil.copy2(src_image, dest_path)
        
        # Delete alternative extensions (.jpg, .jpeg, .webp) to prevent issues
        for ext in ['.jpg', '.jpeg', '.webp']:
            alt_file = media_dir / f"prod_{pid}{ext}"
            if alt_file.exists():
                alt_file.unlink()
        
        # Update the database URL
        try:
            p = Product.objects.get(id=pid)
            p.image_url = f"/media/products/{dest_filename}"
            p.save()
            print(f"Connected custom image for product {pid}: {p.name}")
        except Product.DoesNotExist:
            print(f"Product {pid} not found in DB")

    print("\nSuccessfully connected all custom images in the database!")

if __name__ == '__main__':
    main()
