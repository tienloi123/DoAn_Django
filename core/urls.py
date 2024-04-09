from django.urls import path

from core import views
from core.views import intro, index, category_list_view, product_list_view, category_product_list_view, \
    product_detail_view, ajax_add_review

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
    path("ajax_add_review/<int:pid>/", ajax_add_review, name="ajax_add_review")

]
