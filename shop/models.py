from _decimal import Decimal
from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('F', 'Fantasy'),
        ('D', 'Detective'),
        ('H', 'Horror'),
        ('A', 'Adults'),
    )
    name = models.CharField(max_length=255, verbose_name='product_name')
    code = models.CharField(max_length=255, verbose_name='product_code')  # Уникальный код продукта
    price = models.DecimalField(max_digits=20, decimal_places=2)
    unit = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['pk']
        # это значит, что элементы будут отображаться по времени их созданию

    def __str__(self):
        return f'{self.name}'

    def get_all_by_FANTASY(self):
        fantasy_cat = Product.objects.filter(category='F')
        return fantasy_cat

    def get_all_by_DETECTIVE(self):
        detective_cat = Product.objects.filter(category='D')
        return detective_cat

    def get_all_by_HORROR(self):
        horror_cat = Product.objects.filter(category='H')
        return horror_cat

    def get_all_by_ADULTS(self):
        adults_cat = Product.objects.filter(category='A')
        return adults_cat

    def get_by_increase_price(self):
        increase = Product.objects.all().order_by('price')
        return increase

    def get_by_decline_price(self):
        decline = Product.objects.all().order_by('-price')
        return decline


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # on_delete - если удаляем пользователя, то и удаляем
    # все платежи
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    # decimal_places - после запятой может быть 2 знака
    # blank=True поле может быть пустым, не обязателен ввод
    time = models.DateTimeField(auto_now_add=True)  # Автоматчески время устанавливается
    comment = models.TextField(blank=True, null=True)  # поле может быть пустым и не обязательным

    class Meta:
        ordering = ['pk']
        # это значит, что элементы будут отображаться по времени их созданию

    def __str__(self):
        return f'{self.user} | {self.amount}'

    @staticmethod
    def get_balance(user: User):
        amount = Payment.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)


class Order(models.Model):
    STATUS_CART = '1_cart'
    STATUS_WAITING_FOR_PAYMENT = '2_waiting_for_payment'
    STATUS_PAID = '3_paid'
    STATUS_CHOICES = [
        (STATUS_CART, 'cart'),
        (STATUS_WAITING_FOR_PAYMENT, 'waiting_for_payment'),
        (STATUS_PAID, 'paid')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_CART)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['pk']
        # это значит, что элементы будут отображаться по времени их созданию

    def __str__(self):
        return f'{self.user} | {self.amount} | {self.status}'

    @staticmethod
    def get_cart(user: User):
        cart = Order.objects.filter(user=user,
                                    status=Order.STATUS_CART
                                    ).first()
        if not cart:
            cart = Order.objects.create(user=user,
                                        status=Order.STATUS_CART,
                                        amount=0)
        return cart

    def get_amount(self):
        amount = Decimal(0)
        for item in self.orderitem_set.all():
            amount += item.amount
        return amount

    def make_order(self):
        items = self.orderitem_set.all()
        if items and self.status == Order.STATUS_CART:
            self.status = Order.STATUS_WAITING_FOR_PAYMENT
            self.save()
            auto_payment_unpaid_orders(self.user)

    @staticmethod
    def get_amount_of_unpaid_orders(user: User):
        amount = Order.objects.filter(user=user,
                                      status=Order.STATUS_WAITING_FOR_PAYMENT
                                      ).aggregate(Sum('amount'))['amount__sum']
        return amount or Decimal(0)

    @staticmethod
    def get_history(user: User):
        history = Order.objects.filter(user=user)
        return history


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['pk']
        # это значит, что элементы будут отображаться по времени их созданию

    def __str__(self):
        return f'{self.product} | {self.price}'

    @property
    def amount(self):
        return self.quantity * (self.price - self.discount)


# Автоплатеж неоплачеаемых заказов
# transaction.atomic Декоратор отвечает за то, чтобы всё, что происходило внутри - дошло
# до конца или ничего не должно произойти
@transaction.atomic()
def auto_payment_unpaid_orders(user: User):
    unpaid_orders = Order.objects.filter(user=user,
                                         status=Order.STATUS_WAITING_FOR_PAYMENT)
    for order in unpaid_orders:
        if Payment.get_balance(user) < order.amount:
            break
        order.payment = Payment.objects.all().last()
        order.status = Order.STATUS_PAID
        order.save()
        Payment.objects.create(user=user,
                               amount=-order.amount)


# Эти позволяют отражать любые изменению по заказу, которые влияют на сумму (пересчитывают OrderItems)
@receiver(post_save, sender=OrderItem)
def recalculate_order_amount_after_save(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_delete, sender=OrderItem)
def recalculate_order_amount_after_delete(sender, instance, **kwargs):
    order = instance.order
    order.amount = order.get_amount()
    order.save()


@receiver(post_save, sender=Payment)
def auto_payment(sender, instance, **kwargs):
    user = instance.user
    auto_payment_unpaid_orders(user)


class Blog(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField(max_length=1860)
    date = models.DateTimeField()

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.title}'
