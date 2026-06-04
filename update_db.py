import os
import django
import urllib.parse
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product, Review, Category
from django.contrib.auth.models import User

def update_products():
    print("Updating products with realistic unique images...")
    products = Product.objects.all()
    
    # Create some dummy users for reviews
    usernames = ['Aarav', 'Vihaan', 'Aditya', 'Sai', 'Arjun', 'Diya', 'Ananya', 'Saanvi', 'Kavya', 'Isha']
    users = []
    for uname in usernames:
        user, created = User.objects.get_or_create(username=uname, defaults={'first_name': uname})
        users.append(user)

    review_texts = [
        "Absolutely amazing product! The quality is top-notch.",
        "Very authentic and exactly as described. Will buy again.",
        "Good value for money. The packaging was also very safe.",
        "Loved it! Reminds me of home. Highly recommended.",
        "Beautiful craftsmanship and great attention to detail.",
        "A bit pricey but totally worth it for the authenticity.",
        "Fast delivery and the product is fresh and genuine.",
        "Exceeded my expectations. Great addition to my collection.",
        "The best I have bought online so far.",
        "Very satisfied with this purchase."
    ]

    updated_count = 0
    for p in products:
        # Update image
        prompt = f"high quality product photography of {p.name}, {p.category.name}, authentic indian, white background, cinematic lighting, 8k resolution"
        encoded_prompt = urllib.parse.quote(prompt)
        p.image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=600&height=600&nologo=true&seed={p.id}"
        
        # Add secondary images
        prompt2 = f"lifestyle photography of {p.name}, {p.category.name}, authentic indian, natural lighting, beautiful setting"
        encoded_prompt2 = urllib.parse.quote(prompt2)
        p.image_url_2 = f"https://image.pollinations.ai/prompt/{encoded_prompt2}?width=600&height=600&nologo=true&seed={p.id + 1000}"
        
        # We need to add reviews
        existing_reviews = Review.objects.filter(product=p).count()
        if existing_reviews == 0:
            # Create 3 reviews (Ratings: 5, 5, 4 => Avg 4.67)
            # Or mix it up a bit
            ratings_to_add = [5, 5, 4]
            selected_users = random.sample(users, 3)
            for i, r in enumerate(ratings_to_add):
                Review.objects.create(
                    product=p,
                    user=selected_users[i],
                    rating=r,
                    comment=random.choice(review_texts)
                )
            
            p.rating = Decimal('4.6')
            p.review_count = 3
        
        p.save()
        updated_count += 1
        if updated_count % 10 == 0:
            print(f"Updated {updated_count} products...")

    print(f"Successfully updated {updated_count} products.")

if __name__ == '__main__':
    update_products()
