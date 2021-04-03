from django.contrib import admin
from .models import ProductClass, Product, ProductVariant, \
    SaleSum, SaleQuantity, Organisation, \
    OrderItem, Order, Invoice, SellerOrganisation,\
    Price, OrderStatus, Delivery, ShopConstant, CarouselImage

from super_inlines.admin import SuperInlineModelAdmin, SuperModelAdmin

admin.site.register(ProductClass)
admin.site.register(Organisation)
admin.site.register(SellerOrganisation)
admin.site.register(OrderStatus)


class DeliveryAdmin(SuperModelAdmin):
    list_display = ('minSum', 'price')


class ShopConstantAdmin(SuperModelAdmin):
    list_display = ('name', 'value', 'comment')


class PriceInline(SuperInlineModelAdmin, admin.TabularInline):
    model = Price
    extra = 0


class ProductVariantAdmin(SuperModelAdmin):
    inlines = [PriceInline, ]
    list_display = ('name', 'slug', 'vendorCode', 'quantity', 'available')
    list_filter = ('available', 'product__productClass', 'product',)
    search_fields = ['name', 'slug']


class OrderItemInline(SuperInlineModelAdmin, admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderInline(SuperInlineModelAdmin, admin.StackedInline):
    model = Order
    extra = 0
    inlines = [OrderItemInline, ]


class InvoiceAdmin(SuperModelAdmin):
    inlines = [OrderInline, ]
    list_display = ('pk', 'date', 'getStatus', 'customer', 'toPay')
    list_filter = ('order__status', 'seller', 'customer',)
    search_fields = ['seller__name', 'customer__name']


class ProductVariantInline(SuperInlineModelAdmin, admin.TabularInline):
    model = ProductVariant
    extra = 0


class CarouselImageInline(SuperInlineModelAdmin, admin.TabularInline):
    model = CarouselImage
    extra = 0


class ProductAdmin(SuperModelAdmin):
    inlines = [ProductVariantInline, CarouselImageInline, ]
    list_display = ('pk', 'name', 'slug', 'available')
    list_filter = ('available', 'productClass',)
    search_fields = ['name', 'slug']


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(ShopConstant, ShopConstantAdmin)
