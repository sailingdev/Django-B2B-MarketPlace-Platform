from .models import *
from django import template
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.validators import validate_email
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, HttpResponse, redirect
from django.template.loader import get_template
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from io import BytesIO, StringIO
from django.core.mail import send_mail
from django.template.loader import render_to_string
from num2words import num2words
import json
import pdfkit
import shop.forms
import account.forms
import account.views
import xlrd

# methods returning JSON or string/int/decimal


def getItems(request):
    if request.method == 'POST':
        res = {}
        for item in ProductVariant.objects.all():
            obj = {}
            obj['name'] = item.name
            obj['slug'] = item.slug
            obj['measure'] = item.product.measure
            obj['quantity'] = item.quantity
            obj['multiplicity'] = item.multiplicity
            res[item.slug] = obj
        return HttpResponse(json.dumps(res))
    return HttpResponse('error')


def getItemArray(request):
    if request.method == 'POST':
        res = []
        for item in ProductVariant.objects.all():
            res.append(item.slug)
        return HttpResponse(json.dumps(res))
    return HttpResponse('error')


def getItemPrices(request):
    if request.method == 'POST':
        res = {}
        for item in ProductVariant.objects.all():
            prices = {}
            for price in item.price_set.all():
                prices[int(price.quantity)] = float(price.price)
            res[item.slug] = prices
        return HttpResponse(json.dumps(res))
    return HttpResponse('error')


def getItemStored(request):
    if (request.method == 'POST'):
        res = {}
        for item in ProductVariant.objects.all():
            res[item.slug] = item.quantity
        return HttpResponse(json.dumps(res))
    return HttpResponse('error')


def getCart(request):
    res = {}
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps(res))

        cart = Order.objects.get_or_create(
            user=request.user,
            status=OrderStatus.objects.get(pk=1)
        )[0]

        cart.delZeroes()

        for item in cart.items.all():
            res[item.product.slug] = item.quantity
        return HttpResponse(json.dumps(res))

    return HttpResponse('error')


def addToCart(request):
    if request.method == 'POST':
        if 'item' in request.POST \
                and 'quantity' in request.POST \
                and request.POST['quantity'].isdigit():
            pItem = request.POST['item']
            pQuantity = int(request.POST['quantity'])
            if not request.user.is_authenticated:
                return HttpResponse('not authenticated')
            else:
                cart = Order.objects.filter(
                    user=request.user, status=OrderStatus.objects.get(pk=1))
                if len(cart) == 0:
                    cart = Order.objects.create(
                        user=request.user,
                        status=OrderStatus.objects.get(pk=1)
                    )
                else:
                    cart = cart[0]
                item = get_object_or_404(ProductVariant.objects, slug=pItem)
                if (cart.getQuantity(item) + pQuantity) % item.multiplicity != 0:
                    return HttpResponse('must be divisible by multiplicity')
                # if (item.quantity < cart.getQuantity(item) + pQuantity):
                #    return HttpResponse('stored quantity is too small')
                cart.setQuantity(item, cart.getQuantity(item) + pQuantity)
                cart.delZeroes()
                return HttpResponse('ok')
        else:
            return HttpResponse('error')
    else:
        return HttpResponse('error')


def setInCart(request):
    if request.method == 'POST':
        if 'item' in request.POST \
                and 'quantity' in request.POST \
                and request.POST['quantity'].isdigit():
            pItem = request.POST['item']
            pQuantity = int(request.POST['quantity'])
            if not request.user.is_authenticated:
                return HttpResponse('not authenticated')
            else:
                cart = Order.objects.filter(
                    user=request.user, status=OrderStatus.objects.get(pk=1))
                if len(cart) == 0:
                    cart = Order.objects.create(
                        user=request.user,
                        status=OrderStatus.objects.get(pk=1)
                    )
                else:
                    cart = cart[0]
                item = get_object_or_404(ProductVariant.objects, slug=pItem)

                if pQuantity % item.multiplicity != 0:
                    return HttpResponse('must be divisible by multiplicity')

                # if (item.quantity < pQuantity):
                #    return HttpResponse('stored quantity is too small')
                cart.setQuantity(item, pQuantity)
                cart.delZeroes()
                return HttpResponse('ok')
        else:
            return HttpResponse('error')
    else:
        return HttpResponse('error')


def getCartSum(request):
    if not request.user.is_authenticated:
        return HttpResponse(0)
    cart = Order.objects.filter(
        user=request.user, status=OrderStatus.objects.get(pk=1))
    if len(cart) == 0:
        return HttpResponse(0)
    cart = cart[0]
    cart.delZeroes()
    return HttpResponse(cart.getTotalSum())


def getDelivery(request):
    if not request.user.is_authenticated:
        return HttpResponse('0')
    cart = Order.objects.get_or_create(
        user=request.user,
        status=OrderStatus.objects.get(pk=1)
    )[0]
    cart.delZeroes()
    return HttpResponse(cart.getDelivery())


