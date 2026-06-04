from django.contrib import admin
from .models import (Category, Product, Review, Cart, CartItem,
                     Wishlist, Order, OrderItem, ContactMessage, NewsletterSubscriber)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'rating',
                    'is_featured', 'is_trending', 'is_active']
    list_filter = ['category', 'is_featured', 'is_trending', 'is_active', 'state_origin']
    search_fields = ['name', 'description', 'state_origin', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'discount_price', 'stock', 'is_featured', 'is_trending', 'is_active']
    list_per_page = 25
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'category', 'short_description', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'discount_price', 'stock')
        }),
        ('Images', {
            'fields': ('image_url', 'image_url_2', 'image_url_3')
        }),
        ('Details', {
            'fields': ('state_origin', 'tags', 'rating', 'review_count')
        }),
        ('Flags', {
            'fields': ('is_featured', 'is_trending', 'is_active')
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__username']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'item_count', 'total', 'updated_at']
    inlines = [CartItemInline]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    filter_horizontal = ['products']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_method',
                    'total_amount', 'city', 'state', 'created_at']
    list_filter = ['status', 'payment_method', 'state']
    search_fields = ['order_number', 'user__username', 'full_name', 'phone']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['order_number', 'created_at']
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'total_amount')
        }),
        ('Delivery Address', {
            'fields': ('full_name', 'email', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'pincode')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    list_editable = ['is_read']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    search_fields = ['email']


# Admin site customization
admin.site.site_header = "DesiBazaar Admin Panel"
admin.site.site_title = "DesiBazaar Admin"
admin.site.index_title = "Welcome to DesiBazaar Management Portal"
