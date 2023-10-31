from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, DeleteView
from django.http import HttpResponse

from shop.forms import AddQuantityForm
from shop.models import Product, Order, OrderItem, Blog, Favorite

global flag
flag = None
count = 0


# Это для страницы Shop, чтобы вывести все книги
class ProductsListView(ListView):
    model = Product
    template_name = 'shop/shop.html'

    paginate_by = 9


# Это для страницы с Деталями товара
class ProductsDetailView(DetailView):
    model = Product
    template_name = 'shop/shop-details.html'


@login_required(login_url=reverse_lazy('login'))
def add_item_to_cart(request, pk):
    if request.method == 'POST':
        quantity_form = AddQuantityForm(request.POST)
        if quantity_form.is_valid():
            quantity = quantity_form.cleaned_data['quantity']
            if quantity:
                cart = Order.get_cart(request.user)
                product = get_object_or_404(Product, pk=pk)
                cart.orderitem_set.create(product=product,
                                          quantity=quantity,
                                          price=product.price)
                cart.save()
                return redirect('cart_view')
        else:
            pass
    return redirect('shop')


@login_required(login_url=reverse_lazy('login'))
def cart_view(request):
    cart = Order.get_cart(request.user)
    items = cart.orderitem_set.all()
    context = {
        'cart': cart,
        'items': items,
    }
    return render(request, 'shop/cart.html', context)


@method_decorator(login_required, name='dispatch')
class CartDeleteItem(DeleteView):
    model = OrderItem
    template_name = 'shop/cart.html'
    success_url = reverse_lazy('cart_view')

    # Проверка доступа
    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(order__user=self.request.user)
        return qs


@login_required(login_url=reverse_lazy('login'))
def make_order(request):
    cart = Order.get_cart(request.user)
    cart.make_order()
    return redirect('shop')


def detective_category(request):
    category = Product.get_all_by_DETECTIVE(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/detective_cat.html', context)


def fantasy_category(request):
    category = Product.get_all_by_FANTASY(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/fantasy_cat.html', context)


def horror_category(request):
    category = Product.get_all_by_HORROR(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/horror_cat.html', context)


def adults_category(request):
    if flag:
        category = Product.get_all_by_ADULTS(request.user)
        context = {
            'category': category,
        }
        return render(request, 'shop/categories/adults_cat.html', context)
    else:
        return HttpResponse('Access is denied')


def poetry_category(request):
    category = Product.get_all_by_POETRY(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/poetry_cat.html', context)


def drama_category(request):
    category = Product.get_all_by_DRAMA(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/drama_cat.html', context)


def history_category(request):
    category = Product.get_all_by_HISTORY(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/history_cat.html', context)


def comedy_category(request):
    category = Product.get_all_by_COMEDY(request.user)
    context = {
        'category': category,
    }
    return render(request, 'shop/categories/comedy_cat.html', context)


# СОРТИРОВКА ПО ЦЕНЕ
def order_list_increase(request):
    category = Product.get_by_increase_price(request.user)
    context = {
        'category': category
    }
    return render(request, 'shop/categories/increase_price_page.html', context)


def order_list_decline(request):
    category = Product.get_by_decline_price(request.user)
    context = {
        'category': category
    }
    return render(request, 'shop/categories/decline_price.html', context)


def warning_page(request):
    global count
    if count == 0:
        global flag
        flag = True
        count += 1
        return render(request, 'warning_page.html')
    else:
        return adults_category(request)


def blogs_list(request):
    blogs = Blog.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request, 'blog/blog.html', context)


class BlogsDetailView(DetailView):
    model = Blog
    template_name = 'blog/blog_detail.html'


@login_required(login_url=reverse_lazy('login'))
def history_page(request):
    history = Order.get_history(request.user)
    context = {
        'history': history,
    }
    return render(request, 'shop/history.html', context)


def search(request):
    return render(request, 'shop/search/search_page.html')


def search_result(request):
    query = request.GET.get('query')
    products = Product.objects.filter(name__icontains=query)
    context = {'products': products}
    return render(request, 'shop/search/search.html', context)


@login_required(login_url=reverse_lazy('login'))
def add_to_favorite(request, product_id):
    product = Product.objects.get(id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    return redirect('favorite_page')


def favorite(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'shop/favorites.html', {'favorites': favorites})


def remove_from_favorite(request, pk):
    favorite = Favorite.objects.get(user=request.user, product=pk)
    favorite.delete()
    return redirect('favorite_page')