def getTotal(request):
    if not request.user.is_authenticated:
        return HttpResponse('0')
    cart = Order.objects.get_or_create(
        user=request.user,
        status=OrderStatus.objects.get(pk=1)
    )[0]
    cart.delZeroes()
    return HttpResponse(cart.getDelivery() + cart.getTotalSum())


def getStored(request):
    pass


def getItemQuantityInCart(request):
    if request.method == 'POST':
        if 'item' in request.POST:
            pItem = request.POST['item']
            if not request.user.is_authenticated:
                return HttpResponse('not authenticated')
            else:
                cart = Order.objects.filter(
                    user=request.user,
                    status=OrderStatus.objects.get(pk=1)
                )
                if len(cart) == 0:
                    cart = Order.objects.create(
                        user=request.user,
                        status=OrderStatus.objects.get(pk=1)
                    )
                else:
                    cart = cart[0]
                cart.delZeroes()
                item = get_object_or_404(ProductVariant.objects, slug=pItem)
                return HttpResponse(cart.getQuantity(item))
        else:
            return HttpResponse('error')
    else:
        return HttpResponse('error')


def getMinOrderSum(request):
    return HttpResponse(ShopConstant.getMinOrderSum())

# ----------- Views (HTML/PDF)


def orderList(request):
    if not request.user.is_authenticated:
        return redirect('/itemlist')
    invoices = Invoice.objects.filter(
        order__user=request.user).order_by('-date')
    return render(request, 'shop/orderlist.html', {'invoices': invoices})


def getInvoicePdf(request):
    invoice = get_object_or_404(Invoice.objects, pk=request.GET['pk'])
    if request.user.is_superuser or request.user == invoice.order.user:
        invoice_html = get_template('shop/invoice.html').render(
            {
                'invoice': invoice,
                'sumInWords': num2words(invoice.toPay(),
                                        lang='ru',
                                        to='currency',
                                        currency='RUB',
                                        seperator=' ',
                                        cents=False
                                        ).capitalize(),
            })
        pdf = pdfkit.from_string(invoice_html, False, options={'quiet': ''})

        return HttpResponse(pdf, content_type='application/pdf')
    return redirect('/')
    # return HttpResponse('You have not access to this invoice')


def getInvoice(request):
    invoice = get_object_or_404(Invoice.objects, pk=request.GET['pk'])
    if request.user.is_superuser or request.user == invoice.order.user:
        return render(request, 'shop/invoice.html',
                      {
                          'invoice': invoice,
                          'sumInWords': num2words(invoice.toPay(),
                                                  lang='ru',
                                                  to='currency',
                                                  currency='RUB',
                                                  seperator=' ',
                                                  cents=False
                                                  ).capitalize(),
                      })
    return redirect('/')
    # return HttpResponse('You have not access to this invoice')


def cart(request):
    if not request.user.is_authenticated:
        return redirect('/itemlist')
    cart = Order.objects.filter(
        user=request.user, status=OrderStatus.objects.get(pk=1))
    if len(cart) == 0:
        cart = Order.objects.create(
            user=request.user, status=OrderStatus.objects.get(pk=1))
    else:
        cart = cart[0]
    cart.delZeroes()
    return render(request, 'shop/cart.html',
                  {
                      'cart': cart,
                      'Delivery': Delivery.objects.all()
                  }
                  )


def makeOrder(request):
    if not request.user.is_authenticated:
        return redirect('/itemlist')
    if request.method == 'GET':
        cart = Order.objects.filter(
            user=request.user, status=OrderStatus.objects.get(pk=1))
        if len(cart) == 0:
            cart = Order.objects.create(
                user=request.user, status=OrderStatus.objects.get(pk=1))
        else:
            cart = cart[0]
        cart.delZeroes()
        if not cart.checkOrder():
            return redirect('/order/')
            # return HttpResponse('total sum is too low')
        return render(request, 'shop/customerinfo.html',
                      {
                          'cart': cart,
                          'DADATA_API_KEY': settings.DADATA_API_KEY,
                          'total': (cart.getDelivery() + cart.getTotalSum())
                      }
                      )

    inn = ''
    kpp = ''
    name = ''
    address = ''
    shipAddress = ''
    comment = ''
    face = ''
    facePhone = ''
    personRecipient = ''
    personRecipientPhone = ''

    try:
        inn = request.POST['inn']
        kpp = request.POST['kpp']
        name = request.POST['name']
        address = request.POST['address']
        comment = request.POST['comments']
        shipAddress = request.POST['shipping_address']
        face = request.POST['face']
        facePhone = request.POST['facePhone']
        personRecipient = request.POST['personRecipient']
        personRecipientPhone = request.POST['personRecipientPhone']
    except:
        cart = Order.objects.get_or_create(
            user=request.user,
            status=OrderStatus.objects.get(pk=1)
        )[0]
        return render(request, 'shop/customerinfo.html',
                      {
                          'cart': cart,
                          'errors': 'Ошибка',
                          'DADATA_API_KEY': settings.DADATA_API_KEY
                      }
                      )

    org = Organisation.objects.get_or_create(
        inn=inn,
        kpp=kpp,
        address=address,
        name=name
    )[0]
    cart = Order.objects.get_or_create(
        user=request.user,
        status=OrderStatus.objects.get(pk=1)
    )[0]
    cart.delZeroes()

    if not cart.checkOrder():
        return redirect('/order/')
        # return HttpResponse('total sum is too low')

    if request.user not in org.owners.all():
        org.owners.add(request.user)

    invoice = Invoice.objects.create(
        date=timezone.now(),
        seller=SellerOrganisation.objects.get(pk=1),
        customer=org,
        # order=cart,
        personInCharge=face,
        personInChargePhone=facePhone,
        personRecipient=personRecipient,
        personRecipientPhone=personRecipientPhone,
        comment=comment,
        shipAddress=shipAddress
    )
    cart.invoice = invoice

    for item in cart.items.all():
        item.product.quantity = item.product.quantity - item.quantity
        item.product.save()

    cart.activate()
    invoice.recalc()
    return redirect('/endoforder?pk=' + str(invoice.pk))


