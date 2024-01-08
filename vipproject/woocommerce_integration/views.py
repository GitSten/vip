# woocommerce_integration/views.py
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseServerError
from django.template.defaultfilters import floatformat
from .utils import get_orders_in_range
import logging
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from .models import Order, Product
from .forms import OrderForm
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)


def send_total_amount_sum_notification(customer_name, total_amount_sum, order_id):
    recipient_emails = settings.NOTIFICATION_EMAILS
    subject = 'UUS VIP KLIENDI TELLIMUS!'
    view_orders_link = 'https://www.ecoshvip.eu/view-orders/'

     # Kontrollib, kas teavitus on juba saadetud
    customer_orders = Order.objects.filter(
        customer_name=customer_name,
        total_amount_sum_notified=False,
        order_status__in=['failed', 'cancelled', 'pending', 'refunded'],
    )

    if customer_orders.exists():
        return

    if not Order.objects.filter(customer_name=customer_name, email_notification_sent=False).exists():
        return

    message = (
        f'Klient {customer_name} on saavutanud VIP staatuse.\n'
        f'Kõikide tellimuste summa kokku: {total_amount_sum:.2f} €\n'
        f'Vip Kliendi keskkond: {view_orders_link}'
    )

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_emails, fail_silently=False)

    # Märkib kliendi tellimused teavitatuks
    Order.objects.filter(customer_name=customer_name, email_notification_sent=False).update(
        total_amount_sum_notified=True,
        email_notification_sent=True
    )


@login_required
def sync_orders(request):
    start_date = datetime(2024, 1, 7)
    end_date = datetime(2025, 12, 31)
    total_amount_threshold = 300

    orders_data = get_orders_in_range(start_date, end_date)

    with transaction.atomic():
        for order_data in orders_data:
            order_id = order_data.get('id')
            customer_name = order_data.get('billing').get('first_name') + ' ' + order_data.get('billing').get(
                'last_name')
            order_date_str = order_data.get('date_created')

            try:
                order_date = datetime.strptime(order_date_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=None)
            except ValueError:
                logger.error(f"Failed to parse order date: {order_date_str}")
                continue

            total_amount = float(order_data.get('total'))

            order_status = order_data.get('status')

            if order_status is None:
                logger.error(f"Order status is missing for order ID: {order_id}")
                return HttpResponseServerError("Failed to fetch order status.")

            order, created = Order.objects.get_or_create(
                order_id=order_id,
                defaults={
                    'customer_name': customer_name,
                    'order_date': order_date,
                    'total_amount': total_amount,
                    'order_status': order_status,
                    'synced': False,
                    'email_notification_sent': False,
                    'total_amount_sum_notified': False,
                }
            )

            if order.synced:
                continue

           # Arvutab tellimuste kogusumma
            total_amount_sum = Order.objects.filter(customer_name=customer_name).aggregate(Sum('total_amount'))[
                'total_amount__sum']

            # Kontrolli, kas uus kogusumma ületab läve
            if (
                    total_amount_sum
                    and total_amount_sum > total_amount_threshold
                    and not Order.objects.filter(customer_name=customer_name, total_amount_sum_notified=True,
                                                 order_id=order_id).exists()
            ):
                # Get the latest order/Saada e-kiri
                latest_order = Order.objects.filter(customer_name=customer_name).latest('order_date')
                send_total_amount_sum_notification(customer_name, total_amount_sum, latest_order.order_id)

                  # Märgib  teavitatuks
                Order.objects.filter(customer_name=customer_name, order_id=latest_order.order_id).update(
                    total_amount_sum_notified=True)

               # Märkige tellimus sünkroniseerituks
                order.synced = True
                order.save()

    return render(request, 'sync_complete.html')


def calculate_orders_by_customer():
    # Hangi unikaalsete klientide nimede loend
    customer_names = Order.objects.values_list('customer_name', flat=True).distinct()

  # Looge loend tellimuste hoidmiseks iga kliendi jaoks
    orders_by_customer = []

    for customer_name in customer_names:
        # Get orders for the current customer, excluding canceled orders
        customer_orders = Order.objects.filter(
            customer_name=customer_name
        ).exclude(order_status__in=['cancelled', 'failed', 'pending',
                                    'refunded'])  # filtreerib tühistatud ja ebaõnnestunud tellimused välja

        # Calculate the total amount for the customer
        total_amount_sum = customer_orders.aggregate(Sum('total_amount'))['total_amount__sum']

        # Add the customer's orders and total amount to the list
        orders_by_customer.append({
            'customer_name': customer_name,
            'customer_orders': customer_orders,
            'total_amount_sum': total_amount_sum,
        })

    return orders_by_customer


@login_required
def view_orders(request):
    # Fetch all orders ordered by the latest order date
    orders = Order.objects.exclude(order_status__in=['cancelled', 'failed', 'pending', 'refunded']).order_by('-order_date')

    # Create a set to store unique customer names
    unique_customer_names = set()

    # Create a list to store orders for each customer
    orders_by_customer = []

    for order in orders:
        # Check if the customer name is already processed
        if order.customer_name not in unique_customer_names:
            # Get all orders for the current customer
            customer_orders = orders.filter(customer_name=order.customer_name)

            # Calculate the total amount for the customer
            total_amount_sum = customer_orders.aggregate(Sum('total_amount'))['total_amount__sum']

            # Add the customer's orders and total amount to the list
            orders_by_customer.append({
                'customer_name': order.customer_name,
                'customer_orders': customer_orders,
                'total_amount_sum': total_amount_sum,
            })

            # Add the customer name to the set
            unique_customer_names.add(order.customer_name)

    # Filtreerib tellimused, mille kogusumma on alla 300
    orders_by_customer = [customer_data for customer_data in orders_by_customer if
                          customer_data['total_amount_sum'] and customer_data[
                              'total_amount_sum'] >= 300]

    # Lehekülje kood
    paginator = Paginator(orders_by_customer, 50)  # Set the number of orders per page
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    return render(request, 'view_orders.html', {'orders_by_customer': orders})

# merch
@login_required()
def update_gift(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            # Redirect back to the 'view_orders' page
            return redirect('view_orders')
    else:
        form = OrderForm(instance=order)

    products = Product.objects.all()  # Retrieve all products
    return render(request, 'update_gift.html', {'form': form, 'order': order, 'products': products})


def update_order_statuses(request):
   # Värskendage olemasolevate töötlemistellimuste olekut lõpetatuks
    Order.objects.filter(order_status='processing').update(order_status='completed')

    return JsonResponse({'message': 'Tellimuste olekute värskendamine õnnestus.'})


def index(request):
    return render(request, 'index.html')


class IndexView(LoginRequiredMixin, View):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        # Your view logic goes here
        return render(request, self.template_name, context={'user': request.user})


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(reverse('index'))

def handler404(request, unknown_path):
    return render(request, 'error/404.html', {'unknown_path': unknown_path}, status=404)


