from django.urls import path, include
from paypal.standard.ipn import views as paypal_ipn_views
from core import views
from core.views import intro, index, category_list_view, product_list_view, category_product_list_view, \
    product_detail_view, ajax_add_review, add_to_cart, cart_view, delete_item_from_cart, update_cart, checkout_view, \
<<<<<<< HEAD
    payment_completed_view, payment_failed_view, customer_dashboard, order_detail, make_address_default, wishlist_view, \
    add_to_wishlist, remove_wishlist
from core import glass_virtual_tryon
from core.glass_virtual_tryon import test_view
=======
    payment_completed_view, payment_failed_view,glass_try,customer_dashboard
>>>>>>> 43074547d84c9b41f1ef93325009163f0499c7ba

app_name = "core"

urlpatterns = [
    # home
    path("", intro, name="intro"),
    path("home/", index, name="index"),
    # category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category-product-list"),
    # product
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    # vendor
    path("vendors/", views.vendor_list_view, name="vendor-list"),

    # add reviews
    path("ajax-add-review/<int:pid>/", ajax_add_review, name="ajax-add-review"),

    path("add-to-cart/", add_to_cart, name="add-to-cart"),

    path("cart/", cart_view, name="cart"),
    path("delete-form-cart/", delete_item_from_cart, name="delete-form-cart"),
    path("update-cart/", update_cart, name="update-cart"),
    path("checkout/", checkout_view, name="checkout"),
    path("paypal/", paypal_ipn_views.ipn, name="paypal-ipn"),
    #payment succc
    path("payment-completed/",payment_completed_view, name="payment-completed"),
    #payment fail
    path("payment-failed/",payment_failed_view, name="payment-failed"),
<<<<<<< HEAD
    path("test/",test_view, name="test"),
    path("dashboard/",customer_dashboard, name="dashboard"),
    path("dashboard/order/<int:id>",order_detail, name="order-detail"),
    path("make-default-address/",make_address_default, name="make-default-address"),
    path("wishlist/",wishlist_view, name="wishlist"),
    path("add-to-wishlist/",add_to_wishlist, name="add-to-wishlist"),
    path("remove-from-wishlist/",remove_wishlist, name="remove-from-wishlist"),

=======
    path("glass_try/", glass_try, name="glass_try"),
    # dashboard
    path("dashboard/", customer_dashboard, name="dashboard"),
>>>>>>> 43074547d84c9b41f1ef93325009163f0499c7ba

]

