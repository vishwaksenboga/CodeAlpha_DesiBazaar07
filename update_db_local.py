import os
import django
import urllib.parse
import urllib.request
import random
import time
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desibazaar.settings')
django.setup()

from store.models import Product, Review, Category
from django.contrib.auth.models import User

# Ensure media directory exists
MEDIA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'products')
os.makedirs(MEDIA_DIR, exist_ok=True)

USERNAMES = ['Aarav', 'Vihaan', 'Aditya', 'Sai', 'Arjun', 'Diya', 'Ananya', 'Saanvi', 'Kavya', 'Isha', 
             'Rohan', 'Neha', 'Pooja', 'Rahul', 'Sneha', 'Vikram', 'Priya', 'Amit', 'Sunita', 'Rajesh']

# Realistic reviews categorized by product categories
REVIEWS_BY_CATEGORY = {
    'Traditional Foods': [
        "Absolutely authentic taste, reminds me of home cooking.",
        "Very fresh and tasty. Packaging was airtight and clean.",
        "Great flavors. It has the perfect balance of spices.",
        "Excellent quality, will definitely order again.",
        "Authentic regional product, highly recommended!"
    ],
    'Regional Snacks': [
        "Very crispy and fresh. Not too oily.",
        "Perfect evening snack with tea. Everyone at home loved it.",
        "Exactly the regional taste I was craving for.",
        "Nice packaging, arrived without being crushed.",
        "Authentic taste and good quantity for the price."
    ],
    'Organic Products': [
        "Pure and natural. You can feel the organic quality.",
        "Great packaging and very fresh product.",
        "Excellent addition to our kitchen, completely chemical free.",
        "Very high quality product, definitely worth buying.",
        "Genuine organic product, very happy with the purchase."
    ],
    'Handicrafts': [
        "Exquisite craftsmanship! The attention to detail is stunning.",
        "Beautifully made. Adds a great traditional touch to my home.",
        "Well packaged to prevent damage. Excellent work by the artisans.",
        "Stunning piece of art. Highly recommended.",
        "Great quality and beautiful design. Proud to support local makers."
    ],
    'Festival Specials': [
        "Perfect for the festive season! Looks very beautiful.",
        "Brings back the authentic festival vibes. Very happy.",
        "Excellent quality and timely delivery before the festival.",
        "Beautifully designed, made our celebration special.",
        "Highly recommended for festivals, very genuine quality."
    ],
    'Dry Fruits': [
        "Large sized, fresh and crunchy. Very premium quality.",
        "A bit expensive but the quality is absolutely top-notch.",
        "Well packed in a resealable pouch, fresh taste.",
        "Excellent product. Clean and good quality dry fruits.",
        "Highly recommended, very nutritious and fresh."
    ],
    'Spices': [
        "Very aromatic spices. A small pinch is enough for great flavor.",
        "Extremely fresh and freshly ground aroma.",
        "Adds the perfect authentic touch to our cooking.",
        "Great quality, clean and premium spices.",
        "Will buy again, much better than standard supermarket brands."
    ],
    'Home Decor': [
        "Looks very elegant in our living room. Excellent design.",
        "Beautiful product, matches the pictures exactly.",
        "Sturdy and well-crafted. Worth the money.",
        "A premium home decor piece. Packed safely.",
        "Beautiful addition to my house, very satisfying."
    ],
    'Ayurvedic Products': [
        "Very effective and completely natural. No side effects.",
        "Authentic herbal product, can feel the difference.",
        "High quality ingredients used, very satisfied.",
        "Genuine Ayurvedic preparation. Highly recommended.",
        "Excellent product, helped me a lot. Safe packaging."
    ],
    'Beauty Products': [
        "Gentle on skin and has a lovely natural fragrance.",
        "Excellent product, works beautifully. Will buy again.",
        "Completely natural and nourishing. Very happy.",
        "High quality product, feels premium on the skin.",
        "Perfect daily beauty product, clean ingredients."
    ],
    'Textiles': [
        "The fabric quality is outstanding, very soft and premium.",
        "Beautiful weaving and intricate designs. Fits perfectly.",
        "Colors are vibrant and exactly as shown in photos.",
        "Excellent craftsmanship, feels very rich and authentic.",
        "Beautiful textile work, highly recommended for traditional wear."
    ],
    'Tea & Coffee': [
        "Amazing aroma! The flavor is rich and refreshing.",
        "Best tea/coffee I've had in a long time. Authentic origin.",
        "Very refreshing cup, perfect notes and body.",
        "Premium quality leaves/beans, safe packaging.",
        "Highly recommended for beverage lovers. Excellent quality."
    ],
    'Wellness Products': [
        "Great for daily wellness, highly effective.",
        "Feel much more energetic and healthy. Natural product.",
        "Excellent quality wellness product, packaging is good.",
        "Genuine product, helped improve my daily routine.",
        "Very good quality, completely natural ingredients."
    ],
    'Handmade Gifts': [
        "Perfect gift option! The handmade touch makes it special.",
        "Extremely beautiful and unique. The recipient loved it.",
        "Great craftsmanship, looks very premium and elegant.",
        "Very neat work. Glad I purchased this handmade item.",
        "Highly satisfying purchase. Authentic and unique."
    ],
    'Kitchen Essentials': [
        "Very durable and high quality material.",
        "Traditional kitchen tool, works perfectly as described.",
        "Excellent quality, makes cooking much easier.",
        "Sturdy build and premium finish. Highly recommended.",
        "Exactly what I needed for my traditional Indian kitchen."
    ],
    'Eco-Friendly Products': [
        "Love the sustainable initiative. Excellent green product.",
        "Durable, functional and completely eco-friendly.",
        "Highly pleased with the quality, great alternative to plastic.",
        "Good packaging, 100% biodegradable and useful.",
        "Excellent product. Support sustainability!"
    ],
    'Cultural Products': [
        "Very authentic cultural item. Perfect for rituals and decor.",
        "Brings regional culture to life. High quality.",
        "Beautiful design, very satisfied with the details.",
        "Exactly as traditional items should be. Excellent.",
        "Highly recommended, genuine regional craft."
    ],
    'Stationery': [
        "Lovely design, paper quality is excellent.",
        "Perfect for daily writing or gifting. Very unique.",
        "High quality handmade stationery, beautiful texture.",
        "Very neat finish, elegant and useful product.",
        "Highly recommended for writing enthusiasts."
    ],
    'Toys & Games': [
        "Very safe for kids, completely non-toxic and traditional.",
        "Engaging and fun! Excellent craftsmanship on wood/clay.",
        "Beautiful traditional toy, kids loved it.",
        "Sturdy construction, educational and beautiful.",
        "Highly recommended, great alternative to plastic screen toys."
    ],
    'Daily Use Items': [
        "Highly practical and durable for everyday use.",
        "Excellent quality, exactly as described. Useful.",
        "Sturdy and functional, happy with the purchase.",
        "Very good product, makes daily tasks easier.",
        "Highly recommended, premium everyday product."
    ]
}

