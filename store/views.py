from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST
from .models import (Category, Product, Cart, CartItem, Wishlist,
                     Order, OrderItem, Review, ContactMessage, NewsletterSubscriber)
from .forms import SignUpForm, ReviewForm, ContactForm, CheckoutForm, ProfileUpdateForm
import json


# ─── Home ───────────────────────────────────────────────────────────────────

def home(request):
    categories = Category.objects.all()[:20]
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    trending_products = Product.objects.filter(is_trending=True, is_active=True)[:8]
    all_products = Product.objects.filter(is_active=True).order_by('-created_at')[:12]

    # States for Explore India section
    states_list = [
        {'emoji': '', 'name': 'Andhra Pradesh', 'count': Product.objects.filter(state_origin='Andhra Pradesh', is_active=True).count()},
        {'emoji': '', 'name': 'Jammu & Kashmir', 'count': Product.objects.filter(state_origin__icontains='Kashmir', is_active=True).count()},
        {'emoji': '', 'name': 'Kerala', 'count': Product.objects.filter(state_origin='Kerala', is_active=True).count()},
        {'emoji': '', 'name': 'Rajasthan', 'count': Product.objects.filter(state_origin='Rajasthan', is_active=True).count()},
        {'emoji': '', 'name': 'West Bengal', 'count': Product.objects.filter(state_origin='West Bengal', is_active=True).count()},
        {'emoji': '', 'name': 'Karnataka', 'count': Product.objects.filter(state_origin='Karnataka', is_active=True).count()},
        {'emoji': '', 'name': 'Assam', 'count': Product.objects.filter(state_origin='Assam', is_active=True).count()},
        {'emoji': '', 'name': 'Gujarat', 'count': Product.objects.filter(state_origin='Gujarat', is_active=True).count()},
        {'emoji': '', 'name': 'Punjab', 'count': Product.objects.filter(state_origin='Punjab', is_active=True).count()},
        {'emoji': '', 'name': 'Maharashtra', 'count': Product.objects.filter(state_origin='Maharashtra', is_active=True).count()},
        {'emoji': '', 'name': 'Uttar Pradesh', 'count': Product.objects.filter(state_origin='Uttar Pradesh', is_active=True).count()},
        {'emoji': '', 'name': 'Tamil Nadu', 'count': Product.objects.filter(state_origin='Tamil Nadu', is_active=True).count()},
    ]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'trending_products': trending_products,
        'all_products': all_products,
        'states_list': states_list,
    }
    return render(request, 'store/home.html', context)


# ─── Product Listing ─────────────────────────────────────────────────────────

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # Filters
    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'newest')
    query = request.GET.get('q', '')

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(state_origin__icontains=query)
        )

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_map = {
        'newest': '-created_at',
        'price_low': 'price',
        'price_high': '-price',
        'rating': '-rating',
        'name': 'name',
    }
    products = products.order_by(sort_map.get(sort_by, '-created_at'))

    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'query': query,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'total_count': paginator.count,
    }
    return render(request, 'store/product_list.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return redirect(f'/products/?category={slug}')


def search_results(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(state_origin__icontains=query) |
            Q(category__name__icontains=query)
        )
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)
    context = {
        'products': products_page,
        'query': query,
        'total_count': paginator.count,
    }
    return render(request, 'store/search_results.html', context)


# ─── Product Detail ──────────────────────────────────────────────────────────

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = Review.objects.filter(product=product)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:6]

    user_review = None
    review_form = ReviewForm()
    in_wishlist = False

    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
        try:
            wl = Wishlist.objects.get(user=request.user)
            in_wishlist = wl.products.filter(id=product.id).exists()
        except Wishlist.DoesNotExist:
            pass

    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'user_review': user_review,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        # Remove existing review if any
        Review.objects.filter(product=product, user=request.user).delete()
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            # Update product rating
            avg = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']
            product.rating = round(avg, 1)
            product.review_count = Review.objects.filter(product=product).count()
            product.save()
            messages.success(request, 'Your review has been submitted!')
    return redirect('product_detail', slug=product.slug)


# ─── Cart ────────────────────────────────────────────────────────────────────

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'store/cart.html', context)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count, 'message': f'{product.name} added to cart!'})
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({'success': True, 'cart_count': cart.item_count, 'total': float(cart.total)})
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    deleted = False
    subtotal_val = 0
    if quantity < 1:
        subtotal_val = 0
        item.delete()
        deleted = True
    else:
        subtotal_val = float(item.product.effective_price * quantity)
        item.quantity = quantity
        item.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'subtotal': subtotal_val,
            'total': float(cart.total),
            'cart_count': cart.item_count,
            'deleted': deleted,
        })
    return redirect('cart')


