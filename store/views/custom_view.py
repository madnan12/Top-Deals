from django.urls.base import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from ast import Store
from multiprocessing import context
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from audioop import reverse
import email
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from store.forms import *
from django.contrib.auth import authenticate, login as dj_login, logout
from django.http import HttpResponseRedirect
import random, string
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from store.models import *
from store.utils import Utill
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.utils.html import strip_tags
from django.http import JsonResponse
from store.serializer import CitySerializer
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.db.models import  Q
from store.serializer import *
from rest_framework.response import Response
import datetime
import json
from datetime import date
import geocoder
from django.contrib import messages
from store.filters import *
from django.contrib.auth.decorators import user_passes_test
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from threading import Thread
from store.threads import *
import time

from Constants.Location import get_user_current_location
from Constants.Decorators import LocationRedirection



def view_email(request):
    path = request.GET.get('path', None)
    if path is not None:
        context = {
            'email' : 'dummy@gmail.com', 
            'qrcode' : 'https://deals.tijarah.ae/media/images/qr/3e584112-37ec-4f85-ad28-7a6ed1284722.jpg',
            'created_at' : 'Nov. 04, 2022, 1:07 PM',
            'payment_method' : 'Cash',
            'address' : 'Lahore',
            'reservation_fee' : 'AED 20',
            'deal_options' : [
                {
                    'name' : 'Deal Name here',
                    'image' : 'https://deals.tijarah.ae/media/images/qr/3e584112-37ec-4f85-ad28-7a6ed1284722.jpg',
                    'quantity' : '02'
                },
                {
                    'name' : 'Deal Name here2',
                    'image' : 'https://deals.tijarah.ae/media/images/qr/3e584112-37ec-4f85-ad28-7a6ed1284722.jpg',
                    'quantity' : '05'
                },
            ]
        }
        return render(request, path, context)
    
    return HttpResponse('please add path with path query')

