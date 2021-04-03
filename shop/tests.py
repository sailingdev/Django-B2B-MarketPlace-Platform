from django.test import TestCase
from shop.models import *
from django.contrib.auth.models import User, Group


class OrderTest(TestCase):
    def setUp(self):
        ProductClass.objects.create(name='коробка', slug='box')
        ProductClass.objects.create(name='шнур', slug='cord')
        Product.objects.create(name='коробка 10x10x10', slug='box10x10x10')
        Product.objects.create(name='шнур 10см', slug='cord_10cm')
        ProductVariant.objects.create(name='коробка 10x10x10 черная',
                                      addition='черная',
                                      slug='box10black',
                                      product=Product.objects.get(pk=1),
                                      price=Decimal('10'))
        ProductVariant.objects.create(name='шнур 10см жёлтый',
                                      addition='жёлтый',
                                      slug='cord10yellow',
                                      product=Product.objects.get(pk=2),
                                      price=Decimal('1'))

        Organisation.objects.create(inn='1234567890')
        User.objects.create(username='1@test.com',
                            email='1@test.com', password='password')
        User.objects.create(username='2@test.com',
                            email='2@test.com', password='password')
        Group.objects.create(name='const customers')
        User.objects.get(pk=1).groups.add(Group.objects.get(pk=1))

        Order.objects.create(organisation=Organisation.objects.get(
            pk=1), user=User.objects.get(pk=1))
        OrderItem.objects.create(product=ProductVariant.objects.get(
            pk=1), price=ProductVariant.objects.get(pk=1).price)
        Order.objects.get(pk=1).items.add(OrderItem.objects.get(pk=1))

    def test1(self):
        box, cord = ProductVariant.objects.all()
        order = Order.objects.all()[0]
        self.assertEqual(order.getQuantity(box), 0)
        self.assertEqual(order.getQuantity(cord), 0)
        order.setQuantity(box, 10)
        self.assertEqual(order.getQuantity(box), 10)
        self.assertEqual(order.getQuantity(cord), 0)
        order.setQuantity(cord, 4324)
        self.assertEqual(order.getQuantity(box), 10)
        self.assertEqual(order.getQuantity(cord), 4324)
        order.activate()
        order.finish()
        order.cancel()
        self.assertEqual(order.getTotalQuantity(), 4334)
        self.assertEqual(order.getTotalSum(), 4424)
