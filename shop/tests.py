from _decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase

from shop.models import Product, Payment, OrderItem, Order


class TestDataBase(TestCase):
    fixtures = [
        "shop/fixtures/mydata.json"
    ]

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.p = Product.objects.all().first()

    def test_user_exists(self):  # Находим базового пользователя
        users = User.objects.all()
        users_number = users.count()
        user = users.first()
        self.assertEqual(users_number, 1)
        self.assertEqual(user.username, 'admin')
        self.assertTrue(user.is_superuser)

    def test_user_check_password(self):  # Сравниваем его пароль
        self.assertTrue(self.user.check_password('123456'))

    def test_all_data(self):  # Проверяем, что во всех базах находится больше одного значения
        self.assertGreater(Product.objects.all().count(), 0)
        self.assertGreater(Order.objects.all().count(), 0)
        self.assertGreater(OrderItem.objects.all().count(), 0)
        self.assertGreater(Payment.objects.all().count(), 0)

    def find_cart_number(self):  # Подсчитывает количество корзин для конкретного пользователя (user)
        cart_number = Order.objects.filter(user=self.user,
                                           status=Order.STATUS_CART
                                           ).count()
        return cart_number

    def test_function_get_cart(self):
        # Проверяем число корзин (Вариант 1 - Корзины ещё нет, 2 - корзина уже создана,3 - получить созданную корзину)
        pass
        # 1 - No carts
        self.assertEqual(self.find_cart_number(), 0)

        # 2 - Create cart
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)

        # 3 - Get created cart
        Order.get_cart(self.user)
        self.assertEqual(self.find_cart_number(), 1)

    def test_recalculate_order_amount_after_changing_orderitem(self):
        # 1 - Сначала получаем сомму до любых изменений
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(0))
        # 2 - Потом после добавления элементов
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        i = OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=3)
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(10))

        # 3 - После удаления элементов
        i.delete()
        cart = Order.get_cart(self.user)
        self.assertEqual(cart.amount, Decimal(4))

    def test_cart_status_changing_after_applying_make_order(self):
        # Корзина должна менять свой статус и превращаться в ЗАКАЗ
        # 1 - Меняем статус для пустой корзины
        cart = Order.get_cart(self.user)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_CART)

        # 2 - Не для пустой корзины
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        cart.make_order()
        self.assertEqual(cart.status, Order.STATUS_WAITING_FOR_PAYMENT)

    def test_method_get_amount_of_unpaid_orders(self):
        # Получаем общую сумму неоплачеваемых заказов
        # 1 - Перед созданием корзины
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(13556))

        # 2 - После создания корзины
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(13556))

        # 3 - После создания корзины и применения cart.make_order()
        cart.make_order()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(13560))

        # 4 - После оплаты заказа
        cart.status = Order.STATUS_PAID
        cart.save()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(13556))

        # 5 - После удаления всех заказов
        Order.objects.all().delete()
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))

    def test_method_get_balance(self):
        # Тестируем метод получения баланса по счёту пользователя
        # 1 - Получаем сумму до оплаты
        amount = Payment.get_balance(self.user)
        self.assertEqual(amount, Decimal(13000))

        # 2 - После добавления платежа
        Payment.objects.create(user=self.user, amount=100)
        amount = Payment.get_balance(self.user)
        self.assertEqual(amount, Decimal(13100))

        # 3 После добавления нескольких платежей
        Payment.objects.create(user=self.user, amount=-50)
        amount = Payment.get_balance(self.user)
        self.assertEqual(amount, Decimal(13050))

        # 4 Никаких платежей
        Payment.objects.all().delete()
        amount = Payment.get_balance(self.user)
        self.assertEqual(amount, Decimal(0))

    # Проверка баланса и смена заказа на оплаченный
    def test_auto_payment_after_apply_make_order_true(self):
        Order.objects.all().delete()
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=2)
        self.assertEqual(Payment.get_balance(self.user), Decimal(13000))
        cart.make_order()
        self.assertEqual(Payment.get_balance(self.user), Decimal(12996))

    def test_auto_payment_after_apply_make_order_false(self):
        Order.objects.all().delete()
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=50000)
        cart.make_order()
        self.assertEqual(Payment.get_balance(self.user), Decimal(13000))

    def test_auto_payment_after_add_required_payment(self):
        Payment.objects.create(user=self.user, amount=556)
        self.assertEqual(Payment.get_balance(self.user), Decimal(0))
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))

    # def test_auto_payment_for_earlier_order(self):
    #     cart = Order.get_cart(self.user)
    #     OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=500)
    #     Payment.objects.create(user=self.user, amount=1000)
    #     self.assertEqual(Payment.get_balance(self.user), Decimal(444))
    #     amount = Order.get_amount_of_unpaid_orders(self.user)
    #     self.assertEqual(amount, Decimal(1000))

    def test_auto_payment_for_all_orders(self):
        cart = Order.get_cart(self.user)
        OrderItem.objects.create(order=cart, product=self.p, price=2, quantity=500)
        Payment.objects.create(user=self.user, amount=10000)
        self.assertEqual(Payment.get_balance(self.user), Decimal(9444))
        amount = Order.get_amount_of_unpaid_orders(self.user)
        self.assertEqual(amount, Decimal(0))