DEFAULT_REVIEWS = [
    "Excellent quality product, very authentic.",
    "Very satisfied with the purchase. Prompt shipping.",
    "Great product, works exactly as described.",
    "Good value for money. Highly recommended.",
    "Will buy again, very authentic experience."
]

def get_or_create_users():
    users = []
    for uname in USERNAMES:
        user, created = User.objects.get_or_create(username=uname, defaults={'first_name': uname})
        users.append(user)
    return users

def download_image(url, filepath):
    """Download image from url and save to filepath with retry and backoff logic."""
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        return True

    retries = 3
    delay = 1.0
    for attempt in range(retries):
        try:
            # Sleep slightly to prevent hitting rate limits
            time.sleep(random.uniform(0.1, 0.4))
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read()
                if len(content) > 1000:  # Valid image size
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    return True
        except Exception as e:
            # Exponential backoff on error (especially 402/429)
            print(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                return False
    return False

def process_product(product, users):
    try:
        # Prompt 1
        prompt1 = f"high quality professional studio product photography of {product.name}, {product.category.name}, authentic indian, clean white background, professional lighting, centered, sharp focus, 8k resolution"
        encoded1 = urllib.parse.quote(prompt1)
        url1 = f"https://image.pollinations.ai/prompt/{encoded1}?width=600&height=600&nologo=true&seed={product.id}"
        
        # Prompt 2
        prompt2 = f"lifestyle photography of {product.name}, {product.category.name}, authentic indian, beautiful ambient warm lighting, professional commercial photography, 8k"
        encoded2 = urllib.parse.quote(prompt2)
        url2 = f"https://image.pollinations.ai/prompt/{encoded2}?width=600&height=600&nologo=true&seed={product.id + 1000}"

        # Prompt 3
        prompt3 = f"close up macro detail photography of {product.name}, {product.category.name}, authentic indian, showcasing texture and craft, professional lighting, 8k"
        encoded3 = urllib.parse.quote(prompt3)
        url3 = f"https://image.pollinations.ai/prompt/{encoded3}?width=600&height=600&nologo=true&seed={product.id + 2000}"

        file1 = os.path.join(MEDIA_DIR, f"prod_{product.id}_1.jpg")
        file2 = os.path.join(MEDIA_DIR, f"prod_{product.id}_2.jpg")
        file3 = os.path.join(MEDIA_DIR, f"prod_{product.id}_3.jpg")

        # Download all 3 (non-concurrently per product, and using small worker pool)
        success1 = download_image(url1, file1)
        success2 = download_image(url2, file2)
        success3 = download_image(url3, file3)

        if success1:
            product.image_url = f"/media/products/prod_{product.id}_1.jpg"
        if success2:
            product.image_url_2 = f"/media/products/prod_{product.id}_2.jpg"
        if success3:
            product.image_url_3 = f"/media/products/prod_{product.id}_3.jpg"

        # Check reviews
        existing_reviews = Review.objects.filter(product=product).count()
        if existing_reviews == 0 or product.review_count == 0 or product.rating != Decimal('4.6'):
            # Delete any orphaned reviews just in case
            Review.objects.filter(product=product).delete()

            # Ratings [5, 5, 5, 4, 4] -> Average = 4.6
            ratings = [5, 5, 5, 4, 4]
            selected_users = random.sample(users, 5)
            
            category_comments = REVIEWS_BY_CATEGORY.get(product.category.name, DEFAULT_REVIEWS)
            random.shuffle(category_comments)
            
            for i, rating in enumerate(ratings):
                comment = category_comments[i % len(category_comments)]
                Review.objects.create(
                    product=product,
                    user=selected_users[i],
                    rating=rating,
                    comment=comment
                )
            
            product.rating = Decimal('4.6')
            product.review_count = 5

        product.save()
        print(f"Successfully processed Product ID {product.id}: {product.name} (images: {success1}, {success2}, {success3})")
        return True
    except Exception as e:
        print(f"Error processing product {product.id} ({product.name}): {e}")
        return False

def main():
    print("Fetching users and products...")
    users = get_or_create_users()
    products = list(Product.objects.all())
    total = len(products)
    print(f"Found {total} products. Starting download and database updates using thread pool...")

    # Download images concurrently using only 2 worker threads to respect rate limiting
    success_count = 0
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(process_product, p, users): p for p in products}
        for future in as_completed(futures):
            res = future.result()
            if res:
                success_count += 1
            
    print(f"\nExecution Complete! Successfully processed {success_count}/{total} products.")

if __name__ == '__main__':
    main()