def itemList(request):
    productClasses = ProductClass.objects.all()
    return render(request, 'shop/itemList.html',
                  {
                      'productClasses': productClasses,
                      'cls': 'all',
                      'curitem': '',
                  })


def itemListSelection(request, cls):
    productClasses = ProductClass.objects.all()
    cls = str(cls)
    if len(productClasses.filter(slug=cls)) == 0:
        return redirect('/')
        raise Http404('there are no such tag: ' + cls)
    return render(request, 'shop/itemList.html',
                  {
                      'productClasses': productClasses,
                      'cls': cls,
                      'curitem': '',
                  })


def endOfOrder(request):
    if not request.user.is_authenticated:
        return redirect('/itemlist')
    if 'pk' not in request.GET:
        return HttpResponse('error')
    pk = request.GET['pk']

    _invoice = get_object_or_404(Invoice.objects, pk=request.GET['pk'])
    if not _invoice.sent and (request.user.is_superuser or request.user == _invoice.order.user):
        subject = render_to_string(
            "shop/email/order_subject.txt",
            {'current_site': get_current_site(request)}
        )
        subject = "".join(subject.splitlines())
        message = render_to_string(
            "shop/email/order.txt",
            {'current_site': get_current_site(request)}
        )
        html_message = render_to_string(
            "shop/email/order.html",
            {'current_site': get_current_site(request)}
        )

        msg = EmailMultiAlternatives(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email, ]
        )
        msg.attach_alternative(html_message, "text/html")
        # msg.content_subtype = "html"

        _invoice_html = get_template('shop/invoice.html').render(
            {
                'invoice': _invoice,
                'sumInWords': num2words(_invoice.toPay(),
                                        lang='ru',
                                        to='currency',
                                        currency='RUB',
                                        seperator=' ',
                                        cents=False
                                        ).capitalize()
            })
        _pdf = pdfkit.from_string(_invoice_html, False, options={'quiet': ''})
        msg.attach('invoice.pdf', _pdf, 'application/pdf')
        msg.send()
        _invoice.sent = True
        _invoice.save()
    # else:
        # return redirect('/')
        # return HttpResponse('ERROR')

    showNotification = False

    #item = get_object_or_404(ProductVariant.objects, slug=pItem)
    for item in _invoice.order.items.all():
        if item.quantity > item.product.quantity:
            showNotification = True

    return render(request, 'shop/endoforder.html', {'pk': pk, 'notification': showNotification})


def itemPage(request, itemSlug):
    item = get_object_or_404(Product.objects, slug=itemSlug)
    if not item.available:
        # HttpResponse('Product ' + item.slug + ' is not available now.')
        return redirect('/')
    productClasses = ProductClass.objects.all()
    return render(request, 'shop/itemList.html',
                  {
                      'productClasses': productClasses,
                      'cls': 'all',
                      'curitem': itemSlug,
                  })
    # return render(request, 'shop/itemPage.html', {'item': item})


def about(request):
    return render(request, 'shop/about.html', {})

# auth


class LoginView(account.views.LoginView):
    form_class = account.forms.LoginEmailForm


class SignupView(account.views.SignupView):
    form_class = shop.forms.SignupForm

    def generate_username(self, form):
        username = form.cleaned_data["email"]
        return username

    def after_signup(self, form):
        super(SignupView, self).after_signup(form)

# admin


def adminUploadQuantities(request):
    if not request.user.is_superuser:
        return HttpResponse('###')

    if request.method == 'POST':
        form = shop.forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            updated, errors = updateQuantitiesXls(
                'files/quantity/' + request.FILES['file'].name)

            return render(request, 'admin/admin-update-quantities.html',
                          {
                              'updated': updated,
                              'errors': errors
                          }
                          )
    else:
        form = shop.forms.UploadFileForm()
    return render(request, 'admin/admin-update-quantities.html',
                  {
                      'form': form
                  }
                  )


def handle_uploaded_file(f):
    with open('files/quantity/' + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