# ─── Checkout ────────────────────────────────────────────────────────────────

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()

    if not items.exists():
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            payment_method = request.POST.get('payment_method', d.get('payment_method', 'cod'))
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.total,
                payment_method=payment_method,
                full_name=d['full_name'],
                email=d['email'],
                phone=d['phone'],
                address_line1=d['address_line1'],
                address_line2=d.get('address_line2', ''),
                city=d['city'],
                state=d['state'],
                pincode=d['pincode'],
                status='confirmed',
            )
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_image=item.product.image_url,
                    quantity=item.quantity,
                    price=item.product.effective_price,
                )
                # Decrement stock
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])
            # Clear coupon from session
            request.session.pop('coupon_code', None)
            request.session.pop('coupon_discount', None)
            cart.items.all().delete()
            messages.success(request, f'Order #{order.order_number} placed successfully! 🎉')
            return redirect('order_detail', order_number=order.order_number)
    else:
        initial = {}
        if request.user.first_name:
            initial['full_name'] = f"{request.user.first_name} {request.user.last_name}".strip()
        if request.user.email:
            initial['email'] = request.user.email
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'items': items,
    }
    return render(request, 'store/checkout.html', context)


# ─── Orders ──────────────────────────────────────────────────────────────────

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'store/orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


# ─── Wishlist ────────────────────────────────────────────────────────────────

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.filter(is_active=True)
    return render(request, 'store/wishlist.html', {'products': products})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if wishlist.products.filter(id=product_id).exists():
        wishlist.products.remove(product)
        added = False
        msg = 'Removed from wishlist'
    else:
        wishlist.products.add(product)
        added = True
        msg = 'Added to wishlist!'
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'added': added, 'message': msg,
                             'wishlist_count': wishlist.products.count()})
    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


# ─── Auth ────────────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to DesiBazaar, {user.first_name}!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})


# ─── Profile ─────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    orders = Order.objects.filter(user=request.user)[:5]
    context = {'form': form, 'orders': orders}
    return render(request, 'store/profile.html', context)


# ─── Static Pages ────────────────────────────────────────────────────────────

def about(request):
    return render(request, 'store/about.html')


def contact(request):
    success = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm()
            messages.success(request, 'Thank you! We\'ll get back to you within 24 hours.')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form, 'success': success})


def faq(request):
    return render(request, 'store/faq.html')


def privacy(request):
    return render(request, 'store/privacy.html')


def terms(request):
    return render(request, 'store/terms.html')


def returns(request):
    return render(request, 'store/returns.html')


def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
            messages.success(request, 'You\'ve been subscribed to our newsletter!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ─── 404 ─────────────────────────────────────────────────────────────────────

def custom_404(request, exception):
    return render(request, '404.html', status=404)


# ─── Search Autocomplete (AJAX) ───────────────────────────────────────────────

def search_autocomplete(request):
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(tags__icontains=q) | Q(state_origin__icontains=q),
            is_active=True
        ).select_related('category')[:8]
        for p in products:
            results.append({
                'id': p.id,
                'name': p.name,
                'category': p.category.name,
                'price': str(p.effective_price),
                'image': p.image_url,
                'url': f'/products/{p.slug}/',
                'state': p.state_origin,
            })
        # Also search categories
        cats = Category.objects.filter(name__icontains=q)[:3]
        for c in cats:
            results.append({
                'id': f'cat-{c.id}',
                'name': c.name,
                'category': 'Category',
                'price': None,
                'image': c.image_url or '',
                'url': f'/products/?category={c.slug}',
                'state': f'{c.products.count()} products',
            })
    return JsonResponse({'results': results})


# ─── Quick View (AJAX) ────────────────────────────────────────────────────────

def quick_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    in_wishlist = False
    if request.user.is_authenticated:
        try:
            wl = Wishlist.objects.get(user=request.user)
            in_wishlist = wl.products.filter(id=product_id).exists()
        except Wishlist.DoesNotExist:
            pass
    data = {
        'id': product.id,
        'name': product.name,
        'slug': product.slug,
        'description': product.short_description or product.description[:200],
        'price': str(product.effective_price),
        'original_price': str(product.price) if product.discount_price else None,
        'discount': product.discount_percentage,
        'image': product.image_url,
        'state': product.state_origin,
        'rating': str(product.rating),
        'reviews': product.review_count,
        'in_stock': product.in_stock,
        'category': product.category.name,
        'tags': product.tag_list,
        'in_wishlist': in_wishlist,
        'url': f'/products/{product.slug}/',
    }
    return JsonResponse(data)


# ─── Recently Viewed ──────────────────────────────────────────────────────────

