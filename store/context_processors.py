from .models import Cart, Wishlist


def cart_and_wishlist(request):
    cart_count = 0
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = cart.item_count
        except Cart.DoesNotExist:
            pass
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist_count = wishlist.products.count()
        except Wishlist.DoesNotExist:
            pass
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }
