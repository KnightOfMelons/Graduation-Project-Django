from django.urls import path
from shop.views import ProductsListView, ProductsDetailView, add_item_to_cart, cart_view, CartDeleteItem, make_order, \
    detective_category, fantasy_category, horror_category, adults_category, order_list_increase, order_list_decline, \
    warning_page, blogs_list, BlogsDetailView, history_page, poetry_category, drama_category, history_category, \
    comedy_category, search_result, search, add_to_favorite, favorite

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
    path('poetry_category/', poetry_category, name='poetry_cat'),
    path('drama_category/', drama_category, name='drama_cat'),
    path('history_category/', history_category, name='history_cat'),
    path('comedy_category/', comedy_category, name='comedy_cat'),

    path('increase_price/', order_list_increase, name='inc_price'),
    path('decline_price/', order_list_decline, name='dec_price'),

    path('warning/', warning_page, name='warning_page'),
    path('blog/', blogs_list, name='blog'),
    path('blog-detail/<int:pk>/', BlogsDetailView.as_view(), name='blog-detail'),
    path('history/', history_page, name='history_orders'),

    path('search_page/', search, name='search_page'),
    path('search_result/', search_result, name='search_result'),

    path('add_to_favorite/<int:product_id>', add_to_favorite, name='add_to_favorite'),
    path('favorite_page/', favorite, name='favorite_page'),
]