def track_recently_viewed(request, product_id):
    """Store recently viewed product IDs in session."""
    viewed = request.session.get('recently_viewed', [])
    if product_id in viewed:
        viewed.remove(product_id)
    viewed.insert(0, product_id)
    request.session['recently_viewed'] = viewed[:10]  # keep last 10
    return JsonResponse({'ok': True})


def recently_viewed_products(request):
    ids = request.session.get('recently_viewed', [])
    products = []
    if ids:
        prod_map = {p.id: p for p in Product.objects.filter(id__in=ids, is_active=True)}
        for pid in ids:
            if pid in prod_map:
                p = prod_map[pid]
                products.append({
                    'id': p.id,
                    'name': p.name,
                    'slug': p.slug,
                    'price': str(p.effective_price),
                    'image': p.image_url,
                    'rating': str(p.rating),
                    'category': p.category.name,
                })
    return JsonResponse({'products': products})


# ─── Coupon Code ──────────────────────────────────────────────────────────────

VALID_COUPONS = {
    'WELCOME10': 10,
    'DESI20': 20,
    'INDIA15': 15,
    'FIRST50': 50,
    'FESTIVE25': 25,
}

@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    if not code:
        return JsonResponse({'valid': False, 'message': 'Please enter a coupon code.'})
    discount_pct = VALID_COUPONS.get(code)
    if discount_pct:
        request.session['coupon_code'] = code
        request.session['coupon_discount'] = discount_pct
        return JsonResponse({
            'valid': True,
            'code': code,
            'discount': discount_pct,
            'message': f'✅ Coupon applied! {discount_pct}% off your order.',
        })
    else:
        request.session.pop('coupon_code', None)
        request.session.pop('coupon_discount', None)
        return JsonResponse({'valid': False, 'message': '❌ Invalid or expired coupon code. Try WELCOME10, DESI20 or INDIA15.'})


def remove_coupon(request):
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    return JsonResponse({'ok': True})


# ─── Compare Products ─────────────────────────────────────────────────────────

def add_to_compare(request, product_id):
    compare = request.session.get('compare_list', [])
    if product_id not in compare:
        if len(compare) >= 3:
            return JsonResponse({'ok': False, 'message': 'You can compare up to 3 products.'})
        compare.append(product_id)
    else:
        compare.remove(product_id)
    request.session['compare_list'] = compare
    return JsonResponse({'ok': True, 'count': len(compare), 'ids': compare})


def compare_products(request):
    ids = request.session.get('compare_list', [])
    products = list(Product.objects.filter(id__in=ids, is_active=True).select_related('category'))
    context = {'products': products}
    return render(request, 'store/compare.html', context)


# ─── Deals & Offers ───────────────────────────────────────────────────────────

