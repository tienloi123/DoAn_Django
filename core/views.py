from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from core.models import Product, Category, Vendor, CartOrder, CartOrderItems, ProductImages, ProductReview, wishlist, \
    Address
from core.forms import ProductReviewForm
from django.db.models import Count, Avg


# Create your views here.


def intro(request):
    return render(request, 'core/intro.html')


def index(request):
    products = Product.objects.filter(product_status="published", featured=True)

    context = {
        "products": products
    }

    return render(request, 'core/index.html', context)


def product_list_view(request):
    products = Product.objects.filter(product_status="published")

    context = {
        "products": products
    }

    return render(request, 'core/product-list.html', context)


def category_list_view(request):
    categories = Category.objects.all().annotate(product_count=Count("category"))

    context = {
        "categories": categories
    }
    return render(request, 'core/category-list.html', context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)

    context = {
        "category": category,
        "products": products,
    }
    return render(request, 'core/category-product-list.html', context)


def vendor_list_view(request):
    vendor = Vendor.objects.all()
    context = {
        "vendor": vendor,
    }
    return render(request, "core/vendor-list.html", context)


def products(request):
    return render(request, 'core/product-list.html')


def product_detail_view(request, pid):
    product = Product.objects.get(pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)

    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    review_form = ProductReviewForm()
    make_review = True
    if request.user.is_authenticated:
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()
        if user_review_count > 0:
            make_review = False
    p_image = product.p_images.all()

    context = {
        "p": product,
        "review_form": review_form,
        "p_image": p_image,
        "make_review": make_review,
        "average_rating": average_rating,
        "reviews": reviews,
        "products": products,
    }
    return render(request, "core/product-detail.html", context)


def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review=request.POST['review'],
        rating=request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }
    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
        {
            'bool': True,
            'context': context,
            'avg_reviews': average_reviews
        }
    )