@csrf_exempt
@LocationRedirection
def home(request, country_code=None):
    context = {}
    get_sub_category = SubCategory.objects.filter(status='Active')
    context['get_sub_category'] = get_sub_category
    if request.user.is_authenticated and request.user.is_superuser:
        # return redirect("admin_category")
        pass
    elif request.user.is_authenticated and request.user.user_type=="Business" and request.user.business_status == 'Approved':
        # return redirect('create_store')
        pass
    else:
        pass
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     ip_addr = x_forwarded_for.split(',')[0]
    # else:
    #     ip_addr = request.META.get('REMOTE_ADDR')
    #
    # #Get current user IP Address and Country
    # ipp = geocoder.ip('37.111.129.13')
    # lang = ipp.latlng
    # Latitude = lang[0]
    # Longitude = lang[1]
    # geolocator = Nominatim(user_agent="geoapiExercises")
    # location = geolocator.reverse(str(Latitude) + "," + str(Longitude))
    # address = location.raw['address']
    # country_from_ip = address.get('country', '')

    # # Get Deals Latitude and longitude and match country with current IP address
    # get_all_deals = BusinessDeal.objects.all()
    # new_deal_list = []
    # for deal in get_all_deals:
    #     address = location.raw['address']
    #     location = geolocator.reverse(str(deal.lat) + "," + str(deal.lon))
    #     country = address.get('country', '')
    #     if country == country_from_ip:
    #         new_deal_list.append(deal)

    user_type = request.POST.get('user_type')
    # form = NormalUserForm(request.POST)
    # form = BusinessUserForm(request.POST, request.FILES)



    if user_type == 'Customer':
        form = NormalUserForm(request.POST)
        email = form['email'].value().strip()
        if email:
            user = User.objects.filter(email=email).first()
            if user:
                user_exc = {
                    'type' : 'REGISTER',
                    'form_type' : 'EVERYONE',
                    'message' : 'User with this email already exists!'
                }
                messages.error(request, "User with this email already exists!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=EVERYONE&auth_type=REGISTER&error=TRUE')
        else:
            messages.error(request, "Please Enter Email!")
            return redirect('/')
        password = form['password'].value()
        country = request.POST.get('country')
        city = request.POST.get('city')
        dial_code = request.POST.get('dial_code')
        # adress = request.POST.get('adress')

        confirm_password = form['confirm_password'].value()
        username = email.split('@')[0]
        if request.method == 'POST':
            try:
                request.POST._mutable = True
            except:
                pass
            request.POST['username'] = username
            form = NormalUserForm(request.POST)
            if password != confirm_password:
                user_exc = {
                    'type' : 'REGISTER',
                    'form_type' : 'EVERYONE',
                    'message' : 'Your password does not match!'
                }
                messages.error(request, "Your password does not match!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=EVERYONE&auth_type=REGISTER&error=TRUE')
            if len(password) < 8:
                user_exc = {
                    'type' : 'REGISTER',
                    'form_type' : 'EVERYONE',
                    'message' : 'Your password length must be greater than 8!'
                }
                messages.error(request, "Your password length must be greater than 8!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=EVERYONE&auth_type=REGISTER&error=TRUE')
            if form.is_valid():
                user = form.save()
                user.set_password(request.POST['password'])
                user.is_active = False
                user.dial_code = dial_code
                user.country_id = country
                user.city_id = city
                # user.business_address = adress
                user.save()
                random_digits_for_code = ''.join(
                    random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                verification = VerificationCode.objects.create(code=random_digits_for_code,user=user)

                # html_template = render_to_string('email/u-forgot-password.html',
                #                                  {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
                # text_template = strip_tags(html_template)
                # send_email = EmailMultiAlternatives(
                #     'Top-Deals | Verification Code',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [email]
                # )
                # send_email.attach_alternative(html_template, "text/html")


                # try:
                #     context = {}
                #     context['verification_code'] = verification.code
                #     context['username'] = user.username
                #     html_template = render_to_string('email/verification-code.html', context)
                #     text_template = strip_tags(html_template)
                #     email = EmailMultiAlternatives(
                #         'Your Top Deals Deal Sign Up Email',
                #         text_template,
                #         settings.EMAIL_HOST_USER,
                #         [user.email],
                #     )
                #     email.attach_alternative(html_template, "text/html")
                #     email.send(fail_silently=False)
                #     # body = "Your Top Deal Email Varification code is " + str(verification.code)
                #     # data = {
                #     #     'subject': "Your Top Deal Sign Up Email",
                #     #     'body': body,
                #     #     'to_email': user.email
                #     # }
                #     # Utill.send_email(data)
                # except Exception as e:
                user.username = username
                user.user_type = 'Customer'
                user.is_active = False
                user.save()
                verification.user = user
                verification.save()

                try:
                    thrd = Thread(target=send_otp_to_email, kwargs={'user' : user, 'verification_code': verification.code})
                    thrd.start()
                except:
                    pass
                return redirect(f'verify_email/{user.id}')
            else:
                form = NormalUserForm(request.POST)

    elif user_type == 'Business':
        if request.method == 'POST':
            form = BusinessUserForm(request.POST, request.FILES)
            email = form['email'].value().strip()
            if email:
                user = User.objects.filter(email=email).first()
                if user:
                    user_exc = {
                        'type' : 'REGISTER',
                        'form_type' : 'BUSINESS',
                        'message' : 'Your password length must be greater than 8!'
                    }
                    messages.error(request, "User with this email already exists!", extra_tags=user_exc)
            else:
                messages.error(request, "Please Enter Email!")
                return redirect('/?popup=TRUE&form_type=BUSINESS&auth_type=REGISTER&error=TRUE')
            username = email.split('@')[0]
            password = form['password'].value()
            subcategory = request.POST.get('subcategory')
            dial_code = request.POST.get('dial_code')
            confirm_password = form['confirm_password'].value()
            license_document = request.FILES.get('license_document')
            city = request.POST.get('city')
            if password != confirm_password:
                user_exc = {
                    'type' : 'REGISTER',
                    'form_type' : 'BUSINESS',
                    'message' : 'Your password does not match!'
                }
                messages.error(request, "Your password does not match!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=BUSINESS&auth_type=REGISTER&error=TRUE')
            if city:
                try:
                    city = City.objects.get(id=city)
                except:
                    city = None
            form = BusinessUserForm(request.POST, request.FILES)
            try:
                request.POST._mutable = True
            except:
                pass
            request.POST['username'] = username
            if len(password) < 8:
                user_exc = {
                    'type' : 'REGISTER',
                    'form_type' : 'BUSINESS',
                    'message' : 'Your password length must be greater than 8!'
                }
                messages.error(request, "Your password length must be greater than 8!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=BUSINESS&auth_type=REGISTER&error=TRUE')
            if form.is_valid():
                user = form.save()
                user.set_password(request.POST['password'])
                user.is_active = False
                user.subcategory_id = subcategory
                user.dial_code = dial_code
                user.save()
                
                default_store = BusinessStore.objects.create(user = user,
                                                            name= user.name,
                                                            category= user.category,
                                                            status= False,
                                                            store_status='Pending',
                                                            country= user.country,
                                                            phone= user.phone,
                                                            license_id= user.license_id,
                                                            license_document= user.license_document,
                                                            )
                default_store.subcategory.add(user.subcategory)
                location = StoreLocation.objects.create(business_store=default_store, adress=user.business_address, city=user.city)


                random_digits_for_code = ''.join(
                    random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                verification = VerificationCode.objects.create(code=random_digits_for_code)
                # html_template = render_to_string('email/verification-code.html',
                #                                  {'verification_code': verification.code, 'img_link': settings.DOMAIN_NAME})
                # text_template = strip_tags(html_template)
                # # Getting Email ready
                # send_email = EmailMultiAlternatives(
                #     'Top-Deals | Verification Code',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [email]
                # )
                # send_email.attach_alternative(html_template, "text/html")
                # send_email.send(fail_silently=False)
                
                try:
                    thrd = Thread(target=send_otp_to_email, kwargs={'user' : user, 'verification_code': verification.code})
                    thrd.start()
                except:
                    pass

                # try:
                #     context = {}
                #     context['verification_code'] = verification.code
                #     context['username'] = user.username
                #     html_template = render_to_string('email/verification-code.html', context)
                #     text_template = strip_tags(html_template)
                #     email = EmailMultiAlternatives(
                #         'OTP Verification | Topdeals',
                #         text_template,
                #         settings.EMAIL_HOST_USER,
                #         [user.email],
                #     )
                #     email.attach_alternative(html_template, "text/html")
                #     email.send(fail_silently=False)
                #     # body = "Your Top Deal Email Varification code is " + str(verification.code)
                #     # data = {
                #     #     'subject': "Your Top Deal Sign Up Email",
                #     #     'body': body,
                #     #     'to_email': user.email
                #     # }
                #     # Utill.send_email(data)
                # except Exception as e:
                user.username = username
                user.user_type = 'Business'
                user.is_active = False
                user.business_approved = False
                user.business_status = "Pending"
                user.save()
                verification.user = user
                verification.save()
                user.username = username
                user.user_type = 'Business'
                user.city = city
                user.license_document = license_document
                user.is_active = False
                user.save()
                verification.user = user
                verification.save()
                return redirect(f'verify_email/{user.id}')

        else:
            form = BusinessUserForm(request.POST)

    elif user_type == 'login':
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            try:
                user = User.objects.get(email=email)
                if user.is_active is False:
                    user_exc = {
                        'type' : 'LOGIN',
                        'form_type' : 'EVERYONE',
                        'message' : 'Your email already register but not verified yet. Please verify your email by entring code sent to your email!'
                    }
                    messages.warning(request, "Your email already register but not verified yet. Please verify your email by code sent to your email!", extra_tags=user_exc)
                    return redirect(f'resend_code_reg_user/{user.email}')
                    # return redirect('')
            except Exception as e:
                user_exc = {
                    'type' : 'LOGIN',
                    'form_type' : 'EVERYONE',
                    'message' : 'User with this email doesn"t exist!'
                }
                messages.error(request, "User with this email doesn't exist!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=EVERYONE&auth_type=LOGIN&error=TRUE')
            user = authenticate(request, username=user.username, password=password)

            # Check if authentication successful
            if user is not None:
                dj_login(request, user)
                try:
                    token = Token.objects.get(user=user)
                except Token.DoesNotExist:
                    token = Token.objects.create(user=user)
                    messages.success(request, "Login Successfully!")
                if user.user_type == 'Business':
                    messages.success(request, "Login Successfully!")
                    return redirect('create_store')
                messages.success(request, "Login Successfully!")
                return redirect('home')
            else:
                user_exc = {
                    'type' : 'LOGIN',
                    'form_type' : 'EVERYONE',
                    'message' : 'Invalid Credentials!'
                }
                messages.error(request, "Invalid Credentials!", extra_tags=user_exc)
                return redirect('/?popup=TRUE&form_type=EVERYONE&auth_type=LOGIN&error=TRUE')
        return render(request, 'Store/home.html', context = context)



    location_data = get_user_current_location(request)
    city = location_data.get('city', '')

    if country_code is None:
        country_code = location_data['country_code']
        

    current_date = date.today()

    # if country_name is not None and city is not None:
    #     deals_of_the_day = BusinessDeal.objects.filter(
    #         start_date__date=current_date,
    #         category__status = 'Active', 
    #         store__city__name__icontains=city,
    #         store__status=True, 
    #         is_expired=False, 
    #         is_deleted=False, 
    #         status=True
    #     )
    #     special_discount_of_the_day = BusinessDeal.objects.filter(
    #         # start_date__date=current_date, 
    #         is_expired=False, 
    #         status=True, 
    #         store__city__name__icontains=city,
    #         is_deleted=False, 
    #         category__status = 'Active', 
    #         store__status=True
    #     ).order_by('-discount_price')[:3]
    # else:
    #     deals_of_the_day = BusinessDeal.objects.filter(
    #         start_date__date=current_date,
    #         category__status = 'Active', 
    #         store__status=True, 
    #         is_expired=False, 
    #         is_deleted=False, 
    #         status=True
    #     )

    #     special_discount_of_the_day = BusinessDeal.objects.filter(
    #         # start_date__date=current_date, 
    #         is_expired=False, 
    #         status=True, 
    #         is_deleted=False, 
    #         category__status = 'Active', 
    #         store__status=True
    #     ).order_by('-discount_price')[:3]

    banners = Banner.objects.filter(status=True).all()
    try:
        city = City.objects.get(name__icontains=city)
    except:
        city = None
    if city and city is not None:
        top_offers = BusinessDeal.objects.filter(
            store__country__country_code__iexact=country_code,
            store__category__status='Active', 
            store__status=True, 
            status=True, 
            is_expired=False,
            is_deleted=False,
            # store__city=city
        )
    else:
        top_offers = BusinessDeal.objects.filter(
            # store__country__country_code__iexact=country_code,
            store__category__status='Active',
            store__status=True,
            status=True,
            is_expired=False,
            is_deleted=False,
        )

    # context['form'] = form
    context['user_type'] = user_type
    # context['deals_of_the_day'] = deals_of_the_day
    # context['special_discount_of_the_day'] = special_discount_of_the_day
    context['top_offers'] = top_offers
    context['banners'] = banners
    context['location_data'] = location_data


    if len(top_offers) > 0 :
        context['nearby_deals'] = top_offers[0:3]
    else:
        context['nearby_deals'] = top_offers


    return render(request, 'Store/home.html', context)



def test(request):
    return render(request,"Admin/test.html")

def customers(request):
    return render(request,"Admin/customers.html")

def invoices(request):
    return render(request,"Admin/invoices.html")


def orders(request):
    return render(request,"Store/orders.html")

def credits(request):
    return render(request,"Store/credits.html")

def redeem_rewards(request):
    return render(request,"Store/redeem-rewards.html")

def business_signup(request):
    return render(request,"Store/business-signup.html")


@login_required(login_url='admin_login')
def account_officer(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    
    assign_store = list(Account_Officer.objects.all().values_list('business_store__id', flat=True))
    officer_store = BusinessStore.objects.filter(id__in=assign_store, status=True)
    
    all_stores = BusinessStore.objects.filter(is_account_officer=False, status=True)
    item = request.GET.get('item')
    if item:
        fullname = Account_Officer.objects.filter(account_officer_name__icontains=item)
        status = Account_Officer.objects.filter(account_officer_status__icontains=item)
        store = Account_Officer.objects.filter(business_store__name__icontains=item)
        city = Account_Officer.objects.filter(business_store__city__name__icontains=item)
        country = Account_Officer.objects.filter(business_store__country__name__icontains=item)
        username = Account_Officer.objects.filter(user__username__icontains=item)
        email = Account_Officer.objects.filter(user__email__icontains=item)
        phone = Account_Officer.objects.filter(user__phone__icontains=item)
        searched_officer_records = fullname.union(status,store,city,country,username,email,phone)
        context['searched_officer_records'] = searched_officer_records
        context['all_stores'] = all_stores
    else:
        searched_officer_records = Account_Officer.objects.all()
        context['searched_officer_records'] = searched_officer_records
        context['officer_store'] = officer_store
    context['all_stores'] = all_stores

    return render(request,"Admin/account-officer.html", context)


def add_account_officer(request):
    if request.method  == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        mobile_number = request.POST.get('mobile_number')
        get_business_store = request.POST.getlist('business_store')
        password = request.POST.get('password')
        status = request.POST.get('status')
        image = request.FILES.get('image')
        #First we will save user as a Acount Officer
        save_account_officer_user = User.objects.create_user(username=username,email=email,password=password)
        # Now save AO with user
        
        save_account_officer = Account_Officer.objects.create(
            user = save_account_officer_user,
            account_officer_name = fullname,
            account_officer_status = status,
            image_logo = image,
        )
        for i in get_business_store:
            get_store_id = BusinessStore.objects.get(id=int(i))
            get_store_id.is_account_officer = True
            save_account_officer.business_store.add(get_store_id)
            get_store_id.save()
        save_account_officer.save()
        get_user = User.objects.filter(username=save_account_officer_user).first()
        get_user.phone = mobile_number
        get_user.is_account_officer = True
        get_user.save()
        messages.success(request, "Account Officer Created Successfully!")
        return redirect('account_officer')
    return redirect('account_officer')


def delete_account_officer(request,id):
    get_account_officer = Account_Officer.objects.get(id=id)
    get_account_officer_user = User.objects.get(username=get_account_officer.user)
    get_account_officer_user.delete()
    get_account_officer.delete()
    messages.success(request, "Account Officer Deleted Successfully!")
    return redirect('account_officer')


def edit_account_officer(request, id):
    officer = Account_Officer.objects.get(id=id)
    get_user = User.objects.get(username=officer.user)
    # serialize_now = UserSerializer(get_user).data
    serialize_now = DefaultUserSerializer(get_user).data
    serializer = AccountOfficerSerializer(officer).data
    data = {'serializer':serializer,'serializer_now':serialize_now}
    return JsonResponse(data)


def account_officer_update(request, id):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        username = request.POST.get('username')
        get_business_store = request.POST.getlist('business_store')
        phone = request.POST.get('mobile_number')
        image = request.FILES.get('image')
        password = request.POST.get('password')
        status = request.POST.get('status')
        #Get Store

        get_account_officer = Account_Officer.objects.get(id=id)
        get_account_officer.account_officer_name = fullname
        get_account_officer.account_officer_status = status
        if image:
            get_account_officer.image_logo = image
        for i in get_business_store:
            get_update_store = BusinessStore.objects.get(id=int(i))
            get_account_officer.business_store.add(get_update_store)
        get_account_officer.save()

        # Get User
        get_update_user = User.objects.filter(username=get_account_officer.user).first()
        get_update_user.username = username
        get_update_user.email = email
        get_update_user.phone = phone
        get_update_user.set_password(password)
        get_update_user.save()
        messages.success(request, "Account Officer Updated Successfully!")
        return redirect('account_officer')
    return redirect('account_officer')

@login_required(login_url='admin_login')
def account_officer_detail(request):
    user = request.user
    specific_order_customer = OrderPlaced.objects.all()[:5]
    try:
        get_user = Account_Officer.objects.get(user=user)
    except Exception as e:
        get_user = ''
        print(e)
    # get_usered = Account_Officer.objects.filter(is_account_officer=True,username=request.user)
    context = {}
    context['specific_order_customer'] = specific_order_customer
    context['get_user']  = get_user
    return render(request,"Admin/account-officer-detail.html", context)

def account_officer_reviews(request):
    return render(request,"Admin/account-officer-reviews.html")


# def store_location(request):
#     return render(request,"Store/store-location.html")

def account_officer_complain(request):
    return render(request,"Admin/account-officer-complain.html")

# @login_required(login_url='/')
def cart(request):
    total_price = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_price = sum([(crt_item.option_id.reservation_fee * crt_item.quantity) for crt_item in cart_items])

    else:
        cookies_cart = request.COOKIES.get('cart_items', None)
        if cookies_cart is not None and type(cookies_cart) == str:
            cookies_cart = json.loads(cookies_cart)
            cart_ids = [int(itm) for itm in cookies_cart]
            cart_items = []
            for c_id in cart_ids:
                try:
                    c_deal = DifferentDealData.objects.get(id=c_id)
                except:
                    pass
                else:
                    item_selected_quantity = cookies_cart[f'{c_id}']['quantity']
                    total_price += (c_deal.reservation_fee * int(item_selected_quantity))
                    cart_items.append({
                        'id' : c_id,
                        'quantity' : item_selected_quantity,
                        'price' : c_deal.price,
                        'image' : c_deal.image,
                        'location' : c_deal.location,
                        'option_id' : {'title' : c_deal.title, 'discount_percentage' :  c_deal.discount_percentage},
                        'reservation_fee' : c_deal.reservation_fee
                    })
        else :
            cart_items = []

    # if request.session.get('saved'):
    #     total_amount = 0
    #     discount_amount = 0
    #     for item in request.session.get('saved'):
    #         total_amount += item['orignal_price']
    #         discount_amount += item['discount_price']

    #     return render(request, "Store/add-to-cart.html", {'options': request.session.get('saved'),
    #                                                       'total_amount':total_amount, 'discount_amount':discount_amount})
    if request.user.is_authenticated:
        token = request.user.auth_token
    else:
        token = None
    return render(request,"Store/add-to-cart.html", {'cart_items' : cart_items, 'auth_token' : token , 'total_price' : total_price})


def pay_now(request):
    if request.session.get('saved'):
        email = request.POST.get('email')
        for item in request.session.get('saved'):

            store_id = item['store']
            store = BusinessStore.objects.filter(id=store_id, is_deleted=False).first()
            if store.total_order is None:
                store.total_order=0

            store.total_order += 1
            store.save()
            messages.success(request, "Your order placed successfully.")
        try:
            body = "Your Top Deal Placed Order Email."
            data = {
                'subject': "Your Top Deal Placed Order Email.",
                'body': body,
                'to_email': email
            }
            Utill.send_email(data)
            del request.session['saved']
        except KeyError:
            pass
    else:
        messages.warning(request, "You don't have any item in cart.")

    return redirect('add_to_cart')


def featured_deals(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    if request.method == "GET":
        try:
            item = request.GET.get('item')
            store_name = BusinessDeal.objects.filter(store__name__icontains=item)
            # category_name = BusinessDeal.objects.filter(category__name__icontains=item)
            # country_name = BusinessDeal.objects.filter(country__name__icontains=item)
            # city_name = BusinessDeal.objects.filter(city__name__icontains=item)
            # title = BusinessDeal.objects.filter(title__icontains=item)
            # description = BusinessDeal.objects.filter(description__icontains=item)
            # price = BusinessDeal.objects.filter(price__icontains=item)
            # discount_percentage = BusinessDeal.objects.filter(discount_percentage__icontains=item)
            # gender = BusinessDeal.objects.filter(gender__icontains=item)
            # status = BusinessDeal.objects.filter(status__icontains=item)
            # searched_deals = store_name.union(category_name, country_name, city_name, title, description, price,
            #                                  discount_percentage, gender, status)
            searched_deals = store_name
            context['searched_deals'] = searched_deals
            return render(request, "Business/featured_deals.html", context)
        except Exception as e:
            print(e)
    searched_deals = BusinessDeal.objects.filter(is_deleted=False).all()
    context['searched_deals'] = searched_deals
    return render(request,"Admin/featured_deals.html", context)

def account_officer_order(request):
    specific_order_customer = OrderPlaced.objects.all()

    context = {}
    context['specific_order_customer'] = specific_order_customer
    return render(request,"Admin/account-officer-order.html", context)



def register(request):
    user_type = request.POST.get('user_type')

    if user_type == 'Customer':
        form=NormalUserForm(request.POST)
        email = form['email'].value().strip()
        username = email.split('@')[0]
        if request.method=='POST':
            form=NormalUserForm(request.POST)
            if form.is_valid():
                user=form.save()
                random_digits_for_code = ''.join(
                random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                verification = VerificationCode.objects.create(code=random_digits_for_code)
                # html_template = render_to_string('email/u-forgot-password.html',
                #                                 {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
                # text_template = strip_tags(html_template)
                # # Getting Email ready
                # send_email = EmailMultiAlternatives(
                #     'Top-Deals | Verification Code',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [email]
                # )
                # send_email.attach_alternative(html_template, "text/html")
                try:
                    # send_email.send(fail_silently=False)
                    body = "Your Top Deal Email Varification code is " + str(verification.code)
                    data = {
                        'subject': "Your Top Deal Sign Up Email",
                        'body': body,
                        'to_email': email
                    }
                    Utill.send_email(data)
                except Exception as e:
                    print(e)
                user.set_password(user.password)
                user.username = username
                user.user_type = 'Customer'
                user.save()
                return redirect(f'verify_email/{user.id}')
            else:
                form=NormalUserForm(request.POST)
    else:
        form=BusinessUserForm(request.POST, request.FILES)
        if request.method=='POST':
            email = form['email'].value().strip()
            username = email.split('@')[0]
            license_document = request.FILES.get('license_document')
            city = request.POST.get('city')
            if city:
                try:
                    city = City.objects.get(id=city)
                except:
                    city = None
            form=BusinessUserForm(request.POST, request.FILES)
            if form.is_valid():
                user=form.save()
                random_digits_for_code = ''.join(
                random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
                verification = VerificationCode.objects.create(code=random_digits_for_code)
                # html_template = render_to_string('email/u-forgot-password.html',
                #                                 {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
                # text_template = strip_tags(html_template)
                # # Getting Email ready
                # send_email = EmailMultiAlternatives(
                #     'Top-Deals | Verification Code',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [email]
                # )
                # send_email.attach_alternative(html_template, "text/html")
                try:
                    # send_email.send(fail_silently=False)
                    body = "Your Top Deal Email Varification code is " + str(verification.code)
                    data = {
                        'subject': "Your Top Deal Sign Up Email",
                        'body': body,
                        'to_email': email
                    }
                    Utill.send_email(data)
                except Exception as e:
                    print(e)
                user.set_password(user.password)
                user.username = username
                user.user_type = 'Business'
                user.city = city
                user.license_document = license_document
                user.save()
                return redirect('/verify_email', pk=user.id)
            else:
                form=BusinessUserForm(request.POST)
    context = {
        'form': form,
    }

    return render(request, 'Store/index.html', context)



# def login(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         try:
#             username = User.objects.get(email=email, is_active=True).username
#         except Exception as e:
#             return render(request, 'Store/login.html', {
#                 "message": "User not exist or not active"
#             })

#         user = authenticate(request, username=username, password=password)

#         # Check if authentication successful
#         if user is not None:
#             dj_login(request, user)
#             return HttpResponseRedirect("/")
#         else:
#             return render(request, 'Store/topbar.html', {
#                 "message": "Invalid username or password!"
#             })
#     else:
#         return render(request, 'Store/topbar.html')


def verify_email(request, id):
    try:
        user = User.objects.get(id=id)
    except Exception as e:
        return redirect('/')
    context={}
    if request.method == 'POST':
        num1 = request.POST.get("num1")
        num2 = request.POST.get("num2")
        num3 = request.POST.get("num3")
        num4 = request.POST.get("num4")
        code = str(num1) + str(num2) + str(num3) + str(num4)

        try:
            verified = VerificationCode.objects.get(user=user, code=code, used=False, is_expired=False)
            if user.is_active and verified:
                context['msg'] = "Verifiedemailforpassword"
                context['new_email'] = user.email
                return render(request, "Store/email-verification.html", context)
        except Exception as e:
            context['otp_msg'] = 'You have entered an incorrect OTP'
            context['email'] = user.email
            return render(request,"Store/email-verification.html", context)

        verified.is_expired = False
        verified.used = True
        verified.save()

        user.is_active = True
        user.save()
        try:
            # After verify otp direct login
            dj_login(request, user)
            # Send Email For Welcome.
            # html_template = render_to_string('email/welcome-email.html')
            # text_template = strip_tags(html_template)
            # email = EmailMultiAlternatives(
            #     'Welcome to Top-Deals',
            #     text_template,
            #     settings.EMAIL_HOST_USER,
            #     [user.email],
            # )
            # email.attach_alternative(html_template, "text/html")
            # email.send(fail_silently=False)
            try:
                thrd = Thread(target=send_welcome_email, kwargs={'user' : user})
                thrd.start()
            except:
                pass

            # Send Email For Business Request
            if user.user_type == 'Business':
                # html_template = render_to_string('email/business-request.html', {'user':user.username})           

                # text_template = strip_tags(html_template)
                # email = EmailMultiAlternatives(
                #     'Business Request Submitted',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [user.email],
                # )
                
                # email.attach_alternative(html_template, "text/html")
                # email.send(fail_silently=False)
                try:
                    thrd = Thread(target=send_request_email, kwargs={'user' : user})
                    thrd.start()
                except:
                    pass
                # Send Mail to Admin
                # admin_email = User.objects.filter(is_admin=True).email
                # html_template = render_to_string('email/admin-business-request.html', {'img_link': settings.DOMAIN_NAME,
                #                                                                 'frontend_domain': settings.FRONTEND_SERVER_NAME})

                # text_template = strip_tags(html_template)
                # email = EmailMultiAlternatives(
                #     'Received Business Request',
                #     text_template,
                #     settings.EMAIL_HOST_USER,
                #     [admin_email],
                # )
                # email.attach_alternative(html_template, "text/html")
                # email.send(fail_silently=False)
                
            if user.user_type == 'Business':
                messages.success(request, "Login Successfully!")
                return redirect('create_store')
        except:
            pass
        messages.success(request, "Login Successfully!")
        return  redirect('home')
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    try:
        user = User.objects.get(id=user.id, is_active=True)
    except Exception as e:
        print(e)
    return render(request, 'Store/email-verification.html',{'email':user.email})


def logout_view(request):
    logout(request)
    return redirect("/")


def load_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(state__country__id=country_id).order_by('name')
    return JsonResponse({
        'cities': CitySerializer(cities, many=True).data
    })


def load_categories(request):
    category_id = request.GET.get('category')
    categories = SubCategory.objects.filter(category__id=category_id)
    return JsonResponse({
        'categories': SubcategorySerializer(categories, many=True).data
    })

def load_store_location(request):
    store_id = request.GET.get('store')
    locations = StoreLocation.objects.filter(business_store__id=store_id)
    print('********', locations)
    return JsonResponse({
        'locations': TemplateStoreLocationSerializer(locations, many=True).data
    })

def resend_code(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        msg = request.POST.get('msg', None)
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            messages.error(request, "your email does not exists!")
            return redirect('home')
        codes = VerificationCode.objects.filter(user=user, is_expired=False)
        for i in codes:
            i.is_expired = True
            i.used = True
            i.save()
        random_digits_for_code = ''.join(
            random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
        verification = VerificationCode.objects.create(user=user, code=random_digits_for_code)
        try:
            body = "Your Forget Password Email Varification code is " + str(verification.code)
            data = {
                'subject': "Your Forget Password Email Varification code",
                'body': body,
                'to_email': user.email
            }
            Utill.send_email(data)
        except Exception as e:
            pass
        return redirect(f'/verify_email/{user.id}')
    return render(request, 'Store/home.html')


def change_password(request):
    if request.user:
        old_password = request.data['old_password'] if 'old_password' in request.data else None
        password1 = request.data['password1'] if 'password1' in request.data else None
        password2 = request.data['password2'] if 'password2' in request.data else None
        try:
            user = request.user
        except Exception as e:
            print(e)
        if not old_password or not password1 or not password2:
            print('invalid data!')

        if not user.check_password(old_password):
            print('invalid old password')

        if password1 != password2:
            print('password not match!')

        if not len(password1) < 8:
            user.set_password(password1)
            user.save()
            print('password changed successfully!')
        else:
            print('password should be 8 characters')
    else:
        print('Plz login to change password')


def reset_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2 = request.POST.get('confirm_password')

        if not email or not password2 or not password1:
            messages.error(request, "Passwords are missing!")
            return redirect('home')
        if password1 != password2:
            messages.error(request, "New passwords does not match!")
            return redirect('home')
        try:
            user = User.objects.get(email=email, is_active=True)
        except Exception as e:
            messages.error(request, "Email does not exists or user not active!")
            return redirect('home')
        if not len(password1) < 8:
            user.set_password(password1)
            user.save()
            messages.success(request, "Password has been reset successfully!")
            return redirect('/')
        else:
            messages.error(request, "Passwords length must be greater than 8!")
            return redirect('home')
    return redirect('home')


# @user_passes_test(lambda u: u.is_superuser)
@login_required(login_url='admin_login')
def admin_dashboard(request):
    user = request.user

    orders =  list(OrderItem.objects.all().values_list('deal_option__deal__store__id', flat=True))
    best_store = BusinessStore.objects.filter(id__in=orders)[:4]
    order_deal =  list(OrderItem.objects.all().values_list('deal_option__deal__id', flat=True))
    best_deal = BusinessDeal.objects.filter(id__in=order_deal)[:1]
    category = Category.objects.filter(status='Active')
    request_user = User.objects.filter(is_active=True)

    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    context = {
        'best_store':best_store,
        'category':category,
        'best_deal':best_deal,
        'request_user': request_user,
    }
    return render(request,"Admin/admin-dashboard.html", context)


@login_required(login_url='admin_login')
def admin_category(request):
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    context = {}
    item = request.GET.get('item')
    if item:
        category = SubCategory.objects.filter(category__name__icontains=item)
        subcategoryname = SubCategory.objects.filter(name__icontains=item)
        status = SubCategory.objects.filter(status__icontains=item)
        searched_categories = category.union(subcategoryname,status)
        p_category = Category.objects.filter(name__icontains=item)
        context['searched_categories'] = searched_categories
    else:
        searched_categories = SubCategory.objects.all()
        p_category = Category.objects.all()
        all_deals = BusinessDeal.objects.filter(is_deleted=False).all()
        context['item'] = item
        context['searched_categories'] = searched_categories
        context['all_deals'] = all_deals
    return render(request,"Admin/admin-category.html",context)


def admin_login(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = User.objects.filter(username=username, is_active=True).first()
            if not user:
                messages.warning(request, "Please enter correct username or passwrod!")
                return redirect('admin_login')
            if user:
                if user.is_superuser:
                    user = authenticate(request, username=username, password=password)
                    if not user:
                        messages.warning(request, "Please Enter Correct Email or Passwrod!")
                        return redirect('admin_login')
                    try:
                        token = Token.objects.get(user=user)
                    except Token.DoesNotExist:
                        token = Token.objects.create(user=user)

                    if user is not None:
                        dj_login(request, user)
                        messages.success(request, "Admin Successfully Login!")
                        return redirect("admin_category")
                    else:
                        return redirect('admin_login')
                elif user.is_account_officer:
                    user = authenticate(username=username, password=password)
                    if not user:
                        messages.warning(request, "Please enter correct username or passwrod!")
                    if user is not None:
                        dj_login(request, user)
                        return redirect("account_officer_detail")
                else:
                    return redirect('admin_login')
            else:
                return redirect('admin_login')
        except Exception as e:
             return redirect('admin_login')
    return render(request, 'Admin/signin-admin.html', context={'FormWithCaptcha':FormWithCaptcha})



@login_required(login_url='admin_login')
def admin_business(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    item = request.GET.get('item', None)
    if item is not None:
        # username = User.objects.filter(username__icontains=item)
        # email = User.objects.filter(email__icontains=item)
        # fullname = User.objects.filter(first_name__icontains=item)
        # business_name = User.objects.filter(name__icontains=item)
        # phone = User.objects.filter(phone__icontains=item)
        # country = User.objects.filter(country__name__icontains=item)
        # city = User.objects.filter(city__name__icontains=item)
        # business_address = User.objects.filter(business_address__icontains=item)
        # gender = User.objects.filter(gender__icontains=item)
        # category = User.objects.filter(category__name__icontains=item)
        # business_status = User.objects.filter(business_status__icontains=item)
        # searched_business = username.union(email,fullname,business_name,phone,country,city,business_address,gender,category,business_status)
        searched_business = BusinessStore.objects.filter(
            store_status='Pending',
            name__icontains=item
        )
        context['searched_business'] = searched_business
    else:
        searched_business = BusinessStore.objects.filter(is_deleted=False)
        context['searched_business'] = searched_business
    # if request.user.is_account_officer:
    #     return redirect("account_officer_detail")

    return render(request,"Admin/business.html",context)


@login_required(login_url='admin_login')
def request_verify(request):
    if request.method == 'POST':
        send_request = request.POST.get('send_request')
        request_id = request.POST.get('request_id')

        reservation = request.POST.get('reservation')
        comission = request.POST.get('commission')
        print('******', reservation)
        print('*******', comission)
        user_email = request.POST.get('user_email')
        print(request_id)
        if send_request == 'Accept':
            pending_user = BusinessStore.objects.get(id=request_id)
            pending_user.store_status = 'Active'
            # pending_user.user.business_status = 'Approved'
            
            if reservation:
                pending_user.reservation_fee = reservation
            if comission:
                pending_user.commission_fee = comission

            pending_user.save()
            # business_store = BusinessStore.objects.filter(user=pending_user, store_status='Pending')
            # for i in business_store:
            #     i.verification_status = 'Verified'
            #     i.store_status = 'Active'
            #     i.save()
            html_template = render_to_string('email/request-accepted.html')
            text_template = strip_tags(html_template)
            email = EmailMultiAlternatives(
                'Business Request Submitted',
                text_template,
                settings.EMAIL_HOST_USER,
                [pending_user.user.email],
            )
            email.attach_alternative(html_template, "text/html")
            email.send(fail_silently=False)
            messages.success(request, "Business has been Accepted Successfully!")
            return redirect('admin_business')
        else:
            pending_user = BusinessStore.objects.get(id=request_id)            
            pending_user.store_status = 'Inactive'
            # pending_user.user.business_status = 'Approved'
            pending_user.save()
            # business_store = BusinessStore.objects.filter(user=pending_user, store_status='Pending')
            # for i in business_store:
            #     i.verification_status = 'Verified'
            #     i.store_status = 'Active'
            #     i.save()
            html_template = render_to_string('email/request-rejected.html')
            text_template = strip_tags(html_template)
            email = EmailMultiAlternatives(
                'Business Request Rejected',
                text_template,
                settings.EMAIL_HOST_USER,
                [pending_user.user.email],
            )
            email.attach_alternative(html_template, "text/html")
            email.send(fail_silently=False)
            messages.success(request, "Business has been Rejected Successfully!")
            return redirect('admin_business')
    return redirect('admin_business')



@csrf_exempt
def banner_create(request):
    if request.user.is_superuser:
        if request.method == "POST":
            try:
                image = request.FILES.get('image')  # for another model
                start_date = request.POST.get('start_date')
                end_date = request.POST.get('end_date')
                country = request.POST.get('country')
                company = request.POST.get('company')
                # company = 'three'
                phone = request.POST.get('phone')
                banner_iid = request.POST.get('banner_iid')

                email = request.POST.get('email')
                redirect_url = request.POST.get('redirect_url')

                # country = Country.objects.filter(id=int(country)).first()
                # user = User.objects.filter(is_superuser=True).first()
                user = request.user

                if not image:  # add the corect file path
                    return render(request, 'Store/add_banner.html', {
                        "message": "Please insert valid data"})
                if banner_iid:
                    media = BannerMedia.objects.filter(banner=int(banner_iid))
                    media.delete()
                    banner= Banner.objects.get(id=banner_iid)
                    BannerMedia.objects.create(banner=banner, image=image)
                else:
                    Banner.objects.create(
                        user=user,
                        start_date=start_date,
                        end_date=end_date,
                        country=country,
                        company=company,
                        phone=phone,
                        email=email,
                        redirect_url=redirect_url,
                    )

                    banner_id = Banner.objects.order_by('-id').first()

                    BannerMedia.objects.create(banner=banner_id, image=image)

                # add the correct html file path
                return redirect('admin_content')

            except Exception as e:
                return redirect('admin_content')
        else:
            return redirect('home')
    else:
        return redirect('home')


def admin_content(request):
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    banners = Banner.objects.all()
    text_content = WebDynamicContent.objects.first()
    context = {
        'banners': banners,
        'text_content':text_content
    }
    # add correct path of html file
    return render(request,"Admin/manage-content.html", context)


def ad_faq(request):
    if request.method == 'POST':
        question = request.POST.get('question')
        answer = request.POST.get('answer')

        if question or answer:
            faq = Faq.objects.create(faq_question=question, faq_answer=answer)
        return redirect('/admin_content')

    return render(request,"Admin/manage-content.html")

# @login_required(login_url='admin_login')
def banner_retrieve(request, id):
    banner = Banner.objects.get(id=id)
    serializer = BannerViewSerializer(banner).data
    return JsonResponse(serializer)
    # banner = BannerMedia.objects.select_related("banner").get(id=id)
    # context = {
    #     'banner': banner,
    # }
    # # add correct path of html file
    # return render(request, 'Store/home.html', context)


# @login_required('admin_login')
def banner_destroy(request, id):
    if request.user.is_authenticated and request.user.is_superuser:
        # banner = BannerMedia.objects.select_related("banner").get(id=id)
        # banner_p = Banner.objects.get(id=banner.banner_id)
        banner_p = Banner.objects.get(id=id)
        banner_p.delete()
        # add correct path url
        messages.success(request, "Banner Deleted Successfully!")
        return redirect('admin_content')
    else:
        return redirect('admin_login')


@csrf_exempt
def banner_update(request, id):
    # if request.method == "POST":
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            image = request.FILES.get('image')  # for another model
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            country = request.POST.get('country')
            company = request.POST.get('company')
            phone = request.POST.get('phone')
            status = request.POST.get('status')
            email = request.POST.get('email')
            redirect_url = request.POST.get('redirect_url')

            # country = Country.objects.filter(id=int(country)).first()
            # user = User.objects.filter(is_superuser=True).first()

            # if not image:  # add the corect file path
            #     return render(request, 'Store/add_banner.html', {
            #         "message": "Please insert valid data"})

            banner = Banner.objects.get(id=id)
            banner.user=request.user
            banner.start_date=start_date
            banner.end_date=end_date
            if status:
                if status == 'false':
                    banner.status = False
                if status == 'true':
                    banner.status = True

            # banner.country=country
            banner.company=company
            banner.phone=phone
            banner.email=email
            banner.redirect_url=redirect_url

            banner.save()
            if image and banner:
                media_banner = BannerMedia.objects.get(banner=banner)
                media_banner.image = image
                media_banner.save()

            # add the correct html file path
            return redirect('admin_content')

        except Exception as e:
            return redirect('admin_login')
    else:
        return redirect('admin_login')


@login_required(login_url='admin_login')
def category_create(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            status = request.POST.get('status')
            user = User.objects.filter(is_superuser=True).first()
            category = Category(
                    user=user,
                    name=name,
                    status=status,
            )
            category.save()
            messages.success(request, "Category Created Successfully!")
            return redirect('admin_category')
        except Exception as e:
            messages.error(request, "Category did not Created!")
            return redirect('admin_category')
    return render(request, 'Admin/admin-category.html')




@login_required(login_url='admin_login')
def category_retrieve(request, id):
    category = Category.objects.get(id=id)
    serializer = CategorySerializer(category).data
    return JsonResponse(serializer)


@login_required(login_url='admin_login')
def category_destroy(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    # add correct path url
    messages.success(request, "Category Deleted Successfully!")
    return redirect('admin_category')


@login_required(login_url='admin_login')
def category_update(request, id):
    if request.method == "POST":
            name = request.POST.get('name')  # for another model
            status = request.POST.get('status')
            category = Category.objects.get(id=id)
            category.name=name
            category.status=status
            category.save()
            subcategories_releted_to_category = SubCategory.objects.filter(category__id=id)
            for subcategory in subcategories_releted_to_category:
                subcategory.status=status
                subcategory.save()
            messages.success(request, "Category Updated Successfully!")
            return redirect('admin_category')
    return redirect('admin_category')


@login_required(login_url='admin_login')
def subcategory_create(request):
    if request.method == "POST":
         try:
            print(request.FILES.get('image'))
            category = request.POST.get('category_id',None)
            name = request.POST.get('name' ,None)
            image = request.FILES.get('image' ,None)
            status = request.POST.get('status' ,None)
            category = Category.objects.get(id=category)
            if category.status == 'Inactive' and status == 'Active':
                messages.error(request, "you cannot active subcategory becasue its parent category is inactive!")
                return redirect('admin_category')
            SubCategory.objects.create(name=name,category=category,image=image,status=status)
            messages.success(request, "Subcategory Created Successfully!")
            return redirect('admin_category')

         except Exception as e:
            return redirect('admin_category')
    return render(request, 'Admin/admin-category.html')


@login_required(login_url='admin_login')
def subcategory_retrieve(request, id):
    subcategory = SubCategory.objects.get(id=id)
    serializer = SubCategoryViewSerializer(subcategory).data
    return JsonResponse(serializer)

@login_required(login_url='admin_login')
def subcategory_destroy(request, id):
    subcategory = SubCategory.objects.get(id=id)
    subcategory.delete()
    # add correct path url
    messages.success(request, "Subcategory Deleted Successfully!")
    return redirect('admin_category')


@login_required(login_url='admin_login')
def subcategory_update(request, id):
    if request.method == "POST":
            category = request.POST.get('category')
            name = request.POST.get('name')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            category = Category.objects.get(id=int(category))
            if category.status == 'Inactive' and status == 'Active':
                messages.error(request, "you cannot create subcategory as active becasue its parent category is inactive!")
                return redirect('admin_category')
            subcategory = SubCategory.objects.get(id=id)
            subcategory.category=category
            subcategory.name=name
            subcategory.status=status
            if image:
                subcategory.image=image
            subcategory.save()
            messages.success(request, "Subcategory Updated Successfully!")
            return redirect('admin_category')
    return redirect('admin_category')

@csrf_exempt
def update_user_profile(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    if request.method == "POST":
        name = request.POST.get('first_name')
        # last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        # email = request.POST.get('email')
        email = request.POST.get('email')
        phone = request.POST.get('mobile_number')
        city = request.POST.get('city')
        print(city)
        country = request.POST.get('country')
        print(country)
        address = request.POST.get('address')
        # name = request.POST.get('name')
        user = request.user
        city = City.objects.get(id=int(city))
        country = Country.objects.get(id=int(country))
        user.name = name
        # user.last_name = last_name
        user.gender = gender
        # user.email = email
        user.phone = phone
        user.city = city
        user.country = country
        user.business_address = address
        user.save()
        messages.success(request, 'User profile updated successfully')
        return redirect('user_profile')
    return render(request, 'Store/home.html')


# def retrieve_user_profile(request):
#     if request.user.is_authenticated and request.user.user_type=='Customer':
#         try:
#             user = request.user
#             context = {
#                 'user': user,
#             }
#             # add correct path of html file
#             return render(request, 'Business/user-account-settings.html', context)
#         except Exception as e:
#             redirect('home')
#     else:
#         redirect('home')


#View Further Details of Deals
def view_deal(request,deal_slug):
    print(request.COOKIES)
    get_deal_by_id = BusinessDeal.objects.get(slug=deal_slug, is_deleted=False)
    
    topoffers_filter_by_category = BusinessDeal.objects.filter(sub_category__name=get_deal_by_id.sub_category,
                                        is_expired=False, category__status = 'Active', store__status=True, is_deleted=False)
                                        
    bestsellers_filter_by_category = BusinessDeal.objects.filter(category__name=get_deal_by_id.category,
                                        is_expired=False, category__status = 'Active', store__status=True, is_deleted=False)

    form = NormalUserForm(request.POST)
    form = BusinessUserForm(request.POST, request.FILES)
    businessdeal_data = DifferentDealData.objects.filter(deal=get_deal_by_id).order_by('-created_at')

    context = {}
    context['form'] = form
    context['view_deal'] = get_deal_by_id
    # context['site_url'] = os.getenv('FRONTEND_SERVER_NAME_s3')
    context['site_url'] = settings.FRONTEND_SERVER_NAME  # set this dynamic
    context['businessdeal_data'] = businessdeal_data
    context['topoffers_filter_by_category'] = topoffers_filter_by_category
    context['bestsellers_filter_by_category'] = bestsellers_filter_by_category
    if request.user.is_authenticated:
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=request.user)
    else:
        token = None
        
    context['auth_token'] = token

    return render(request, 'Store/deal-detail.html', context)
    


#View Further Details of Category
@LocationRedirection
def view_category(request, category_slug, country_code = None):
    sub_category = request.GET.get('sub_category', None)
    country = request.GET.get('country', None)
    city = request.GET.get('city', None)
    price = request.GET.get('my_range')
    if price:
        p = price.split(';')
        price1 = p[0]
        price2 = p[1]

    try:
        get_category_by_slug = Category.objects.get(slug=category_slug)
    except:
        get_category_by_slug = None
        return redirect('/')

    if not sub_category:
        sub_category = ''

    if not country:
        country = ''

    if not city:
        city = ''
    
    try:
        default_country = Country.objects.get(name__icontains='United Arab Emirates')
        default_cities = City.objects.filter(state__country__name__icontains=default_country)
    except:
        pass

    try:
        sub_category = SubCategory.objects.get(slug=sub_category)
        sub_category = sub_category.name
    except:
        pass

    try:
        country = Country.objects.get(id=country)
        country = country.name
    except:
        pass

    try:
        city = City.objects.get(id=city)
        city = city.name
    except:
        pass


    if get_category_by_slug is not None:
        sub_categories = SubCategory.objects.filter(category=get_category_by_slug, is_deleted=False)

    top_offers_filter_by_category = BusinessDeal.objects.filter(
                                        category__name__icontains=get_category_by_slug.name, 
                                        category__status = 'Active', is_deleted=False)
    discounts_filter_by_category = BusinessDeal.objects.filter(
                                        category__name__icontains=get_category_by_slug.name, 
                                        category__status = 'Active', is_deleted=False)[:3]
    form = NormalUserForm(request.POST)
    form = BusinessUserForm(request.POST, request.FILES)

    if country and city and sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            price__gte=price1,
                                            price__lte=price2,
                                            store__country__name__icontains = country, is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif country and city and sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            store__country__name__icontains = country, is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif country and city and not sub_category and  price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            is_deleted=False,
                                            store__country__name__icontains = country, is_expired=False,
                                            price__gte=price1,
                                            price__lte=price2,
                                            category__status = 'Active', store__status=True)
    elif country and city and not sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, is_deleted=False,
                                            store__country__name__icontains = country, is_expired=False,
                                            store__city__name__icontains = city,
                                            category__status = 'Active', store__status=True)
    elif country and not city and sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, is_deleted=False,
                                            store__country__name__icontains = country,
                                            is_expired=False,
                                            price__gte=price1,
                                            price__lte=price2,
                                            category__status = 'Active', store__status=True)
    elif country and not city and sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            store__country__name__icontains = country,
                                            is_expired=False, is_deleted=False,
                                            category__status = 'Active', store__status=True)
    elif country and not city and not sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, is_deleted=False,
                                            store__country__name__icontains = country,
                                            price__gte=price1,
                                            price__lte=price2,
                                            is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif country and not city and not sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            
                                            store__country__name__icontains = country, is_deleted=False,
                                            is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and city and sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            price__gte=price1,
                                            price__lte=price2,
                                            is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and city and sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and city and not sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            price__gte=price1,
                                            price__lte=price2, 
                                            is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and city and not sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and not city and sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category,
                                            price__gte=price1,
                                            price__lte=price2, 
                                            is_deleted=False,
                                            is_expired=False,
                                            category__status = 'Active', store__status=True)
    elif not country and not city and sub_category and not price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            sub_category__name__icontains=sub_category, 
                                            is_deleted=False,
                                            is_expired=False,
                                            category__status = 'Active', store__status=True)

    elif not country and not city and not sub_category and price:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, 
                                            price__gte=price1,
                                            price__lte=price2,
                                            is_deleted=False,
                                            store__city__name__icontains = city, is_expired=False,
                                            category__status = 'Active', store__status=True)
    else:
        dealfilter = BusinessDeal.objects.filter(
                                            category__name__icontains=get_category_by_slug.name, is_expired=False,
                                            category__status = 'Active', store__status=True, is_deleted=False)

    context = {}
    context['dealfilter'] = dealfilter
    context['sub_categories'] = sub_categories
    context['form'] = form    
    context['default_cities'] = default_cities    
    context['default_country'] = default_country    

    # context['deal_filtered_category'] = deal_filtered_category
    context['view_category'] = get_category_by_slug
    context['top_offers_filter_by_category'] = top_offers_filter_by_category
    context['discounts_filter_by_category'] = discounts_filter_by_category
    # context['deals_filter_by_category'] = deals_filter_by_category
    return render(request, 'Store/category_detail.html', context)



#View Further Details of SubCategory
@LocationRedirection
def view_subcategory(request, country_code=None):
    subcategory_slug = request.GET.get('sub_category', None)
    category_slug = request.GET.get('category', None)
    sort_by = request.GET.get('sorted_by', '')
    country = request.GET.get('country', '')
    city = request.GET.get('city', '')
    search_by = request.GET.get('search_by', '')
    get_subcategory_by_slug = ''
    sub_categories = ''
    top_offers_filter_by_subcategory = ''
    discounts_filter_by_subcategory = ''
    deals_filter_by_subcategory = ''
    sub_categories = ''
    dealfilter = ''
    deal_filtered_category = ''
    discounts_filter_by_subcategory = ''

    if  category_slug and category_slug is not None:
        get_subcategory_by_slug = SubCategory.objects.get(category__slug=category_slug, slug=subcategory_slug, status='Active')
    elif subcategory_slug and not category_slug:
        get_subcategory_by_slug = SubCategory.objects.get(slug=subcategory_slug, status='Active')
    elif not subcategory_slug and category_slug:
        get_subcategory_by_slug = SubCategory.objects.filter(slug=subcategory_slug, status='Active')
    else:
        pass
    
    if get_subcategory_by_slug:
        top_offers_filter_by_subcategory = BusinessDeal.objects.filter(sub_category__name=get_subcategory_by_slug.name,
                                                                    is_deleted=False, is_expired=False, store__status=True)
        discounts_filter_by_subcategory = BusinessDeal.objects.filter(sub_category__name=get_subcategory_by_slug.name,
                                                                  is_deleted=False, is_expired=False, store__status=True)

        deals_filter_by_subcategory = BusinessDeal.objects.filter(sub_category__name=get_subcategory_by_slug.name,
                                                                is_deleted=False, is_expired=False, store__status=True)
        sub_categories = SubCategory.objects.filter(category__slug=get_subcategory_by_slug.category.slug, status='Active')

        dealfilter = BusinessDealFilter(request.GET, queryset=deals_filter_by_subcategory)
        deal_filtered_category = dealfilter.qs

        top_offers_filter_by_subcategory = BusinessDeal.objects.filter(sub_category__name=get_subcategory_by_slug.name, is_deleted=False)
        discounts_filter_by_subcategory = BusinessDeal.objects.filter(sub_category__name=get_subcategory_by_slug.name, is_deleted=False)

        top_offers_filter_by_category = BusinessDeal.objects.filter(is_deleted=False,
                                            category__name__icontains=get_subcategory_by_slug.name, 
                                            category__status = 'Active')
        discounts_filter_by_category = BusinessDeal.objects.filter(is_deleted=False,
                                            category__name__icontains=get_subcategory_by_slug.name, 
                                            category__status = 'Active')[:3]
    if category_slug:
        sub_categories = SubCategory.objects.filter(category__slug=category_slug, is_deleted=False)

    sub_category = request.GET.get('sub_category', None)
    country = request.GET.get('country', None)
    city = request.GET.get('city', None)

    try:
        get_subcategory_by_slug =SubCategory.objects.get(category__slug=category_slug, slug=subcategory_slug)
    except:
        pass

    if not sub_category:
        sub_category = ''

    if not country:
        country = ''

    if not city:
        city = ''
    
    try:
        default_country = Country.objects.get(name__icontains='United Arab Emirates')
        default_cities = City.objects.filter(state__country__name__icontains=default_country)
    except:
        pass

    try:
        sub_category = SubCategory.objects.get(name=sub_category)
        get_subcategory_by_slug = sub_category
    except:
        pass

    try:
        country = Country.objects.get(id=country).name
    except:
        pass

    try:
        city = City.objects.get(id=city).name
    except:
        pass

    if country and city and sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name,
                                            store__country__name__icontains = country, is_deleted=False,
                                            city__name__icontains = city,
                                            category__status = 'Active', status=True)
    elif country and city and not sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            store__country__name__icontains = country, is_deleted=False,
                                            store__city__name__icontains = city)
                                            #category__status = 'Active', status=True)
    elif country and not city and sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name, 
                                            store__store__country__name__icontains = country, is_deleted=False,
                                            category__status = 'Active', status=True)
    elif country and not city and not sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name, 
                                            store__store__country__name__icontains = country, is_deleted=False,
                                            category__status = 'Active', status=True)
    elif not country and city and sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name, 
                                            store__city__name__icontains = city, is_deleted=False,
                                            category__status = 'Active', status=True)
    elif not country and city and not sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name, 
                                            store__city__name__icontains = city, is_deleted=False,
                                            category__status = 'Active', status=True)
    elif not country and not city and sub_category:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug.name, 
                                            category__status = 'Active', is_deleted=False, status=True)
    else:
        dealfilter = BusinessDeal.objects.filter(
                                            sub_category__name__icontains=get_subcategory_by_slug, 
                                            category__status = 'Active', is_deleted=False, status=True)
    print('***************', dealfilter)
    # dealfilter = BusinessDealFilter(request.GET, queryset=deals_filter_by_category)
    # deal_filtered_category = dealfilter.qs

    context = {}
    # context['form'] = form
    context['dealfilter'] = dealfilter
    context['default_country'] = default_country
    context['default_cities'] = default_cities 

    context['category_slug'] = category_slug
    context['sub_categories'] = sub_categories
    # context['deal_filtered_category'] = deal_filtered_category
    context['view_category'] = get_subcategory_by_slug
    context['top_offers_filter_by_category'] = top_offers_filter_by_subcategory
    context['discounts_filter_by_category'] = discounts_filter_by_subcategory



    # context['deals_filter_by_category'] = deals_filter_by_subcategory
    return render(request, 'Store/category_detail.html', context)





@login_required(login_url='home')
def update_deal(request, id):
    try:
        request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    except:
        return redirect('business_settings')
    if request.method == 'POST':
        deal_instance = BusinessDeal.objects.get(id=id, is_deleted=False)
        # store = deal_instance.store
        category = request.POST.get('category')
        sub_category = request.POST.get('sub_category')
        sub_sub_category = request.POST.get('sub_sub_category')
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        image = request.FILES.getlist('image')
        gender = request.POST.get('gender')
        quantity = request.POST.get('quantity')

        #something should be update here about request.user
        user = User.objects.filter(id=user).first()
        store = BusinessStore.objects.filter(id=int(store)).first()
        category = Category.objects.filter(id=int(category)).first()
        sub_category = SubCategory.objects.filter(id=int(sub_category)).first()
        store_ins = BusinessStore.objects.filter(id=deal_instance.store.id, is_deleted=False,).first()
        if not user:
            print("user not found")
            return redirect('')

        # if not store or not category or not sub_category \
        #         or not title or not description or not gender \
        #         or not price or not start_date or not end_date or not quantity:
        #     print("something missing")

        deal_instance.objects.update(
            store=store_ins,
            category=category,
            sub_category=sub_category,
            title=title,
            description=description,
            price=price,
            start_date=start_date,
            end_date=end_date,
            gender=gender,
            quantity=quantity)
        if image:
            img = DealMedia.objects.filter(business_deal=deal_instance)
            img.delete()
        for i in image:
            media = DealMedia.objects.create(business_deal=deal_instance, image=i)
        print("********")
        # give correct url
        return redirect('')
    return redirect('')


@login_required(login_url='home')
def delete_deal(request, id):
    try:
        request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    except:
        return redirect('business_settings')
    try:
            deal_instance = BusinessDeal.objects.get(id=id, is_deleted=False)
            if deal_instance:
                deal_option = DifferentDealData.objects.filter(deal=deal_instance, is_delete=False)
                if deal_option:
                    for option in deal_option:
                        option.is_delete = True
                        option.save()
            if deal_instance:
                deal_instance.is_deleted = True
                deal_instance.save()
                messages.success(request,'Deal Deleted Successfully!')
            return redirect('DealCreateView')
    except Exception as e:
            print(e)
            return redirect('DealCreateView')
    return redirect('DealCreateView')



@login_required(login_url='home')
def create_store(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    # try:
    #     request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    # except:
    #     return redirect('business_settings')

    if request.method == 'POST':
            name = request.POST.get('name')
            category = request.POST.get('category')
            subcategory = request.POST.getlist('sub_category')
            image = request.FILES.get('image')
            address = request.POST.get('address')
            status = request.POST.get('status')
            country = request.POST.get('country')
            city = request.POST.get('city')
            phone = request.POST.get('phone')

            license_id = request.POST.get('license_id')
            license_file = request.FILES.get('license_file')

            check_store = BusinessStore.objects.filter(user=user, category=category)
            if check_store:
                bool_status = True
                store_status = 'Active'
            else:
                bool_status = False
                store_status = 'Pending'

            try:
                city = City.objects.get(id=int(city))
            except:
                pass
            if category:
                category = Category.objects.filter(id=int(category)).first()
            
            try:
                country = Country.objects.get(id=int(country))
            except:
                pass

            business_store = BusinessStore(
                user = request.user,
                country=country,
                category=category,
                name=name,
                city = city,
                phone=phone,
                business_logo=image,
                license_id=license_id,
                license_document=license_file,
                # store_address=address,
                store_status=store_status,
                status=bool_status,
            )
            business_store.save()
            if subcategory:
                for s in subcategory:

                    sub = SubCategory.objects.get(id=int(s))
                    business_store.subcategory.add(sub)
            location = StoreLocation.objects.create(business_store=business_store, adress=address, status=True, city=city)
            messages.success(request,'Store Created Successfully!')
            return redirect('create_store')
    if request.method == "GET":
        try:
            item = request.GET.get('item')
            store_name = BusinessStore.objects.filter(
                Q(name__icontains=item)|
                Q(category__name__icontains=item) |
                Q(subcategory__name__icontains=item) |
                Q(description__icontains=item),
                user=request.user, 
                is_deleted=False)
            # category_name = BusinessStore.objects.filter(category__name__icontains=item,user=request.user)
            # country_name = BusinessStore.objects.filter(country__name__icontains=item,user=request.user)
            # city_name = BusinessStore.objects.filter(city__name__icontains=item,user=request.user)
            # description = BusinessStore.objects.filter(description__icontains=item,user=request.user)
            # price = BusinessStore.objects.filter(deal_price__icontains=item,user=request.user)
            # address = BusinessStore.objects.filter(store_address__icontains=item,user=request.user)
            # status = BusinessStore.objects.filter(store_status__icontains=item,user=request.user)
            # store_list = store_name.union(category_name,country_name,city_name,description,price,address,status)
            store_list = store_name
            context['store_list'] = store_list
            return render(request, 'Business/create-store.html',context)
        except Exception as e:
            print(e)
    store_list = BusinessStore.objects.filter(user=request.user, is_deleted=False)
    context['store_list'] = store_list
    return render(request,'Business/create-store.html', context)


@login_required(login_url='home')
def update_store(request, id):
    try:
        request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    except:
        return redirect('business_settings')
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        category = request.POST.get('category')
        subcategory = request.POST.getlist('sub_category')
        country = request.POST.get('country')
        image = request.FILES.get('image')
        store_address = request.POST.get('address')
        status = request.POST.get('status')
        phone = request.POST.get('phone')

        if status == 'Active':
            bool_status = True
        else:
            bool_status = False

        if city:
            try:
                city = City.objects.get(id=int(city))
            except:
                pass
        if category:
            try:
                category = Category.objects.get(id=int(category))
            except:
                pass
        # if subcategory:
        #     subcategory = SubCategory.objects.filter(id=int(subcategory)).first()
        if country:
            try:
                country = Country.objects.get(id=int(country))
            except:
                pass

        get_businesstore = BusinessStore.objects.get(id=id, is_deleted=False)
        get_businesstore.city = city
        get_businesstore.category=category
        get_businesstore.country=country
        get_businesstore.store_status=status
        get_businesstore.phone=phone
        get_businesstore.name=name
        get_businesstore.store_address=store_address
        get_businesstore.status=bool_status

        if subcategory:
            for s in subcategory:
                sub = SubCategory.objects.get(id=int(s))
                get_businesstore.subcategory.add(sub)

        if image:
            get_businesstore.business_logo=image
        get_businesstore.save()

        try:
            if get_businesstore.status is False or get_businesstore.store_status == 'Inactive':
                # deals = BusinessDeal.objects.filter(store=id)
                deals = BusinessDeal.objects.filter(store=get_businesstore, is_deleted=False)
                for deal in deals:
                    deal.status = False
                    deal.deal_status = 'Inactive'
                    deal.save()
        except Exception as e:
            pass


        # if get_businesstore.store_status == 'Inactive':
        #     all_deals = BusinessDeal.objects.filter(store=get_businesstore, status=True, is_deleted=False)
        #     for d in all_deals:
        #         d.status = False
        #         d.save()


        messages.success(request,'Store Updated Successfully!')
        return redirect('create_store')
    return redirect('create_store')


@login_required(login_url='home')
def retrieve_store(request, id):
    store = BusinessStore.objects.get(id=id)
    serializer = StoreSerializerTemplate(store).data
    return JsonResponse(serializer)


@login_required(login_url='home')
def delete_store(request, id):
    try:
        request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    except:
        return redirect('business_settings')
    try:
        store_instance = BusinessStore.objects.get(id=id, is_deleted=False)
        if store_instance:
            deals = BusinessDeal.objects.filter(store=store_instance, is_deleted=False)
            if deals:
                for deal in deals:
                    deal.is_deleted = True
                    deal.save()
        store_instance.is_deleted = True
        store_instance.save()
        messages.success(request, 'Store Deleted Successfully!')
        return redirect('create_store')
    except Exception as e:
        print(e)
        return redirect('create_store')
    return redirect('create_store')


def add_store_location(request, slug):
    context = dict()
    try:
        businesstore = BusinessStore.objects.get(slug=slug, is_deleted=False)
        cities = City.objects.filter(state__country__name=businesstore.country)
    except Exception as e:
        pass

    if request.method == 'POST':
        data = request.POST.get('location_data')
        quantity = request.POST.get('quantity')
        data = json.loads(data)
        for i in data:
            # my_dict = json.loads(i)
            # for k,v in i.items():
            #     print('key', k, 'val', v)
            location = StoreLocation.objects.create(business_store=businesstore, adress=i['address'], status=True, city_id=i['city'], location_detail=i['name'], quantity=i['quantity'])

        messages.success(request,'Store Updated Successfully!')
        return redirect('create_store')
    context = {
    'businesstore': businesstore,
    'cities': cities
    }
    return render(request, 'Store/store-location.html', context)


def search_deals(request):
    context = {}
    if request.method == "GET":
        item = request.GET.get('item')
        if item:
            # store_name = BusinessDeal.objects.filter(store__name__icontains=item)
            # category_name = BusinessDeal.objects.filter(category__name__icontains=item)
            # country_name = BusinessDeal.objects.filter(country__name__icontains=item)
            # city_name = BusinessDeal.objects.filter(city__name__icontains=item)
            title = BusinessDeal.objects.filter(Q(title__icontains=item) |
                                                Q(category__name__icontains=item) |
                                                Q(sub_category__name__icontains=item)
                                                                )
            # description = BusinessDeal.objects.filter(description__icontains=item)
            # price = BusinessDeal.objects.filter(price__icontains=item)
            # discount_percentage = BusinessDeal.objects.filter(discount_percentage__icontains=item)
            # gender = BusinessDeal.objects.filter(gender__icontains=item)
            # status = BusinessDeal.objects.filter(status__icontains=item)
            # searched_deals = store_name.union(category_name,country_name,city_name,title,description,price,discount_percentage,gender,status)
            context['searched_deals'] = title
            return render(request, 'Store/search-deals.html', context)
    else:
        return redirect('home')
    return redirect('home')


@csrf_exempt
def update_business_profile(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    if request.user.is_authenticated:
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            # email = request.POST.get('email')
            name = request.POST.get('name')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            business_address = request.POST.get('business_address')
            phone = request.POST.get('phone')
            profile_pic = request.FILES.get('site_logo')
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.name = name
            user.business_address = business_address
            user.phone = phone
            if profile_pic:
                user.logo = profile_pic
            if password1 != None and password2 != None and password1==password2:
                user.set_password(password1)
            else:
                print("enter corect data")
            user.save()
            messages.success(request, "Basic Information Updated Successfully!")
            return redirect('business_settings')
        return redirect('business_settings')
    return redirect('home')



@csrf_exempt
def update_business_password(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    if request.user.is_authenticated:
        if request.method == "POST":
            current_password = request.POST.get('current_password')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            user = request.user
            if not user.check_password(current_password):
                messages.error(request, 'Your current password does not match!')
                return redirect('business_settings')
            if len(password1) < 6:
                messages.error(request, 'Password length must be greater than 6!')
                return redirect('business_settings')
            user.set_password(password1)
            user.save()
            messages.success(request, 'Password has been reset Successfully!')
            return redirect('home')
        return redirect('business_settings')
    return redirect('home')


@csrf_exempt
def update_business_len_cur(request):
    context = {}
    user = request.user
    if request.user.is_authenticated:
        if request.method == "POST":
            language = request.POST.get('language')
            # print(language)
            currency = Currency.objects.get(id=int(request.POST.get('currency')))

            user = request.user
            user.language = language
            user.currency = currency
            user.save()

            # messages.success(request, 'Student Record Are Successfully Updated !')
            # render on right path and page
            if user.is_superuser:
                messages.success(request, "General Settings Updated Successfully!")
                return redirect('admin_profile')
            if user.user_type == "Customer":
                messages.success(request, "General Settings Updated Successfully!")
                return redirect('user_profile')
            messages.success(request, "General Settings Updated Successfully!")
            return redirect('business_settings')
        if user.is_superuser:
            return redirect('admin_profile')
        if user.user_type == "Customer":
            return redirect('user_profile')
        return redirect('business_settings')
    return redirect('home')

# @login_required
def add_to_cart(request):
    if request.method == "POST":
        user = request.user
        deal_id = request.POST.get('deal_id')
        option_ids = request.POST.getlist('option')
        quantity = request.POST.getlist('quantity')
        # for i in quantity:
        #     if i == str(0)
        #         i.pop(1)
        request.session['deal_id'] = deal_id
        request.session['option'] = option_ids
        request.session['quantity'] = quantity
        context = {
            deal_id : deal_id,
            option_ids : option_ids,
            quantity : quantity
        }

        # deal = BusinessDeal.objects.filter(id=deal_id, is_deleted=False, is_expired=False).first()
        # store = BusinessStore.objects.filter(id=deal.store_id, is_deleted=False, status=True, store_status='Approved').first()
        # if deal and store:
        #     discount_price = deal.discount_price
        #     delivery_charges = deal.delivery_charges
        #     CartItem(user=user, deal=deal, store=store, quantity=quantity, discount_price=discount_price,
        #              delivery_charges=delivery_charges).save()
        return render(request, 'Store/add-to-cart.html', context)
    else:
        return redirect('/')
    return redirect('/')


@csrf_exempt
def update_user_leng_cur(request):
    if request.method == "POST":
        try:
            language = request.POST.get('language')
            currency = request.POST.get('currency')

            user = User.objects.filter(id=request.user.id).first()
            if user:
                currency = Currency.objects.get(id=int(currency))

                user.language = language
                user.currency = currency

                user.save()
            else:
                print('user not found')
            # messages.success(request, 'Student Record Are Successfully Updated !')
            # render on right path and page
            return redirect('/')
        except Exception as e:
            print(str(e))

    return render(request, 'Store/home.html')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        carts = CartItem.objects.filter(user=user)

        amount = 0.0
        shipping_amount = 0.0
        total_amount = 0.0
        cart_product = [p for p in CartItem.objects.all() if p.user == user]

        if cart_product is not None:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discount_price)
                amount += tempamount
                shipping_amount = p.delivery_charges
                total_amount = amount + shipping_amount
        # set the correct html file path
        return render(request, 'Store/home.html', {'carts': carts, 'total_amount': total_amount, 'shipping_amount': shipping_amount, 'amount': amount})


@login_required
def remove_cart(request):
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = CartItem.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 0.0
        total_amount = 0.0
        cart_product = [p for p in CartItem.objects.all() if p.user == user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
            shipping_amount = p.delivery_charges
        data = {
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)


@login_required
def plus_cart(request):
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = CartItem.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shipping_amount = 0.0
        total_amount = 0.0
        cart_product = [p for p in CartItem.objects.all() if p.user == user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
            shipping_amount = p.delivery_charges

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)

@login_required
def minus_cart(request):      # add authentication
    if request.method == 'GET':
        user = request.user
        prod_id = request.GET['prod_id']
        c = CartItem.objects.get(Q(id=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shipping_amount = 0.0
        total_amount = 0.0
        cart_product = [p for p in CartItem.objects.all() if p.user == user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discount_price)
            amount += tempamount
            shipping_amount = p.delivery_charges

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'total_amount': amount + shipping_amount
        }
        return JsonResponse(data)


@login_required(login_url='home')
def business_dashboard(request):
    user = request.user
    today = datetime.datetime.now()
    current_month = today.month
    current_year = date.today().year

    month_orders = []
    my_store = request.GET.get('store_name', None)
    if my_store:
        try:
            my_store = BusinessStore.objects.get(slug=my_store)
        except:
            pass

        order_item = OrderItem.objects.filter(deal_option__deal__store=my_store).order_by('-created_at')

        for m in range(current_month):
            months = m+1
            graph_order_item = OrderItem.objects.filter(
                                                created_at__month=months, 
                                                created_at__year=current_year, 
                                                deal_option__deal__store=my_store)
            month_orders.append(graph_order_item)
            
    else:
        for m in range(current_month):
            months = m+1
            graph_order_item = OrderItem.objects.filter(
                                                created_at__month=months, 
                                                created_at__year=current_year, 
                                                deal_option__deal__store__user=user)
            month_orders.append(graph_order_item)
        order_item = OrderItem.objects.filter(deal_option__deal__store__user=user).order_by('-created_at')
    business_store = BusinessStore.objects.filter(store_status='Active', is_deleted=False)

    context={
        'business_store': business_store,
        'order_item': order_item,
        'month_orders':month_orders,
    }
    return render(request,"Business/dashboard.html", context)


# @login_required(login_url='home')
# def single_store_dashboard(request, slug):

    


#     context={
        
#     }
    
#     return render(request,"Business/dashboard.html", context)
    # context = {}
    # user = request.user
    # try:
    #     User.objects.get(id=user.id, is_admin=True)
    #     return redirect('home')
    # except Exception as e:
    #     pass
    # try:
    #     request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
    # except:
    #     return redirect('business_settings')
    # # business_user_order = OrderPlaced.objects.filter(deal__create_by=user)[:5]
    # business_user_order = OrderPlaced.objects.all()
    # # reviews_of_deal = DealRating.objects.filter(business_deal__create_by=user)[:5]
    # reviews_of_deal = DealRating.objects.all()
    # # top_selling_products = BusinessDeal.objects.filter(id=user.id)[:5]
    # top_selling_products = BusinessDeal.objects.filter(is_deleted=False).all()

    # context['business_user_order'] = business_user_order
    # context['reviews_of_deal'] = reviews_of_deal
    # context['top_selling_products'] = top_selling_products
    # context['user'] = request.user
    # return redirect('create_store')

    

@login_required(login_url='home')
def business_settings(request):
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    try:
        user = request.user
        currencies = Currency.objects.all()
        context = {}
        context['user'] = user
        context['currencies'] = currencies
        context['pending_business_msg'] = 'Your Business request has been submitted successfully. You will get a confirmation email after approval'
        return render(request,"Business/business-settings.html", context)
    except Exception as e:
        return render(request, "Business/business-settings.html")
    else:
        return redirect('home')

@csrf_exempt
def user_profile(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    try:
        request_user = User.objects.get(username = request.user)
    except Exception as e:
        return redirect('/')
    try:
        user = request.user
        currencies = Currency.objects.all()
        context = {}
        context['user'] = user

        context['currencies'] = currencies
        return render(request,"Store/user-account-settings.html", context)
    except Exception as e:
        return render(request, "Store/user-account-settings.html")

@login_required(login_url='admin_login')
def admin_profile(request):
    try:
        request_user = User.objects.get(username=request.user, is_account_officer=True)
        return redirect('account_officer_detail')
    except Exception as e:
        user = request.user
        try:
            User.objects.get(id=user.id, is_admin=True)
        except Exception as e:
            return redirect('home')
        currencies = Currency.objects.all()
        context = {}
        context['user'] = user
        context['currencies'] = currencies
        return render(request,"Admin/admin-profile-settings.html", context)
    return redirect('home')
    # else:
    #     return redirect('home')




@login_required(login_url='admin_login')
def site_settings(request):
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
    except Exception as e:
        return redirect('home')
    if request.method == 'POST':
                logo = request.FILES.get('site_logo')
                username = request.POST.get('username')
                # email = request.POST.get('email')
                phone = request.POST.get('mobile_number')
                print(phone)
                country = request.POST.get('country')
                location_business = request.POST.get('location_business')
                country= Country.objects.get(id=int(country))
                try:
                    user = User.objects.get(username=request.user, is_admin=True)
                except Exception as e:
                    print(e)

                if logo:
                    user.logo = logo
                user.username = username
                # user.email = email
                user.phone = phone
                user.country= country
                user.location_business = location_business
                user.save()
                messages.success(request, "Admin Settings Updated Successfully!")
                return redirect('admin_profile')
    else:
                return redirect('admin_profile')


@csrf_exempt
def admin_password(request):
    context = {}
    user = request.user
    try:
        User.objects.get(id=user.id, is_admin=True)
        return redirect('home')
    except Exception as e:
        pass
    if request.user.is_authenticated:
        try:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            con_password = request.POST.get('con_password')
            user = request.user
            if not user.check_password(old_password):
                messages.error(request, 'Your current password does not match!')
                return redirect('user_profile')
            if len(new_password) < 6:
                messages.error(request, 'Password length must be greater than 6!')
                return redirect('user_profile')
            if new_password != con_password:
                messages.error(request, 'New password does not match!')
                return redirect('user_profile')
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset Successfully!')
            return redirect('user_profile')
        except Exception as e:
            return redirect('user_profile')
    else:
        return redirect('user_profile')


@csrf_exempt
def admin_password_chnage(request):
    print(request.user.is_admin)
    if request.user.is_authenticated:
        try:
            new_password = request.POST.get('new_password')
            con_password = request.POST.get('con_password')
            user = request.user
            if len(new_password) < 6:
                messages.error(request, 'Password length must be greater than 6!')
                return redirect('admin_profile')
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been reset Successfully!')
            return redirect('admin_profile')
        except Exception as e:
            return redirect('admin_profile')
    else:
        return redirect('admin_profile')

# @login_required(login_url='home')
# def add_deal(request):
#     context = {}
#     try:
#         request_user = User.objects.get(username=request.user, business_status='Approved', user_type='Business')
#     except:
#         return redirect('business_settings')
#     if request.method == 'POST':
#             user = request.user
#             category = request.POST.get('category')
#             sub_category = request.POST.get('subcategory')
#             title = request.POST.get('title')
#             description = request.POST.get('description')
#             price = request.POST.get('price')
#             start_date = request.POST.get('start_date')
#             end_date = request.POST.get('end_date')
#             image = request.FILES.get('image')
#             video = request.FILES.get('video')
#             gender = request.POST.get('gender')
#             discount_percentage = request.POST.get('discount_percentage')
#             store = request.POST.get('store')
#             city = request.POST.get('city')
#             status = request.POST.get('status')
#             country = request.POST.get('country')
#
#
#             #something should be update here about request.user
#             store = BusinessStore.objects.filter(id=int(store)).first()
#             category = Category.objects.filter(id=int(category)).first()
#             sub_category = SubCategory.objects.filter(id=int(sub_category)).first()
#             city = City.objects.filter(id=int(city)).first()
#             country = Country.objects.filter(id=int(country)).first()
#             if status == 'Active':
#                 status = True
#             elif status == 'Inactive':
#                 status = False
#             else:
#                 pass
#             business_deal = BusinessDeal(
#                 title=title,
#                 store = store,
#                 category=category,
#                 sub_category=sub_category,
#                 start_date=start_date,
#                 end_date=end_date,
#                 gender=gender,
#                 create_by=user,
#                 city=city,
#                 status = status,
#                 country=country,
#             )
#             business_deal.save()
#             deals_data = DifferentDealData(deal=business_deal,title=title, description=description, price=price,discount_percentage=discount_percentage)
#             deals_data.save()
#             media = DealMedia.objects.create(business_deal=business_deal, image=image,video=video,order=1)
#             media.save()
#             return redirect('add_deal')
#     if request.method == "GET":
#         try:
#             item = request.GET.get('item')
#             store_name = BusinessDeal.objects.filter(store__name__icontains=item)
#             category_name = BusinessDeal.objects.filter(category__name__icontains=item)
#             country_name = BusinessDeal.objects.filter(country__name__icontains=item)
#             city_name = BusinessDeal.objects.filter(city__name__icontains=item)
#             title = BusinessDeal.objects.filter(title__icontains=item)
#             description = BusinessDeal.objects.filter(description__icontains=item)
#             price = BusinessDeal.objects.filter(price__icontains=item)
#             discount_percentage = BusinessDeal.objects.filter(discount_percentage__icontains=item)
#             gender = BusinessDeal.objects.filter(gender__icontains=item)
#             status = BusinessDeal.objects.filter(status__icontains=item)
#             searched_deal = store_name.union(category_name,country_name,city_name,title,description,price,discount_percentage,gender,status)
#             context['searched_deal'] = searched_deal
#             return render(request, "Business/add-deal.html", context)
#         except Exception as e:
#             print(e)
#     searched_deal = BusinessDeal.objects.all()
#     context['searched_deal'] = searched_deal
#     return render(request, "Business/add-deal.html", context)



class DealCreateView(CreateView, SuccessMessageMixin, LoginRequiredMixin):
    model = BusinessDeal
    success_url = reverse_lazy('DealCreateView')
    template_name = 'Business/businessdeal_form.html'
    form_class = BusinessDealForm
    redirect_field_name = '/home/'
    success_message = "Deal Created Successfully!"

    def get(self, *args, **kwargs):
        context = {}
        user = self.request.user
        try:
            User.objects.get(id=user.id, is_admin=True)
            return redirect('home')
        except Exception as e:
            pass
        # try:
        #     request_user = User.objects.get(username=self.request.user, business_status='Approved', user_type='Business')
        # except:
        #     return redirect('business_settings')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DealCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = DifferentDealDataFormset(
                self.request.POST, prefix="differentdealdata_set"
            )
        else:
            item = self.request.GET.get('item', '')
            store_name = self.request.GET.get('store_name')

            if item:
                store_name = BusinessDeal.objects.filter(
                            Q(title__icontains=item) |
                            Q(store__name__icontains=item) |
                            Q(description__icontains=item) ,
                            create_by=self.request.user,
                            is_deleted=False)
                # category_name = BusinessDeal.objects.filter(category__name__icontains=item,create_by=self.request.user)
                # country_name = BusinessDeal.objects.filter(country__name__icontains=item,create_by=self.request.user)
                # city_name = BusinessDeal.objects.filter(city__name__icontains=item,create_by=self.request.user)
                # title = BusinessDeal.objects.filter(title__icontains=item,create_by=self.request.user)
                # description = BusinessDeal.objects.filter(description__icontains=item,create_by=self.request.user)
                # price = BusinessDeal.objects.filter(price__icontains=item,create_by=self.request.user)
                # discount_percentage = BusinessDeal.objects.filter(discount_percentage__icontains=item,create_by=self.request.user)
                # gender = BusinessDeal.objects.filter(gender__icontains=item,create_by=self.request.user)
                # status = BusinessDeal.objects.filter(status__icontains=item,create_by=self.request.user)
                # searched_deall = store_name.union(category_name, country_name, city_name, title, description, price,
                #                                  discount_percentage, gender, status)
                searched_deall=store_name
                context['searched_deal'] = searched_deall
            else:
                my_store = ''
                try:
                    my_store = BusinessStore.objects.get(slug=store_name)
                except:
                    pass
                if my_store:
                    searched_deall = BusinessDeal.objects.filter(create_by=self.request.user, is_deleted=False, store=my_store)
                    print('*******', searched_deall)
                else:
                    searched_deall = BusinessDeal.objects.filter(create_by=self.request.user, is_deleted=False)
                stores = BusinessStore.objects.filter(user=self.request.user, store_status='Active', is_deleted=False)
                context['searched_deal'] = searched_deall
                context['stores'] = stores
            context['mediaform'] = DealMediaForm()
            context["items"] = DifferentDealDataFormset(prefix="differentdealdata_set")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        form.instance.create_by = self.request.user
        self.object.save()
        formed = DealMediaForm(self.request.POST, self.request.FILES or None)
        files = self.request.FILES.getlist('image')
        video = self.request.FILES.get('video')
        location = self.request.POST.getlist('location')
        for l in location:
            self.object.location.add(l)
        self.object.save()

        if files:
            for i in files:
                save_media = DealMedia.objects.create(business_deal=self.object, image=i)
        if video:
            save_media = DealMedia.objects.create(business_deal=self.object, video=video)
            
        
        # context['mediaform'] = formed
        # if formed.is_valid():
        #     for idx, f in enumerate(files):
        #         if int(idx) == 0:
        #             save_media = DealMedia(business_deal=self.object, image=f,video=video)
        #             save_media.save()
        #         else:
        #             save_media = DealMedia(business_deal=self.object, image=f)
        #             save_media.save()
        if self.object.id != None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)





class DealCreateView2(CreateView, SuccessMessageMixin, LoginRequiredMixin):
    model = BusinessDeal
    success_url = reverse_lazy('DealCreateView')
    template_name = 'Business/business_deal.html'
    form_class = BusinessDealForm
    redirect_field_name = '/home/'
    success_message = "Deal Created Successfully!"

    def get(self, *args, **kwargs):
        context = {}
        user = self.request.user
        try:
            User.objects.get(id=user.id, is_admin=True)
            return redirect('home')
        except Exception as e:
            pass
        # try:
        #     request_user = User.objects.get(username=self.request.user, business_status='Approved', user_type='Business')
        # except:
        #     return redirect('business_settings')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DealCreateView2, self).get_context_data(**kwargs)
        if self.request.POST:
            context["items"] = DifferentDealDataFormset(
                self.request.POST, prefix="differentdealdata_set"
            )
        else:
            item = self.request.GET.get('item', '')
            if item:
                store_name = BusinessDeal.objects.filter(title__icontains=item,create_by=self.request.user, is_deleted=False)
                # category_name = BusinessDeal.objects.filter(category__name__icontains=item,create_by=self.request.user)
                # country_name = BusinessDeal.objects.filter(country__name__icontains=item,create_by=self.request.user)
                # city_name = BusinessDeal.objects.filter(city__name__icontains=item,create_by=self.request.user)
                # title = BusinessDeal.objects.filter(title__icontains=item,create_by=self.request.user)
                # description = BusinessDeal.objects.filter(description__icontains=item,create_by=self.request.user)
                # price = BusinessDeal.objects.filter(price__icontains=item,create_by=self.request.user)
                # discount_percentage = BusinessDeal.objects.filter(discount_percentage__icontains=item,create_by=self.request.user)
                # gender = BusinessDeal.objects.filter(gender__icontains=item,create_by=self.request.user)
                # status = BusinessDeal.objects.filter(status__icontains=item,create_by=self.request.user)
                # searched_deall = store_name.union(category_name, country_name, city_name, title, description, price,
                #                                  discount_percentage, gender, status)
                searched_deall=store_name
                context['searched_deal'] = searched_deall
            else:
                searched_deall = BusinessDeal.objects.filter(create_by=self.request.user, is_deleted=False)
                stores = BusinessStore.objects.filter(user=self.request.user, store_status='Active', is_deleted=False)
                context['searched_deal'] = searched_deall
                context['stores'] = stores
            context['mediaform'] = DealMediaForm()
            context["items"] = DifferentDealDataFormset(prefix="differentdealdata_set")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["items"]
        self.object = form.save()
        form.instance.create_by = self.request.user
        self.object.save()
        formed = DealMediaForm(self.request.POST, self.request.FILES or None)
        files = self.request.FILES.getlist('image')
        video = self.request.FILES.get('video')
        start_date = self.request.POST.get('start_date')
        is_continue = self.request.POST.get('is_continue')
        is_featured = self.request.POST.get('is_featured')
        quantity = self.request.POST.get('quantity')

        
        start_date = self.request.POST.get('start_date')

        location = self.request.POST.getlist('location')

        title2 = self.request.POST.get('title2')
        discount_percentage = self.request.POST.get('discount_percentage')

        if is_continue:
            is_continue = True
        else:
            is_continue = False

        if is_featured:
            is_featured = True
        else:
            is_featured = False
            
        self.object.start_date = start_date
        for l in location:
            self.object.location.add(l)
        self.object.is_continue = is_continue
        self.object.is_featured = is_featured
        self.object.save()
        option = DifferentDealData(deal=self.object, title=title2, discount_percentage=discount_percentage, quantity=quantity)
        deal_location = DealLocation.objects.create(business_deal=self.object, quantity=quantity)
        option.save()

        if files:
            for i in files:
                save_media = DealMedia.objects.create(business_deal=self.object, image=i)

        if video:
            save_media = DealMedia.objects.create(business_deal=self.object, video=video)
            
        
        # context['mediaform'] = formed
        # if formed.is_valid():
        #     for idx, f in enumerate(files):
        #         if int(idx) == 0:
        #             save_media = DealMedia(business_deal=self.object, image=f,video=video)
        #             save_media.save()
        #         else:
        #             save_media = DealMedia(business_deal=self.object, image=f)
        #             save_media.save()
        if self.object.id != None:
            if form.is_valid() and formset.is_valid():
                formset.instance = self.object
                formset.save()
        return super().form_valid(form)




class DealUpdateView(UpdateView):
    model = BusinessDeal
    success_url = "/createdeal/"
    template_name = 'Business/update/businessdeal_form.html'
    form_class = UpdateBusinessDealForm

    def get_context_data(self, *args, **kwargs):
        context = super(DealUpdateView, self).get_context_data(**kwargs)
        bd_deal = BusinessDeal.objects.get(id=self.kwargs.get('pk'), is_deleted=False)
        bd_store = BusinessStore.objects.get(id=bd_deal.store.id, is_deleted=False)
        options = DifferentDealData.objects.get(deal=bd_deal)
        f_start_date = str(bd_deal.start_date)

        if self.request.method == 'POST':
            # global bd_store

            image = self.request.FILES.getlist('image')
            video = self.request.FILES.get('video')
            start_date = self.request.POST.get('start_date')

            reservation_fee = self.request.POST.get('reservation_fee')
            is_continue = self.request.POST.get('is_continue')
            is_featured = self.request.POST.get('is_featured')



            title2 = self.request.FILES.get('title2')
            quantity = self.request.FILES.get('quantity')
            discount_percentage = self.request.FILES.get('discount_percentage')


            if is_continue:
                is_continue = True
            else:
                is_continue = False
            

            if is_featured:
                is_featured = True
            else:
                is_featured = False

            # context["items"] = DifferentDealDataFormset(
            #     self.request.POST, instance=self.object
            # )
            # all_data = self.request.POST.get('huzaifadata')
            # country = ''
            # city = ''


            # if type(all_data) == str:
            #     all_data = all_data.replace('"[' , '[')
            #     all_data = all_data.replace(']"' , ']')
            #     all_data = json.loads(all_data)

            try:
                bd_deal = BusinessDeal.objects.get(id=self.kwargs.get('pk'), is_deleted=False)
                if start_date:
                    bd_deal.start_date = start_date

                    bd_deal.is_continue = is_continue

                    bd_deal.is_featured = is_featured
                    bd_deal.save()
            except Exception as err:
                print(err)
                pass
                            

            if title2:
                options.title = title2
            if quantity:
                options.quantity = quantity
            if reservation_fee:
                options.reservation_fee = reservation_fee

            if discount_percentage:
                options.discount_percentage=discount_percentage
                options.description = ''
            options.save()
            # for data in all_data:
            #     card_id = data.get('id' , None)
            #     created_ = data.get('created', None)
            #     is_deleted = data.get('is_deleted', None)
            #     if card_id is not None:
            #         try:
            #             card_obj = DifferentDealData.objects.get(id=card_id)
            #         except:
            #             pass
            #         else:
            #             title = data.get('title', card_obj.title)
            #             description = data.get('description', card_obj.description)
            #             price = data.get('price', card_obj.price)
            #             discount_percentage = data.get('discount', card_obj.discount_percentage)
            #             quantity = data.get('quantity', card_obj.quantity)

            #             card_obj.title = title
            #             card_obj.description = description
            #             card_obj.price = price
            #             card_obj.discount_percentage = discount_percentage
            #             card_obj.quantity = quantity
            #             card_obj.save()

            #     if created_ is not None:
            #         title = data.get('title', card_obj.title)
            #         description = data.get('description', card_obj.description)
            #         price = data.get('price', card_obj.price)
            #         discount_percentage = data.get('discount', card_obj.discount_percentage)
            #         quantity = data.get('quantity', card_obj.quantity)


            #         card_obj_1 = DifferentDealData(
            #             deal = bd_deal,
            #             title = title,
            #             description = description,
            #             price = price,
            #             discount_percentage = discount_percentage,
            #             quantity = quantity,
            #         )
            #         card_obj_1.save()

            #     if is_deleted is not None:
            #         try:
            #             deal_data = DifferentDealData.objects.get(id=card_id)
            #             deal_data.delete()
            #         except:
            #             pass

            if image:
                for i in image:
                    media = DealMedia.objects.create(business_deal=bd_deal, image=i)
            
            # if video:
            #     media = DealMedia.objects.create(business_deal=bd_deal, video=video)

            bd_deal.store = bd_store
            bd_deal.save()
            if bd_deal:
                if bd_deal.deal_status == 'Active':
                    bd_deal.status = True

                    # bd_deal.deal_status = 'Active'
                    # bd_deal.store = 'Active'

                    bd_deal.save()
                else:
                    bd_deal.status = False
                    # bd_deal.deal_status = 'Inctive'
                    bd_deal.save()

        else:
            
            searched_deall = BusinessDeal.objects.filter(create_by=self.request.user, is_deleted=False)
            stores = BusinessStore.objects.filter(user=self.request.user, store_status='Active', is_deleted=False).exclude(id=bd_deal.store.id)

            try:
                bd_deal = BusinessDeal.objects.get(id=self.kwargs.get('pk'), is_deleted=False)
            except Exception as err:
                pass

            country = bd_deal.country
            city = bd_deal.city
            category = bd_deal.category
            store = bd_deal.store
            select_sub_category = bd_deal.sub_category
            sub_categories = ''

            try:
                sub_categories = SubCategory.objects.filter(category__name__icontains=category)
            except:
                pass
            selected_cities = ''
            try:
                selected_cities = City.objects.filter(state__country__name__icontains=country).order_by('name')
            except:
                pass

            media = DealMedia.objects.filter(business_deal=bd_deal).exclude(image='')
            # bd_deal.store = bd_store
            bd_deal.save()
            if bd_deal:
                if bd_deal.deal_status == 'Active':
                    bd_deal.status = True
                    # bd_deal.deal_status = 'Active'
                    # bd_deal.store = 'Active'

                    bd_deal.save()
                else:
                    bd_deal.status = False
                    # bd_deal.deal_status = 'Inctive'
                    bd_deal.save()

            context['searched_deal'] = searched_deall
            context['options'] = options
            context['bd_store'] = bd_store

            context['media'] = media
            context['country'] = country
            context['city'] = city
            context['selected_cities'] = selected_cities

            context['bd_deal'] = bd_deal

            context['select_sub_category'] = select_sub_category
            context['sub_categories'] = sub_categories
            context['mediaform'] = DealMediaForm()
            context['start_date'] = f_start_date

            context['stores'] = stores
            # context["items"] = DifferentDealDataFormset(instance=self.object)
        return context
    def form_valid(self, form):
        context = self.get_context_data()
        # itemsformset = context["items"]
        # # if form.is_valid() and itemsformset.is_valid():
        # if form.is_valid():
        #     form.save()
        #     # itemsformset.save()
        # return super().form_valid(form)

        context = self.get_context_data()

        # formset = context["items"]
        self.object = form.save()

        form.instance.create_by = self.request.user
        self.object.save()
        formed = DealMediaForm(self.request.POST, self.request.FILES or None)
        video = self.request.FILES.get('video')
        if video:
            save_media = DealMedia.objects.create(business_deal=self.object, video=video)
        # if self.object.id != None:
        #     if form.is_valid() and formset.is_valid():
        #         formset.instance = self.object
        #         formset.save()

        return super().form_valid(form)

# def edit_deal(request, slug):
#     form = BusinessDealForm(request.POST)
#     # form_media = DealMediaForm()
#     # form_different = DifferentDealDataForm()
#     if request.method == 'POST':
#         try:
#             business_deal = BusinessDeal.objects.get(slug=slug)
#         except Exception as e:
#             print(e)
#         form = BusinessDealForm(request.POST, instance=business_deal)
#         # form_media = DealMediaForm()
#         # form_different = DifferentDealDataForm()
#         if form.is_valid():

#             form.save()
#             print('data saved')
#         else:
#             form = BusinessDealForm(instance=business_deal)
            
#     context = {
#         'form': form,
        
#     }
#     return render(request, 'Business/update/businessdeal_form.html', context)
    # context = ''
    # business_deal = BusinessDeal.objects.get(slug=slug)
    # form1 = BusinessDealForm(instance=business_deal)
    # different = DifferentDealData.objects.filter(deal=business_deal, is_delete=False)
    # for d in different:
    #     form2 = UpdateDifferentDealDataForm(instance=d)
    #     if request.method == 'POST':
    #         form1 = BusinessDealForm(request.POST or None, instance=business_deal)
    #         form2 = UpdateDifferentDealDataForm(request.POST or None, instance=d)
    #         if form1.is_valid() and form2.is_valid():
    #             f1=form1.save()
    #             f1.save()
    #             f2=form2.save(commit=False)
    #             f2.user=f1
    #             user2=f2.save()
    #             return redirect('/createdeal')
    #         else:
    #             form1 = BusinessDealForm(request.POST or None, instance=business_deal)
    #             form2 = UpdateDifferentDealDataForm(request.POST or None, instance=d)
    #     context = {
    #         'form1':form1,
    #         'form2':form2,
    #     }
    # return render(request, 'Business/update/businessdeal_form.html', context)





@csrf_exempt
def web_dynamic_content(request):
    # print(request.user.is_admin)
    if request.method == "POST":
        if request.user.is_authenticated and request.user.is_admin:
            try:
                user = request.user
                terms_conditions = request.POST.get('terms_conditions')
                privacy_policy = request.POST.get('privacy_policy')
                about_us = request.POST.get('about_us')

                text_content = WebDynamicContent.objects.first()

                if terms_conditions:
                    text_content.terms_conditions = terms_conditions
                if privacy_policy:
                    text_content.privacy_policy = privacy_policy
                if about_us:
                    text_content.about_us = about_us
                text_content.save()

                return redirect('admin_content')
            except Exception as e:
                return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('admin_content')



@csrf_exempt
def social_url(request):
    # print(request.user.is_admin)
    if request.user.is_admin:
        try:
            facebook_link = request.POST.get('facebook_link')
            instagram_link = request.POST.get('instagram_link')
            twitter_link = request.POST.get('twitter_link')

            user = request.user

            user.facebook_link = facebook_link
            user.instagram_link = instagram_link
            user.twitter_link = twitter_link

            user.save()

            return redirect('admin_profile')
        except Exception as e:
            return redirect('admin_profile')
    else:
        return redirect('admin_login')



@login_required(login_url='admin_login')
def remove_logo(request):
            try:
                logo = request.FILES.get('site_logo')
                user = User.objects.get(username=request.user, is_admin=True)
            except Exception as e:
                    print(e)
            user.logo = logo
            user.save()
            return redirect('admin_profile')

@login_required(login_url='home')
def remove_logo_business(request):
            try:
                logo = request.FILES.get('site_logo')
                user = User.objects.get(username=request.user,user_type="Business")
                user.logo = logo
                user.save()
            except Exception as e:
                    print(e)
            return redirect('business_settings')

def edit_deal_function(request ,id):
    get_deal = BusinessDeal.objects.get(id=id, is_deleted=False)
    serializer = DealSerializer(get_deal).data
    get_multiple_deals = DifferentDealData.objects.filter(deal=get_deal)
    serialized_multiple_deal = MultipleDealSerializer(get_multiple_deals, many=True).data
    data = {'serializer':serializer,'serialized_multiple_deal':serialized_multiple_deal}
    print(data,'0000')
    return JsonResponse(data)


def verify_email_for_new_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email, is_active=True)
            random_digits_for_code = ''.join(
                random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
            verification = VerificationCode.objects.create(code=random_digits_for_code, user=user)
            # body = "Your Top Deal Email Varification code is " + str(verification.code)
            # data = {
            #     'subject': "Your Top Deal Forgot password Email",
            #     'body': body,
            #     'to_email': user.email
            # }
            # Utill.send_email(data)
            html_template = render_to_string('email/u-forgot-password.html',
                                                 {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
            text_template = strip_tags(html_template)
            send_email = EmailMultiAlternatives(
                'Top-Deals | Verification Code',
                text_template,
                settings.EMAIL_HOST_USER,
                [email]
            )
            send_email.attach_alternative(html_template, "text/html")
            return redirect(f'/verify_email/{user.id}')
        except Exception as e:
            messages.error(request, 'Your email does not exist!')
            return redirect('home')
    return redirect('home')


def resend_code_reg_user(request, id):
    if request.method == 'GET':
        # email = request.POST.get('email', None)
        try:
            user = User.objects.get(email=id)
        except Exception as e:
            messages.error(request, "your email does not exists!")
            return redirect('home')
        codes = VerificationCode.objects.filter(user=user, is_expired=False)
        if codes:
            for i in codes:
                i.is_expired = True
                i.used = True
                i.save()
        random_digits_for_code = ''.join(
            random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
        verification = VerificationCode.objects.create(user=user, code=random_digits_for_code)
        # body = "Your Top Deal Email Varification code is " + str(verification.code)
        # data = {
        #     'subject': "Your Top Deal Sign Up Email",
        #     'body': body,
        #     'to_email': user.email
        # }
        # Utill.send_email(data)
        html_template = render_to_string('email/u-forgot-password.html',
                                            {'code': verification.code, 'img_link': settings.DOMAIN_NAME})
        text_template = strip_tags(html_template)
        send_email = EmailMultiAlternatives(
            'Top-Deals | Verification Code',
            text_template,
            settings.EMAIL_HOST_USER,
            [email]
        )
        send_email.attach_alternative(html_template, "text/html")
        return redirect(f'/verify_email/{user.id}')
    return render(request, 'Store/home.html')



def user_listed(request):
    """admin will see the list of all customer users from admin panel"""
    if request.user.is_superuser and request.user.is_admin:
        if request.method == "GET":
            try:
                item = request.GET.get('item')
                if item:
                    users = User.objects.filter((Q(username__icontains=item) | Q(name__icontains=item) | Q(name__icontains=item)), is_active=True,
                                    user_type='Customer', is_staff=False, is_admin=False, is_superuser=False, is_account_officer=False).order_by('-date_joined')
                else:
                    users = User.objects.filter(is_active=True, user_type='Customer', is_staff=False, is_admin=False,
                                              is_superuser=False, is_account_officer=False).order_by('-date_joined')
                return render(request, 'Admin/customers.html', {'users':users})
            except Exception as e:
                messages.error(request, 'Something wrong.')
                return redirect('home')
    return redirect('admin_login')



def news_letter(request):
    """any user will subscribe the site to get update notificaiton of platform"""
    from store.constant import email_validator
    if request.method == "POST":
        try:
            email = request.POST.get('email')
            email_validate = email_validator(email)
            find_email = NewsLetter.objects.filter(email=email)
            if find_email:
                messages.success(request, 'You already subscribed the platform.')
                return redirect('home')
            if email_validate and not find_email:
                html_template = render_to_string('email/newsletter.html',
                                                {'img_link': settings.DOMAIN_NAME})
                text_template = strip_tags(html_template)
                # Getting Email ready
                send_email = EmailMultiAlternatives(
                    'Top-Deals | Subscription Email',
                    text_template,
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                send_email.attach_alternative(html_template, "text/html")
                try:
                    send_email.send(fail_silently=False)
                except:
                    return redirect('home')
                NewsLetter.objects.create(email=email)
            else:
                messages.error(request, 'Please enter valid email.')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'Something wrong.')
            return redirect('home')
    return redirect('home')



def sort_deals(request):
    context = {}
    sorted_by = request.GET.get('sorted_by')

    if sorted_by == 'hightolow':
        dealfilter = BusinessDeal.objects.filter(category__status = 'Active', store__status=True, status=True, is_expired=False, is_deleted=False).order_by('-price')

    if sorted_by == 'lowtohigh':
        dealfilter = BusinessDeal.objects.filter(category__status = 'Active', store__status=True, status=True, is_expired=False, is_deleted=False).order_by('price')

    if sorted_by == 'popular':
        dealfilter = BusinessDeal.objects.filter(category__status = 'Active', store__status=True, status=True, is_expired=False, is_deleted=False)

    if sorted_by == 'trendy':
        dealfilter = BusinessDeal.objects.filter(category__status = 'Active', store__status=True, status=True, is_expired=False, is_deleted=False)

    else:
        dealfilter = BusinessDeal.objects.filter(category__status = 'Active', store__status=True, status=True, is_expired=False, is_deleted=False).order_by('-created_at')
    
    context['dealfilter'] = dealfilter

    return render(request, 'Store/category_detail.html', context)


def get_webcontent(request):
    content = WebDynamicContent.objects.first().terms_conditions

    return render(request, 'Admin/term-condition.html', {'content':content})


def privacy(request):
    content = WebDynamicContent.objects.first().privacy_policy
    

    return render(request, 'Admin/privacy.html', {'content':content})


def get_faqs(request):
    content = WebDynamicContent.objects.first().faq
    # content = ''

    return render(request, 'Admin/faqs.html', {'content':content})


def get_contact_us(request):
    content = WebDynamicContent.objects.first().contact_us
    # content = ''

    return render(request, 'Admin/contact-us.html', {'content':content})

def get_about_us(request):
    content = WebDynamicContent.objects.first().about_us

    return render(request, 'Admin/about-us.html', {'content':content})



def nearby_deals(request):
    try:
        top_offers = BusinessDeal.objects.filter(is_deleted=False, is_expired=False,
                                                 store__store_status='Active').filter(~Q(lat=None, lon=None))

        serializer = HomeDealSerializer(top_offers, many=True)
    except:
        pass
    # officer = Account_Officer.objects.get(id=id)
    # get_user = User.objects.get(username=officer.user)
    # # serialize_now = UserSerializer(get_user).data
    # serialize_now = DefaultUserSerializer(get_user).data
    # serializer = AccountOfficerSerializer(officer).data
    data = {'serializer':serializer.data}
    return JsonResponse(data)


# def check_daily_deal(request, slug):
#     current_time = time.ctime()

#     try:
#         my_deal = BusinessDeal.objects.get(is_deleted=False, is_expired=False,  start_time__gte=current_time, 
#                                                 end_time__lte=current_time,
#                                                  store__store_status='Active')

#     except:
#         pass

#     my_deal.is_expired = True
#     my_deal.save()


def merchant_login(request):
    return render(request, 'Store/business-signup.html')


def all_cat(request):
    category = Category.objects.filter(status='Active')
    subcategory = Category.objects.filter(status='Active')
    context={
        'category': category,
        'subcategory': subcategory,
    }
    return render(request, 'Store/all-categories.html', context)

    
def search_all(request):
    sub_category = request.GET.get('sub_category', None)
    city = request.GET.get('city', None)
    search_by = request.GET.get('search_by', None)
    
    get_sub_category = SubCategory.objects.filter(status='Active')

    try:
        sub_category = SubCategory.objects.get(slug=sub_category)
        sub_category = sub_category.name
    except:
        pass

    # try:
    #     city = City.objects.get(id=city)
    #     city = city.name
    # except:
    #     pass


    if sub_category and city and search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        Q(store__name__icontains=search_by) |
                                        Q(category__name__icontains=search_by) |
                                        Q(country__name__icontains=search_by) |
                                        Q(title__icontains=search_by)|
                                        Q(description__icontains=search_by) |
                                       
                                        Q(gender__icontains=search_by),
                                        deal_status = 'Active',
                                        sub_category__name__icontains=sub_category,
                                        city__name__icontains = city,
                                        status = True,
                                         is_deleted=False)
    elif sub_category and city and not search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        deal_status = 'Active',
                                        sub_category__name__icontains=sub_category,
                                        city__name__icontains = city,
                                        status = True,
                                         is_deleted=False)
    elif sub_category and not city and search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        Q(store__name__icontains=search_by) |
                                        Q(category__name__icontains=search_by) |
                                        Q(country__name__icontains=search_by) |
                                        Q(title__icontains=search_by)|
                                        Q(description__icontains=search_by) |
                                        
                                        Q(gender__icontains=search_by),
                                        deal_status = 'Active',
                                        sub_category__name__icontains=sub_category,
                                        status = True,
                                         is_deleted=False)
    elif sub_category and not city and not search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        
                                        deal_status = 'Active',
                                        sub_category__name__icontains=sub_category,
                                        status = True,
                                         is_deleted=False)
    elif not sub_category and city and search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        Q(store__name__icontains=search_by) |
                                        Q(category__name__icontains=search_by) |
                                        Q(country__name__icontains=search_by) |
                                        Q(title__icontains=search_by)|
                                        Q(description__icontains=search_by) |

                                        Q(gender__icontains=search_by),
                                        deal_status = 'Active',
                                        city__name__icontains = city,
                                        status = True,
                                         is_deleted=False)
    elif not sub_category and city and not search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        deal_status = 'Active',
                                        city__name__icontains = city,
                                        status = True,
                                         is_deleted=False)
    elif sub_category and city and not search_by:
        dealfilter = BusinessDeal.objects.filter(
                                        
                                        deal_status = 'Active',
                                        sub_category__name__icontains=sub_category,
                                        city__name__icontains = city,
                                        status = True,
                                         is_deleted=False)
    elif not sub_category and not city and search_by:
        dealfilter = BusinessDeal.objects.filter(
                                                    Q(title__icontains=search_by)|
                                        Q(store__name__icontains=search_by) |
                                        Q(category__name__icontains=search_by) |
                                        Q(country__name__icontains=search_by) |

                                        Q(description__icontains=search_by) |
                                        
                                        Q(gender__icontains=search_by),
                                        deal_status = 'Active',
                                        status = True,
                                        is_deleted=False)
    else:
        dealfilter = BusinessDeal.objects.filter(
                                        deal_status = 'Active',
                                        status = True,
                                         is_deleted=False)
    print('*********', dealfilter)
    context = {
        'dealfilter' :dealfilter,
        'get_sub_category':get_sub_category,
        'search':True
    }

    return render(request, 'Business/search.html', context)


