import os
import django
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product, Category

def main():
    protected_ids = [153, 152, 151, 150, 149, 148, 147, 146, 145, 144]
    
    total_products = Product.objects.count()
    target = 100
    to_delete_count = total_products - target
    
    if to_delete_count <= 0:
        print(f"Total is already {total_products}. No need to delete.")
        return
        
    print(f"Current total: {total_products}. Need to delete {to_delete_count} products.")
    
    # We will delete products iteratively from the largest category
    deleted = 0
    
    while deleted < to_delete_count:
        # Get current counts per category (only considering unprotected products)
        unprotected = Product.objects.exclude(id__in=protected_ids)
        
        # Manually count to find the category with the most unprotected products
        counts = Counter()
        for p in unprotected:
            cat_id = p.category.id if p.category else 0
            counts[cat_id] += 1
            
        if not counts:
            print("No unprotected products left to delete!")
            break
            
        # Find category with most products
        largest_cat_id = counts.most_common(1)[0][0]
        
        # Get one unprotected product from this category
        if largest_cat_id == 0:
            product_to_delete = unprotected.filter(category__isnull=True).first()
        else:
            product_to_delete = unprotected.filter(category_id=largest_cat_id).first()
            
        if product_to_delete:
            print(f"Deleting '{product_to_delete.name}' from category ID {largest_cat_id}")
            product_to_delete.delete()
            deleted += 1
        else:
            print(f"Error: Couldn't find product in category {largest_cat_id}")
            break
            
    print(f"Finished. Deleted {deleted} products. New total: {Product.objects.count()}")
    
    # Also clean up any categories that now have 0 products
    for c in Category.objects.all():
        if c.products.count() == 0:
            print(f"Deleting empty category: {c.name}")
            c.delete()

if __name__ == '__main__':
    main()
