
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import qrcode

from store.models import ExceptionRecord, OrderItem

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_order_email_to_customer(data):
    try:
        order = data['order']

        image_path = f'images/qr/{order.id}.jpg'

        qr_code_data = {
            'id' : str(order.id),
            'name' : str(order.name),
            'phone' : str(order.phone),
            'address' : str(order.address),
            'email' : str(data['email']),
        }
        qr_code = qrcode.make(qr_code_data)
        qr_code.save(f'media/{image_path}')

        order.qr_image = image_path
        order.save()

        img_mail_path = f'{settings.BACKEND_SERVER_URL}/media/{image_path}'
        all_order_items = OrderItem.objects.filter(order=order)
        html_template = render_to_string('email/order_confirmation.html', 
            {
                'email' : data['email'], 
                'qrcode' : img_mail_path, 
                'created_at' : order.created_at, 
                'payment_method' : 'Card',
                'address' : order.address,
                'reservation_fee' : 'AED 20',
                'deal_options' : all_order_items
            } 
        )

        # {
        #     'name' : 'Deal Name here',
        #     'image' : 'https://deals.tijarah.ae/media/images/qr/3e584112-37ec-4f85-ad28-7a6ed1284722.jpg',
        #     'quantity' : '02'
        # }
        text_template = strip_tags(html_template)
        send_mail = EmailMultiAlternatives(
            'Order Confirmation',
            text_template,
            settings.EMAIL_HOST_USER,
            [data['email']],
        )
        send_mail.attach_alternative(html_template, "text/html")
        send_mail.send(fail_silently=False)
    except Exception as err:
        ExceptionRecord.objects.create(text=str(err))