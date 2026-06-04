from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('search/', views.search_results, name='search_results'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Profile
    path('profile/', views.profile, name='profile'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('returns/', views.returns, name='returns'),

    # Newsletter
    path('newsletter/', views.newsletter_subscribe, name='newsletter'),

    # Review
    path('review/<int:product_id>/', views.submit_review, name='submit_review'),

    # ── NEW ENHANCEMENTS ──────────────────────────────────────────────────────
    # Search autocomplete (AJAX)
    path('api/search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),

    # Quick View (AJAX)
    path('api/quick-view/<int:product_id>/', views.quick_view, name='quick_view'),

    # Recently Viewed
    path('api/track-viewed/<int:product_id>/', views.track_recently_viewed, name='track_recently_viewed'),
    path('api/recently-viewed/', views.recently_viewed_products, name='recently_viewed_products'),

    # Coupon
    path('api/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('api/coupon/remove/', views.remove_coupon, name='remove_coupon'),

    # Compare
    path('api/compare/<int:product_id>/', views.add_to_compare, name='add_to_compare'),
    path('compare/', views.compare_products, name='compare_products'),

    # ── DEALS & ARTISAN PAGES ─────────────────────────────────────────────────
    path('deals/', views.deals, name='deals'),
    path('artisans/', views.artisan_stories, name='artisan_stories'),

    # ── SEO ───────────────────────────────────────────────────────────────────
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', views.robots_txt, name='robots_txt'),

    # ── PRODUCT JSON API (for SPA integration) ───────────────────────────────
    path('api/products/', views.api_products, name='api_products'),
    path('api/categories/', views.api_categories, name='api_categories'),
]
