from django.urls import path
from shop.views import ProductsListView, ProductsDetailView, add_item_to_cart, cart_view, CartDeleteItem, make_order, \
    detective_category, fantasy_category, horror_category, adults_category, order_list_increase, order_list_decline, \
    warning_page, blogs_list

urlpatterns = [
    path('', ProductsListView.as_view(), name='shop'),
    path('cart_view/', cart_view, name='cart_view'),
    path('detail/<int:pk>/', ProductsDetailView.as_view(), name='shop_detail'),
    path('add-item-to-cart/<int:pk>', add_item_to_cart, name='add_item_to_cart'),
    path('delete_item/<int:pk>', CartDeleteItem.as_view(), name='cart_delete_item'),
    path('make-order/', make_order, name='make_order'),
    path('detective_category/', detective_category, name='detective_cat'),
    path('fantasy_category/', fantasy_category, name='fantasy_cat'),
    path('horror_category/', horror_category, name='horror_cat'),
    path('adults_category/', adults_category, name='adults_cat'),
    path('increase_price/', order_list_increase, name='inc_price'),
    path('decline_price/', order_list_decline, name='dec_price'),
    path('warning/', warning_page, name='warning_page'),
    path('blog/', blogs_list, name='blog')
]
