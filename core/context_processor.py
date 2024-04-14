from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist_model, Address
from django.contrib import messages
def default(request):
    categories = Category.objects.all()

    try:
        wishlist = wishlist_model.objects.filter(user=request.user)
    except:
        messages.warning(request, "You need to login before accessing your wishlist")
        wishlist = 0

    try:
        address = Address.objects.filter(user=request.user)
    except:
        address = None

    return {
        'categories':categories,
        'wishlist':wishlist,
        'address':address,

    }