def deals(request):
    """Dedicated deals page showing all discounted products."""
    sort = request.GET.get('sort', 'newest')
    category_slug = request.GET.get('category')

    products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False,
    ).select_related('category')

    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Sort options — fixed key names to match frontend values
    sort_map = {
        'discount': '-rating',       # highest rated deals first
        'price_low': 'discount_price',
        'price_high': '-discount_price',
        'rating': '-rating',
        'newest': '-created_at',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    categories = Category.objects.all()
    paginator = Paginator(products, 24)
    page = paginator.get_page(request.GET.get('page'))

    # Stats
    total_savings = sum(
        (p.price - p.discount_price) for p in products if p.discount_price
    )

    context = {
        'page_obj': page,
        'categories': categories,
        'current_category': category_slug,
        'total_savings': total_savings,
        'deals_count': products.count(),
    }
    return render(request, 'store/deals.html', context)


# ─── Artisan Stories ──────────────────────────────────────────────────────────

ARTISAN_STORIES = [
    {
        'name': 'Ramesh Kumar',
        'craft': 'Blue Pottery',
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=400',
        'story': 'For over 30 years, Ramesh has been keeping the ancient art of Jaipur Blue Pottery alive in his small workshop. His turquoise glazed bowls and vases are recognized worldwide.',
        'products': 12,
        'rating': 4.8,
        'since': '1994',
    },
    {
        'name': 'Meena Devi',
        'craft': 'Madhubani Painting',
        'state': 'Bihar',
        'image': 'https://images.unsplash.com/photo-1594736797933-d0501ba2fe65?w=400',
        'story': 'Meena learned Madhubani painting from her grandmother at age 8. Today she runs a cooperative of 25 women artists from Mithila, bringing centuries-old folk art to global markets.',
        'products': 28,
        'rating': 4.9,
        'since': '2005',
    },
    {
        'name': 'Arjun Singh',
        'craft': 'Organic Spices',
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400',
        'story': 'Arjun farms 12 acres of certified organic spice gardens in Wayanad. No pesticides, no chemicals — just Kerala\'s rich soil and traditional wisdom passed through generations.',
        'products': 35,
        'rating': 4.7,
        'since': '2010',
    },
    {
        'name': 'Fatima Begum',
        'craft': 'Chikankari Embroidery',
        'state': 'Uttar Pradesh',
        'image': 'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400',
        'story': 'Fatima heads a women\'s self-help group of 80 artisans in Lucknow. The delicate white threadwork on muslin fabric takes days of meticulous handwork for each piece.',
        'products': 19,
        'rating': 4.9,
        'since': '2008',
    },
    {
        'name': 'Suresh Rao',
        'craft': 'Mysore Silk',
        'state': 'Karnataka',
        'image': 'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400',
        'story': 'With 40 years of silk weaving mastery, Suresh produces GI-tagged Mysore Silk sarees on traditional power looms. Each saree takes 3-7 days to complete.',
        'products': 22,
        'rating': 4.8,
        'since': '1985',
    },
    {
        'name': 'Tribal Collective',
        'craft': 'Warli Art',
        'state': 'Maharashtra',
        'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400',
        'story': 'A collective of 60 Warli tribal artists from Palghar district who paint their ancestral geometric patterns on handmade paper and fabric, depicting life, nature and rituals.',
        'products': 41,
        'rating': 4.6,
        'since': '2012',
    },
]

def artisan_stories(request):
    context = {
        'artisans': ARTISAN_STORIES,
        'total_artisans': 500,
        'states_covered': 28,
        'products_created': 5000,
    }
    return render(request, 'store/artisan_stories.html', context)


# ─── Sitemap XML ──────────────────────────────────────────────────────────────

from django.http import HttpResponse
from django.utils import timezone

def sitemap_xml(request):
    products = Product.objects.filter(is_active=True).values('slug', 'updated_at')
    categories = Category.objects.all().values('slug')

    base = request.build_absolute_uri('/')[:-1]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # Static pages
    static_urls = ['', '/products/', '/about/', '/contact/', '/faq/',
                   '/deals/', '/artisans/', '/privacy/', '/terms/', '/returns/']
    for url in static_urls:
        xml += f'  <url><loc>{base}{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'

    # Product pages
    for p in products:
        xml += f'  <url><loc>{base}/products/{p["slug"]}/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>\n'

    # Category pages
    for c in categories:
        xml += f'  <url><loc>{base}/products/?category={c["slug"]}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'

    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def robots_txt(request):
    base = request.build_absolute_uri('/')
    content = f"""User-agent: *
Disallow: /admin/
Disallow: /checkout/
Disallow: /cart/
Disallow: /orders/
Disallow: /profile/
Disallow: /api/
Allow: /

Sitemap: {base}sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')


# ─── Product API (for HTML SPA integration) ───────────────────────────────────

def api_products(request):
    """JSON product listing API for SPA integration."""
    products = Product.objects.filter(is_active=True).select_related('category')

    # Filters
    category_slug = request.GET.get('category')
    q = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', 'newest')
    featured = request.GET.get('featured')
    trending = request.GET.get('trending')
    limit = int(request.GET.get('limit', 20))
    page_num = int(request.GET.get('page', 1))

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q) |
            Q(tags__icontains=q) | Q(state_origin__icontains=q)
        )
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if featured:
        products = products.filter(is_featured=True)
    if trending:
        products = products.filter(is_trending=True)

    sort_map = {
        'newest': '-created_at', 'price_low': 'price', 'price_high': '-price',
        'rating': '-rating', 'name': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, limit)
    page = paginator.get_page(page_num)

    data = {
        'count': paginator.count,
        'pages': paginator.num_pages,
        'page': page_num,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'results': [{
            'id': p.id,
            'name': p.name,
            'slug': p.slug,
            'category': p.category.name,
            'category_slug': p.category.slug,
            'price': str(p.price),
            'discount_price': str(p.discount_price) if p.discount_price else None,
            'effective_price': str(p.effective_price),
            'discount_percentage': p.discount_percentage,
            'image': p.image_url,
            'state': p.state_origin,
            'rating': str(p.rating),
            'review_count': p.review_count,
            'is_featured': p.is_featured,
            'is_trending': p.is_trending,
            'in_stock': p.in_stock,
            'tags': p.tag_list,
            'url': f'/products/{p.slug}/',
        } for p in page]
    }
    return JsonResponse(data)


def api_categories(request):
    """JSON categories API for SPA integration."""
    from django.db.models import Count
    cats = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).filter(product_count__gt=0)
    data = [{
        'id': c.id,
        'name': c.name,
        'slug': c.slug,
        'image': c.image_url,
        'count': c.product_count,
    } for c in cats]
    return JsonResponse({'categories': data})
