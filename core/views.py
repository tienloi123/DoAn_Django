from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from core.models import Product, Category, Vendor, CartOrder, ProductImages, ProductReview, wishlist_model, \
    Address, CartOrderItems
from core.forms import ProductReviewForm
from django.db.models import Count, Avg
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import cv2
import numpy as np
from django.core import serializers


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
            'average_reviews': average_reviews
        }
    )
def add_to_cart(request):
    cart_product = {}

    cart_product[str(request.GET['id'])] = {
        'title': request.GET['title'],
        'qty': request.GET['qty'],
        'price': request.GET['price'],
        'image': request.GET['image'],
        'pid': request.GET['pid'],
    }
    if 'cart_data_obj' in request.session:
        if str(request.GET['id']) in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = int(cart_product[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cart_data_obj'] = cart_data
        else:
            cart_data = request.session['cart_data_obj']
            cart_data.update(cart_product)
            request.session['cart_data_obj'] = cart_data
    else:
        request.session['cart_data_obj'] = cart_product
    return JsonResponse({"data":request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj'])})

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
                cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {"cart_data":request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    else:
        messages.warning(request, "Giỏ hàng trống")
        return redirect("core:index")

def delete_item_from_cart(request):
    product_id = str(request.GET['id'])
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del request.session['cart_data_obj'][product_id]
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems':len(request.session['cart_data_obj'])})

def update_cart(request):
    product_id = str(request.GET['id'])
    product_qty = request.GET['qty']

    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[str(request.GET['id'])]['qty'] = product_qty
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {"cart_data":request.session['cart_data_obj'],'totalcartitems':len(request.session['cart_data_obj']), 'cart_total_amount': cart_total_amount})
    return JsonResponse({"data": context, 'totalcartitems':len(request.session['cart_data_obj'])})

def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0

    if 'cart_data_obj' in request.session:
        # Tính tổng số tiền cho đơn hàng
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])

        # Tạo đơn hàng mới và lưu vào cơ sở dữ liệu
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount
        )

        # Lưu thông tin sản phẩm trong giỏ hàng vào cơ sở dữ liệu
        for p_id, item in request.session['cart_data_obj'].items():
            cart_order_products = CartOrderItems.objects.create(
                order=order,
                invoice_no="INVOICE_NO" + str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty']) * float(item['price'])
            )

        # Xóa giỏ hàng sau khi đã đặt hàng thành công
        # del request.session['cart_data_obj']

    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_amount,
        'item_name': "Order-Item-No-" + str(order.id),
        'invoice': "INVOICE_NO-" + str(order.id),
        'currency_code': "USD",
        'notify_url': 'http://{}{}'.format(host, reverse("core:paypal-ipn")),
        'return_url': 'http://{}{}'.format(host, reverse("core:payment-completed")),
        'cancel_url': 'http://{}{}'.format(host, reverse("core:payment-failed")),
    }
    paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
    try:
        active_address = Address.objects.get(user=request.user, status=True)
    except:
        messages.warning(request, "There are multiple address, only one should be ACTIVATED.")
        active_address = None
    return render(request, "core/checkout.html", {
        "cart_data": request.session.get('cart_data_obj', {}),
        'totalcartitems': len(request.session.get('cart_data_obj', {})),
        'cart_total_amount': cart_total_amount,
        'paypal_payment_button': paypal_payment_button,
        "active_address":active_address
    })

def payment_completed_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
    return render(request, "core/payment-completed.html", {"cart_data": request.session['cart_data_obj'],
                                                  'totalcartitems': len(request.session['cart_data_obj']),
                                                  'cart_total_amount': cart_total_amount})


def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')


def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)

    if request.method == "POST":
        address = request.POST.get("address")
        mobile = request.POST.get("mobile")

        new_address = Address.objects.create(
            user = request.user,
            address = address,
            mobile = mobile,
        )
        messages.success(request, "Address Added Successfully")
        return redirect("core:dashboard")
    context = {
        "orders": orders,
        "address": address,
    }
    return render(request, 'core/dashboard.html', context)
def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user,id = id)
    order_items = CartOrderItems.objects.filter(order = order)

    context = {
        "order_items": order_items,
    }
    return render(request, 'core/order-detail.html',context)

def make_address_default(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean": True})


def add_to_wishlist(request):
    product_id = request.GET['id']
    product = Product.objects.get(id=product_id)
    print("product id issssssssss:" + product_id)

    context = {}
    wishlist_count = wishlist_model.objects.filter(product=product, user = request.user).count()
    print(wishlist_count)

    if wishlist_count>0:
        context = {
            "bool": True
        }
    else:
        new_wishlist = wishlist_model.objects.create(
            user=request.user,
            product = product,
        )
        context = {
            "bool": True
        }
    return JsonResponse(context)
def wishlist_view(request):
    try:
        wishlist = wishlist_model.objects.all()
    except:
        wishlist=None

    context = {
        "w":wishlist
    }
    return render(request, "core/wishlist.html", context)

def remove_wishlist(request):
    try:
        pid = request.GET['id']
        wishlist = wishlist_model.objects.filter(user=request.user)
        product = wishlist_model.objects.get(id=pid)
        product.delete()

        # Serialize wishlist queryset to JSON
        wishlist_json = serializers.serialize('json', wishlist)

        # Render wishlist HTML asynchronously
        wishlist_html = render_to_string("core/async/wishlist-list.html", {"w": wishlist})

        # Return JSON response with updated wishlist HTML and JSON data
        return JsonResponse({"data": wishlist_html, "w": wishlist_json})
    except Exception as e:
        return JsonResponse({"error": str(e)})