import json
from rest_framework.response import Response
from django.db.models import Q, Count
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from django.contrib.auth import authenticate, logout
import random, string
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from Constants.Emails import send_order_email_to_customer

import store.models
from store.constant import password_validator
from store.serializer import *
from store.models import *
from store.utils import Utill

from django.views.decorators.csrf import csrf_exempt
from threading import Thread

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def get_countries(request):
    countries = Country.objects.all()
    serializer = CountrySerializer(countries, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request):
    country = request.query_params.get('country', None)
    if not country:
        return Response({"success": False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        country = Country.objects.get(id=country)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    cities = City.objects.filter(state__country=country)
    serializer = CitySerializer(cities, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_currency(request):
    currencies = Currency.objects.all()
    serializer = CurrencySerializer(currencies, many=True)
    return Response({'success': True, 'message': serializer.data},
                                            status=status.HTTP_200_OK)
                                            

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    last_name = request.data['last_name'] if 'last_name' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    business_address = request.data['business_address'] if 'business_address' in request.data else None
    phone = request.data['phone'] if 'phone' in request.data else None
    dial_code = request.data['dial_code'] if 'dial_code' in request.data else None
    license_id = request.data['license_id'] if 'license_id' in request.data else None
    license_document = request.data['license_document'] if 'license_document' in request.data else None
    email = request.data.get('email').lower() if 'email' in request.data else None
    password = request.data['password'] if 'password' in request.data else None
    user_type = request.data['user_type'] if 'user_type' in request.data else None
    country = request.data['country'] if 'country' in request.data else None
    city = request.data['city'] if 'city' in request.data else None
    category = request.data['category'] if 'category' in request.data else None
    
    lat = request.data.get('lat', None)
    long = request.data.get('long', None)


    if not user_type:
        return Response({"success": False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not email:
        return Response({"success": False, 'response': 'Email is required for Sign Up!'},
                        status=status.HTTP_400_BAD_REQUEST)
    if email:
        user = User.objects.filter(email=email).first()
        if user:
            return Response({"success": False, 'response': 'Unique email is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

    if user_type == 'Business':
        if not first_name:
            return Response({"success": False, 'response': 'First Name is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not last_name:
            return Response({"success": False, 'response': 'Last Name is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not business_address:
            return Response({"success": False, 'response': 'Buusiness Address is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not country:
            return Response({"success": False, 'response': 'Country is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not city:
            return Response({"success": False, 'response': 'City is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not category:
            return Response({"success": False, 'response': 'Category is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not license_id:
            return Response({"success": False, 'response': 'License Id is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not license_document:
            return Response({"success": False, 'response': 'License Document is required for Sign Up!'},
                            status=status.HTTP_400_BAD_REQUEST)

    else:
        user_type = 'Customer'

    if not name:
        return Response({"success": False, 'response': 'Name is required for Sign Up!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not phone:
        return Response({"success": False, 'response': 'Phone is required for Sign Up!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not password:
        return Response({"success": False, 'response': 'Password is required for Sign Up!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if len(password) < 8:
        return Response({"success": False, 'response': 'Please enter a strong password!'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        return Response({"success": False, 'response': 'User with this email address is already registered!'},
                        status=status.HTTP_400_BAD_REQUEST)
    except:
        pass
    
    
    
    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    verification = VerificationCode.objects.create(code=random_digits_for_code)
    html_template = render_to_string('email/verification-code.html',
                                     {'verification_code': verification.code, 'img_link': settings.DOMAIN_NAME})
    text_template = strip_tags(html_template)
    # Getting Email ready
    send_email = EmailMultiAlternatives(
        'Top-Deals | Verification Code',
        text_template,
        settings.EMAIL_HOST_USER,
        [email]
    )
    send_email.attach_alternative(html_template, "text/html")

    # try:
    #     # send_email.send(fail_silently=False)
    #     body = "Your Top Deal Email Varification code is " + str(verification.code)
    #     data = {
    #         'subject': "Your Top Deal Sign Up Email",
    #         'body': body,
    #         'to_email': email
    #     }
    #     Utill.send_email(data)
    # except:
    #     return Response({"success": False, 'response': 'Email server failed!'},
    #                     status=status.HTTP_503_SERVICE_UNAVAILABLE)

    if country:
        try:
            country = Country.objects.get(id=country)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if city:
        try:
            city = City.objects.get(id=city)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)
    if category:
        try:
            category = Category.objects.get(id=category)
        except Exception as e:
            return Response({"success": False, 'response': {'message': str(e)}},
                            status=status.HTTP_404_NOT_FOUND)

    username = email.split('@')[0]
    user = User.objects.create(
        first_name=first_name,
        last_name=last_name,
        name=name,
        business_address=business_address,
        email=email,
        phone=phone,
        dial_code=dial_code,
        user_type=user_type,
        license_id=license_id,
        username=username,
        is_active=False,
    )
    

    user.license_document = license_document
    user.country = country
    user.city = city
    user.category = category
    user.set_password(password)
    user.save()
    verification.user = user
    verification.save()
    
    if user.user_type == 'Business':
        business_store = BusinessStore.objects.create(
            user = user,
            name=name,
            store_address=business_address,
            country = country,
            license_id = license_id,
            city = city,
            license_document = license_document,
            category = category
        )
        lat = Decimal(lat)
        lng = Decimal(long)
        store_location = StoreLocation.objects.create(
            business_store=business_store, 
            adress=business_address, 
            status=True, 
            city=city, 
            lat=lat, 
            lng=lng
            )
    
    return Response(
        {"success": True, 'response': 'Sign Up Successful, verify Your Email!'},
        status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data['email'].lower().strip() if 'email' in request.data else None
    password = request.data['password'] if 'password' in request.data else None

    if not email or not password:
        return Response({"success": False, 'response': {'message': 'Invalid Data!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if email is not None:
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"success": False, 'response': {'message': 'Sorry! User not Found.'}},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email, is_active=True)
            username = user.username
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Sorry! User is Inactive.'}},
                            status=status.HTTP_404_NOT_FOUND)
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"success": False, 'response': {'message': 'Incorrect User Credentials!'}},
                            status=status.HTTP_403_FORBIDDEN)
        else:
            """
            Creating new token 
            """
            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)
            access_token = token.key
    serializer = DefaultUserSerializer(user)

    return Response({'success': True, 'access_token': access_token, 'response': {'profile': serializer.data}},
                    status=status.HTTP_201_CREATED)


class Logout(APIView):
    def get(self, request, format=None):
        # simply delete the token to force a login
        Token.objects.get(user=request.user).delete()
        # return Response(status=status.HTTP_200_OK)
        return Response({'success': True, 'message': 'user logout'},
                        status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    email = request.data['email'].lower().strip() if 'email' in request.data else None
    code = request.data['code'] if 'code' in request.data else None
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'requested user does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        verified = VerificationCode.objects.get(user=user, code=code, used=False, is_expired=False)
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    verified.is_expired = False
    verified.used = True
    verified.save()
    if not user.is_active:
        user.is_active = True
        user.save()
        # Send Email For Welcome.
        html_template = render_to_string('email/welcome-email.html', {'img_link': settings.DOMAIN_NAME,
                                                                        'frontend_domain': settings.FRONTEND_SERVER_NAME})
        text_template = strip_tags(html_template)
        email = EmailMultiAlternatives(
            'Welcome to Top-Deals',
            text_template,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        email.attach_alternative(html_template, "text/html")
        try:
            email.send(fail_silently=False)
        except:
            return Response({'success': False, 'message': 'There is an issue with Email Host Server'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)

    try:
        user = User.objects.get(id=user.id, is_active=True)
        serializer = DefaultUserSerializer(user)
        return Response({'success': True, 'token': str(user.auth_token), 'profile': serializer.data, 'response': {'message': {'id': user.id, 'user_type':user.user_type}}},
                        status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'success': True, 'response': {'message': 'user is not active!'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_code(request):
    email = request.data['email'] if 'email' in request.data else None
    # Generating random Code
    try:
        user = User.objects.get(email=email)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Sorry! User with this email does not exist'}},
                        status=status.HTTP_404_NOT_FOUND)

    codes = VerificationCode.objects.filter(user=user, is_expired=False)
    for i in codes:
        i.is_expired = True
        i.used = True
        i.save()

    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits) for _ in range(4))
    verification = VerificationCode.objects.create(user=user, code=random_digits_for_code)
    html_template = render_to_string('email/u-forgot-password.html',
                                     {'verification_code': verification.code, 'img_link': settings.DOMAIN_NAME}
                                     )
    text_template = strip_tags(html_template)

    # Getting Email ready
    email = EmailMultiAlternatives(
        'Top-Deals | Verification Code',
        text_template,
        settings.EMAIL_HOST_USER,
        [user.email]
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send(fail_silently=False)
        return Response({'success': True, 'response': {'message': 'Verification code sent'}},
                        status=status.HTTP_201_CREATED)
    except:
        return Response({'success': False, 'response': {'message': 'There is an issue with Email Host Server'}},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data['email'].lower().strip() if 'email' in request.data else None
    password1 = request.data['password1'] if 'password1' in request.data else None
    password2 = request.data['password2'] if 'password2' in request.data else None
    code = request.data['code'] if 'code' in request.data else None

    if not email or not password2 or not password1 or not code:
        return Response({'success': False, 'response': {'message': 'Invalid data'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if password1 != password2:
        return Response({'success': False, 'response': {'message': 'Password do not match'}},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email, is_active=True)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'User not found against given email!'}},
                        status=status.HTTP_404_NOT_FOUND)

    try:
        code = VerificationCode.objects.get(user=user, code=code)
    except ObjectDoesNotExist:
        return Response({'success': False, 'response': {'message': 'Invalid Code!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if not len(password1) < 8:
        user.set_password(password1)
        user.save()
        return Response({'success': True, 'response': {'message': 'Password reset successfully!'}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': 'Password should be 8 letters long!'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data['old_password'] if 'old_password' in request.data else None
    password1 = request.data['password1'] if 'password1' in request.data else None
    password2 = request.data['password2'] if 'password2' in request.data else None
    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)
    if not old_password or not password1 or not password2:
        return Response({'success': False, 'response': {'message': 'Invalid data!'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if not user.check_password(old_password):
        return Response({'success': False, 'response': {'message': 'Invalid Old Password!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if password1 != password2:
        return Response({'success': False, 'response': {'message': 'Password not matched!'}},
                        status=status.HTTP_400_BAD_REQUEST)
    if not len(password1) < 8:
        user.set_password(password1)
        user.save()
        return Response({'success': True, 'response': {'message': 'Password changed successfully!'}},
                        status=status.HTTP_201_CREATED)
    else:
        return Response({'success': False, 'response': {'message': 'Password should be 8 letters long!'}},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data['email']
    try:
        user = User.objects.get(email=email, is_active=True)
    except ObjectDoesNotExist:
        return Response(
            {'success': False, 'response': {'message': 'User with the given email address does not exist!'}},
            status=status.HTTP_404_NOT_FOUND)
    # Generating random Code
    random_digits_for_code = ''.join(
        random.SystemRandom().choice(string.digits + string.digits)
        for _ in range(4))
    verificaton = VerificationCode.objects.create(
        user=user,
        code=random_digits_for_code
    )
    html_template = render_to_string('email/u-forgot-password.html',
                                     {
                                         'verification_code': verificaton.code,
                                         'img_link': settings.DOMAIN_NAME,
                                     })
    text_template = strip_tags(html_template)
    # Getting Email ready
    email = EmailMultiAlternatives(
        'Top-Deals | Forgot Password',
        text_template,
        settings.EMAIL_HOST_USER,
        [user.email],
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send(fail_silently=False)
    except Exception as e:
        return Response({'success': False,
                         'message': 'There is an issue with Email Host Server'},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({'success': True,
                     'message': 'Verification code has been sent to your provided Email'},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_404_NOT_FOUND)
    serializer = DefaultUserSerializer(user)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    id = request.data['id'] if 'id' in request.data else None
    first_name = request.data['first_name'] if 'first_name' in request.data else None
    last_name = request.data['last_name'] if 'last_name' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    business_address = request.data['business_address'] if 'business_address' in request.data else None
    phone = request.data['phone'] if 'phone' in request.data else None
    license_id = request.data['license_id'] if 'license_id' in request.data else None
    license_document = request.data['license_document'] if 'license_document' in request.data else None
    location_business = request.data['location_business'] if 'location_business' in request.data else None
    email = request.data.get('email').lower() if 'email' in request.data else None
    password = request.data['password'] if 'password' in request.data else None
    user_type = request.data['user_type'] if 'user_type' in request.data else None

    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    if user.user_type == 'Business':
        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name

        if business_address:
            user.business_address = business_address

        if license_id:
            user.license_id = license_id

        if license_document:
            user.license_document = license_document

        if location_business:
            user.license_document = license_document

    if name:
        user.name = name
    user.save()
    serializer = DefaultUserSerializer(user)

    return Response({'success': True, 'response': {'profile': serializer.data}},
                    status=status.HTTP_200_OK)


# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_profile(request):
#     try:
#         user = request.user
#     except Exception as e:
#         return Response({'success': False, 'response': {'message': str(e)}},
#                         status=status.HTTP_404_NOT_FOUND)

#     if user.deleteaccountrequest_user.filter(approved=False, is_deleted=False):
#         return Response({'success': False, 'message': 'You already sent request, wait for approve!'},
#                                     status=status.HTTP_400_BAD_REQUEST)

#     delete_account = DeleteAccountRequest.objects.create(user=user)
#     return Response({'success': True, 'message': 'Your Account delete request sent!'},
#                                     status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request):
    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    name = request.data['name'] if 'name' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    if not name or not image:
        return Response({'success': False, 'message': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    category = Category.objects.create(name=name, image=image, user=user)

    serializer = CategorySerializer(category)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_categories(request):
    category = Category.objects.filter(is_deleted=False)

    serializer = CategorySerializer(category, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_category(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'message': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        category = Category.objects.get(id=id, is_deleted=False)
        subcategory = SubCategory.objects.filter(category=id, is_deleted=False).all()
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)
    category.status = 'Inactive'
    category.is_deleted = True
    category.save()
    for sub in subcategory:
        sub.status='Inactive'
        sub.is_deleted = True
        sub.save()

    return Response({'success': True, 'message': 'Category Deleted Successfully!'},
                    status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request):
    id = request.data['id'] if 'id' in request.data else None
    if not id:
        return Response({'success': False, 'message': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        user = request.user
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_401_UNAUTHORIZED)

    name = request.data['name'] if 'name' in request.data else None
    image = request.data['image'] if 'image' in request.data else None
    try:
        category = Category.objects.get(id=id, is_deleted=False)
        if name:
            category.name = name
        if image:
            category.image = image
        category.save()
    except Exception as e:
        return Response({'success': False, 'response': {'message': str(e)}},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(category)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


################### STORE #############################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_store(request):
    category = request.data['category'] if 'category' in request.data else None
    country = request.data['country'] if 'country' in request.data else None
    currency = request.data['currency'] if 'currency' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    deal_price = request.data['deal_price'] if 'deal_price' in request.data else None
    billing_reccurence = request.data['billing_reccurence'] if 'billing_reccurence' in request.data else None
    # image = request.data['image'] if 'image' in request.data else None
    lat = request.data['lat'] if 'lat' in request.data else None
    lon = request.data['lon'] if 'lon' in request.data else None
    web_url = request.data['web_url'] if 'web_url' in request.data else None
    pin_code = request.data['pin_code'] if 'pin_code' in request.data else None
    subcategory = request.data.get('subcategory', None)

    address = request.data['store_address'] if 'store_address' in request.data else None
    # location = request.data['location'] if 'location' in request.data else None
    city = request.data['city'] if 'city' in request.data else None
    lat = request.data['lat'] if 'lat' in request.data else None
    lng = request.data['lng'] if 'lng' in request.data else None

    user = request.user

    # if not name or not description or not country \
    #         or not category or not currency or not deal_price or not billing_reccurence:
    #     return Response({"success": False, 'response': 'Invalid Data!'},
    #                     status=status.HTTP_400_BAD_REQUEST)
    try:
        business_store = BusinessStore.objects.get(user=user.id, store_status='Pending')
        return Response({'success': True, 'message': "Your store is already in pending!"},
                status=status.HTTP_200_OK)
    except Exception as e:
        pass

    request.data._mutable = True

    # first_store = BusinessStore.objects.filter(user=user.id, is_deleted=False)
    # user_store = first_store.filter(user=user.id, is_deleted=False) dont user this
    if user:
        if user.user_type != "Business" and user.business_status != "Approved":
            return Response({'success': False, 'message': "User Should be Approved and Bussiness User"},
                            status=status.HTTP_400_BAD_REQUEST)
        request.data['user'] = user.id
        serializer = StoreSerializer(data=request.data, context={'request': request})
        # serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            business_store = serializer.save()
            # if type(subcategory)== str:
            #     subcategory = json.loads(subcategory)
            
            if subcategory:
                if type(subcategory) == str:
                    subcategory = json.loads(subcategory)
                
                for s in subcategory:
                    try:
                        sub = SubCategory.objects.get(id=s)
                        business_store.subcategory.add(sub)
                    except Exception as err:
                        print(err)

            if address or city or lat or lng is not None:
                print(address)
                lat = Decimal(lat)
                lng = Decimal(lng)
                store_location = StoreLocation.objects.create(business_store=business_store, adress=address, status=True, city_id=city, lat=lat, lng=lng)
            # for i in image:
            #     StoreMedia.objects.create(business_store=business_store, image=image)
            # serializer = GetStoreSerializer(business_store)
            if category:
                check_store = BusinessStore.objects.filter(user=user.id, store_status='Active', category=category)
                if check_store:
                    #business_store.verification_status = 'Verified'
                    business_store.store_status = 'Active'
                    business_store.save()
            serializer = StoreGetSerializer(business_store)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'message': serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
    # elif first_store and user.business_status != "Approved":
    #     return Response({'success': False, 'message': "Please approve your first store form admin"},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # elif first_store and user.business_status == 'Approved':
    #     request.data['status']=True
    #     serializer = StoreSerializer(data=request.data, context={'request': request})
    #     # serializer = StoreSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         # for i in image:
    #         #     StoreMedia.objects.create(business_store=business_store, image=image)
    #         # serializer = GetStoreSerializer(business_store)
    #         return Response({'success': True, 'message': serializer.data},
    #                         status=status.HTTP_201_CREATED)
    #     else:
    #         return Response({'success': False, 'message': serializer.errors},
    #                         status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'success': False, 'message': "User Not Found"},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_store(request):
    id = request.data['id'] if 'id' in request.data else None
    user = request.user

    if not id:
        return Response({'success': False, 'message': 'Invalid data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        business_store = BusinessStore.objects.get(id=id, is_deleted=False)
        if user == business_store.user:
            business_store.is_deleted = True
            business_store.status = False
            business_store.save()
            deals = BusinessDeal.objects.filter(store=id, is_deleted=False).all()
            for deal in deals:
                deal.is_deleted=True
                deal.save()
            return Response({'success': True, 'message': 'Store deleted Successfuly!'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'message': 'You have no permission to delete store!'},
                            status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'message': str(e)},
                        status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stores(request): # list perticular user store
    user = request.user
    business_store = BusinessStore.objects.filter(user=user, is_deleted=False)
    # serializer = GetStoreSerializer(business_store, many=True)
    serializer = StoreSerializer(business_store, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_store(request):
    subcategory = request.data.get('subcategory', None)
    user = request.user
    id = request.data.get('id', None)
    
    category = request.data.get('category', None)
    country = request.data.get('country', None)
    currency = request.data.get('currency', None)
    city = request.data.get('city', None)
    
    store_address = request.data.get('store_address', None)
    billing_reccurence = request.data.get('billing_reccurence', None)
    store_status = request.data.get('store_status', None)
    
    name = request.data.get('name', None)
    description = request.data.get('description', None)
    
    image = request.data.get('business_logo', None)
    deal_price = request.data.get('deal_price', None)
    
    if id is None:
        return Response(
            {
                'success': False,
                'message': 'Invalid data!',
                'fields' : 'id'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business_store = BusinessStore.objects.get(id=id, is_deleted=False)
        
    except Exception as e:
        print('TTTTTTTTTTT', e)
        return Response({'success': False, 'message': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
    if user == business_store.user:
        
        if subcategory is not None:
            if type(subcategory) ==  str:
                subcategory = json.loads(subcategory)
            #for rev in business_store.subcategory.clear():
                
            business_store.subcategory.clear()
            
            for sub in subcategory:
                try:
                    subcate = SubCategory.objects.get(id = sub )
                    business_store.subcategory.add(subcate)
                    print(subcate)
                except Exception as err:
                    print('SubCategory error',err)

            business_store.save()  
        if category:
            try:
                category = Category.objects.get(id = category )
                business_store.category = category
            except Exception as err:
                category = None
        if country:    
            try:
                country = Country.objects.get(id = country)
                business_store.country = country
            except Exception as err:
                country = None
        if city:
            try:
                city_id = City.objects.get(id = city)
                business_store.city = city_id
            except Exception as err:
                city_id = None
        if currency:
            try:
                currency = Currency.objects.get(id = currency)
                business_store.currency = currency
            except Exception as err:
                currency = None
                
         #request.data.get('category', business_store.category )
          #request.data.get('country', business_store.country )
          #request.data.get('country', business_store.country )
         #request.data.get('currency', business_store.currency )
        #business_store.billing_reccurence = request.data.get('billing_reccurence', business_store.billing_reccurence )
        #business_store.store_address = request.data.get('store_address', business_store.store_address )
        #business_store.store_status = request.data.get('store_status', business_store.store_status )
        #business_store.store_address = request.data.get('location', business_store.store_status )
        
        # if category:
        #     try:
        #         category = Category.objects.get(id=category)
        #     except Exception as e:
        #         return Response({'success': False, 'message': str(e)},
        #                         status=status.HTTP_404_NOT_FOUND)
        #
        #     business_store.category = category
        #
        # if country:
        #     try:
        #         country = Country.objects.get(id=country)
        #     except Exception as e:
        #         return Response({'success': False, 'message': str(e)},
        #                         status=status.HTTP_404_NOT_FOUND)
        #     business_store.country = country
        #
        # if currency:
        #     try:
        #         currency = Currency.objects.get(id=currency)
        #     except Exception as e:
        #         return Response({'success': False, 'message': str(e)},
        #                         status=status.HTTP_404_NOT_FOUND)
        #     business_store.currency = currency
        #
        if billing_reccurence:
            business_store.billing_reccurence = billing_reccurence
            
        if store_address:
            business_store.store_address = store_address
        
        try:
            busines_deal = BusinessDeal.objects.get(store = business_store)
        except Exception as err:
            print(err)
        
        if store_status:
            business_store.store_status = store_status
            if store_status == 'Inactive':
                try:
                    busines_deal.deal_status = store_status
                    busines_deal.save()
                except Exception as err:
                    print(err)
            
        if name:
            business_store.name = name
        
        if description:
            business_store.description = description
        
        if deal_price:
            business_store.deal_price = deal_price
        if image:
            business_store.business_logo = image
        business_store.save()
        # request.data._mutable = True
        # request.data['user'] = user.id.
        
        try:
            request.data._mutable = True
        except:
            pass
        r_data = request.data
        del r_data['subcategory']
        print(r_data)
        # serializer = StoreSerializer(business_store, data=r_data,  partial=True, context={'request': request},)
        # if not serializer.is_valid():
        #     return Response(
        #             {
        #         'status' : False,
        #         'response' : {
        #             'message' : 'Store Serializer Invalid',
        #             'error_message' : str(serializer.errors),
        #         }
        #     },
        #     status=status.HTTP_404_NOT_FOUND
        # )
        # # serializer.is_valid(raise_exception=True)
        # serializer.save()

        serializer = StoreSerializer(business_store,)
        return Response({'success': True, 'message': serializer.data},
                        status=status.HTTP_200_OK)

    #     if store.store_status == "Inactive" or store.status is False:
    #         all_deals = BusinessDeal.objects.filter(Q(store=store.id, status=True, is_deleted=False) | Q(store=store.id, deal_status="Active", is_deleted=False))
    #         if all_deals:
    #             for deal in all_deals:
    #                 deal.deal_status = "Inactive"
    #                 deal.status = False
    #                 deal.save()
    #     # serializer = GetStoreSerializer(business_store)
    #     return Response({'success': True, 'message': serializer.data},
    #                     status=status.HTTP_200_OK)
    # else:
    #     return Response({'success': False, 'message': 'You have no permission to Update store!'},
    #                     status=status.HTTP_400_BAD_REQUEST)
        
        
        
    # except Exception as e:
    #     return Response({'success': False, 'message': str(e)},
    #                         status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_social_login(request):
    email = request.data['email'] if 'email' in request.data else None
    phone = request.data['phone'] if 'phone' in request.data else None
    name = request.data['name'] if 'name' in request.data else None
    social_id = request.data['social_id'] if 'social_id' in request.data else None
    social_platform = request.data['social_platform'] if 'social_platform' in request.data else None

    # if not name or not phone or not social_platform:
    if not name or not social_platform:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if not email and not social_id:
        return Response({'success': False, 'response': {'message': 'Invalid Data'}},
                        status=status.HTTP_400_BAD_REQUEST)

    if not email:
        email = f"{social_id}@{social_platform}.com"
    username = email.split('@')[0]

    try:
        user = User.objects.get(email=email)
        password = user.password
    except:
        username = email.split('@')[0]
        user = User.objects.create(
            name=name,
            email=email,
            phone=phone,
            username=username,
            is_active=True,
            user_type='Customer'
        )
        user.set_password('User123$')
        user.save()

    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    access_token = token.key
    serializer = DefaultUserSerializer(user)

    return Response({'success': True, 'response': {'user': serializer.data, 'profile': serializer.data, 'access_token': access_token}},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_subcategory_deals(request):
    subcategory = request.GET.get('subcategory', None)
    if subcategory == 'all':
        busines_deal = BusinessDeal.objects.all()
    else:
        busines_deal = BusinessDeal.objects.filter(store__subcategory__id = subcategory )
    serialized = HomeDealSerializer(busines_deal, many=True)
    return Response(
        {
            'status' : 200,
            'error_message' : None,
            'data' : serialized.data
        },
        status=status.HTTP_200_OK
    )


# Deals
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_deal(request):  #done

    store = request.data.get('store', None)
    title = request.data['title'] if 'title' in request.data else None
    condition = request.data['conditions'] if 'conditions' in request.data else None
    location = request.data.get('location', None)
    description = request.data['description'] if 'description' in request.data else None
    
    image = request.data.getlist('image', None) #if 'image' in request.data else None
    video = request.data['video'] if 'video' in request.data else None
    
    #new
    audience = request.data.get('audience', None)
    status_deal = request.data.get('status_deal', None)
    start_date = request.data.get('start_date', None)
    end_date = request.data.get('end_date', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    
    #option
    option_title = request.data.get('option_title', None)
    fees = request.data.get('fees', None)
    no_seats = request.data.get('no_seats', None)
    no_seats_booked = request.data.get('no_seats_booked', None)
    discount = request.data.get('discount', None)
    
    # sub_sub_category = request.data['sub_sub_category']

    #print(store)
    # category = request.data['category']
    # sub_category = request.data['sub_category']
    try:
        request.data._mutable = True
    except Exception as e:
        pass
    #user=request.user.id    
    
    store_ins = BusinessStore.objects.filter(id=store, store_status="Active", user = request.user.id ).first()
    if not store_ins:
        return Response({'success': False, 'message': "Store not found or Inactive"},
                        status=status.HTTP_400_BAD_REQUEST)
    user = request.user
    if user.user_type != "Business" and user.business_status != "Approved":
        return Response({'success': False, 'message': "Something wrong with user, Approved issue"},
                        status=status.HTTP_400_BAD_REQUEST)
    create_deal = BusinessDeal.objects.create(
        create_by = user,
        store = store_ins,
        title = title,
        description =description,
        condition =condition ,
        #price = fees,
        gender =audience,
        start_time = start_time,
        end_time =  end_time,
        start_date = start_date,   
        end_date = end_date,   
        deal_status= status_deal,
        discount_percentage = discount,
    )
    
    if type(location) == str:
        location = json.loads(location)
    
    for loc in location:
        try:
            locat = StoreLocation.objects.get(id  =loc)
            create_deal.location.add(locat)
        except Exception as err:
            print(err)
            
        create_deal.save()
        
    if image is not None:
        for i in image:
            media = DealMedia.objects.create(
                business_deal=create_deal, 
                image=i
                )
    if video:
        media_v = DealMedia.objects.create(
            business_deal=create_deal, 
            video=video
            )
    
    if store_ins.category:
        try:
            cate = Category.objects.get(id = store_ins.category.id)
            create_deal.category = cate
        except Exception as err:
            print(err)
        
    # if store_ins.subcategory:
    #     try:
    #         sub = SubCategory.objects.get(id = store_ins.subcategory.id)
    #         create_deal.sub_category.add(sub)
    #     except Exception as err:
    #         print(err)
    
    create_deal.latitude = store_ins.lat
    create_deal.longitude = store_ins.lon
    create_deal.save()
    
    #     create_deal.sub_category = store_ins.subcategory.id
    
    differentDealData  = DifferentDealData.objects.create(
            deal=create_deal,
            title=option_title,
            description=description,
            discount_percentage=discount, 
            quantity=no_seats, 
            #no_seats_booked=no_seats_booked
        )    
    
    # request.data['status'] = 'True'
    # request.data['deal_status'] = 'Active'
   
    # if store_ins.country:
    #     request.data['country'] = store_ins.country.id
    # if store_ins.city:
    #     request.data['city'] = store_ins.city.id

    # if store_ins.lat and store_ins.lon:
    #     request.data['lat'] = store_ins.lat
    #     request.data['lon'] = store_ins.lon
    # # price = request.data['price']
    # # discount_price = request.data['discount_price']
    # # start_date = request.data['start_date']
    # # end_date = request.data['end_date']
    # image = request.data.getlist('image', None) #if 'image' in request.data else None
    # video = request.data['video'] if 'video' in request.data else None
    # # gender = request.data['gender']
    # # quantity = request.data['quantity']
    # # lat = request.data['lat']
    # # lon = request.data['lon']
    # options = request.data.get('options', None) #if 'options' in request.data else None
    
    
    
    # if type(options) == str:
    #     options = json.loads(options)
        
    # request.data['create_by'] = user.id

    # # if not store or not category or not sub_category \
    # #         or not title or not description or not gender \
    # #         or not price or not start_date or not end_date or not image or not quantity:
    # #     return Response({'success': False, 'response': {'message': 'Invalid Data'}},
    # #                     status=status.HTTP_400_BAD_REQUEST)
    # # if request.user.business_approved = True:
    # serializer = DealSerializer(data=request.data)
    
    # if serializer.is_valid():
    #     business_deal = serializer.save()
    #     if type(location) == str:
    #         location = json.loads(location)

    #     if location:
    #         for i in location:
    #             print(i)
    #             business_deal.location.add(i)
    #     if options is not None:
    #         for option in options:
    #             option = DifferentDealData.objects.create(
    #                 deal=business_deal,
    #                 title=option["name"], 
    #                 description=option["description"],
    #                 price=option["price"], 
    #                 discount_percentage=option["discount"], 
    #                 quantity=option["quantity"]
    #             )
   #GetDealSerializer
    serializer = HomeDealSerializer(create_deal)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_201_CREATED)
    # else:
    #     return Response({'success': False, 'response': serializer.errors},
    #                     status=status.HTTP_400_BAD_REQUEST)
    
# @api_view(['GET'])
# @permission_classes([AllowAny])
# def get_deals(request):
#     store = 
    

@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_deals(request):
    """all deals of a single store"""
    store = request.query_params.get('store', None)
    if not store:
        return Response({'success': False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        # store = BusinessStore.objects.get(id=store, status=True, is_deleted=False)
        store = BusinessStore.objects.get(id=store)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    business_deals = BusinessDeal.objects.filter(store=store, status=True, is_deleted=False)
    serializer = GetDealSerializer(business_deals, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_deal(request):
    """user for delete a singel deal or the singel option of deals"""
    user = request.user
    business_deal = request.data['business_deal'] if 'business_deal' in request.data else None
    deal_option = request.data['deal_option'] if 'deal_option' in request.data else None
    if not business_deal and not deal_option :
        return Response({'success': False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)

    if business_deal:
        try:
            business_deal = BusinessDeal.objects.get(id=business_deal, is_deleted=False)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)
    if deal_option:
        deal_option = DifferentDealData.objects.filter(id=deal_option).first()
        deal_option.is_delete = True
        deal_option.save()
        return Response({'success': True, 'message': 'Option deleted Successfully!'},
                        status=status.HTTP_200_OK)
    if user == business_deal.create_by:
        business_deal.is_deleted = True
        business_deal.save()
        deal_options = DifferentDealData.objects.filter(deal=business_deal, is_delete=False)
        if deal_options:
            for option in deal_options:
                option.is_delete = True
                option.save()

        return Response({'success': True, 'message': 'Deal deleted Successfully!'},
                        status=status.HTTP_200_OK)
    else:
        return Response({'success': False, 'message': 'Ops, You have no permission to delete this deal!'},
                        status=status.HTTP_400_BAD_REQUEST)
# business_store.user

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_deal(request):
    
    business_deal = request.data['business_deal'] if 'business_deal' in request.data else None  #id
    # category = request.data['category'] if 'category' in request.data else None
    # sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
    # sub_sub_category = request.data['sub_sub_category'] if 'sub_sub_category' in request.data else None
    title = request.data['title'] if 'title' in request.data else None
    description = request.data['description'] if 'description' in request.data else None
    condition = request.data['conditions'] if 'conditions' in request.data else None
    # price = request.data['price'] if 'price' in request.data else None
    start_date = request.data['date'] if 'date' in request.data else None
    end_date = request.data['end_date'] if 'end_date' in request.data else None
    status = request.data['status'] if 'status' in request.data else None
    image = request.data.getlist('image') if 'image' in request.data else None
    video = request.data['video'] if 'video' in request.data else None
    # gender = request.data['gender'] if 'gender' in request.data else None
    # quantity = request.data['quantity'] if 'quantity' in request.data else None
    location = request.data.get('location', None)
    
    #
    end_date = request.data.get('end_date', None)
    start_time = request.data.get('start_time', None)
    end_time = request.data.get('end_time', None)
    option_title = request.data.get('option_title', None)
    fees = request.data.get('fees', None)
    no_seats = request.data.get('no_seats', None)
    no_seats_booked = request.data.get('no_seats_booked', None)
    discount = request.data.get('discount', None)
    
    print(business_deal)
    user = request.user
    
    if not business_deal:
        return Response({'success': False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        business_deal = BusinessDeal.objects.get(id=business_deal, is_deleted=False,)# create_by=user.id)
    except Exception as e:
        return Response({'success': False, 'message': 'business_deal not found', 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    # if user != str(business_deal.create_by) and user.user_type=='Business':
    #     return Response({'success': False, 'message': 'Ops, You have no permission to Update this deal!'},
    #                     status=status.HTTP_400_BAD_REQUEST)
    try:
        differentdeal =  DifferentDealData.objects.get(deal = business_deal )
    except Exception as err:
        return Response({'success': False, 'message': 'DifferentDealData not found', 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        
    if option_title:
        differentdeal.title = option_title
    # if fees:
    #     differentdeal.price = fees
    if no_seats:
        differentdeal.quantity = no_seats
    if no_seats_booked:
        differentdeal.no_seats_booked = no_seats_booked
    if discount:
        differentdeal.discount_percentage = discount
        
    
    # if category:
    #     try:
    #         category = Category.objects.get(id=category)
    #     except Exception as e:
    #         return Response({'success': False, 'response': str(e)},
    #                         status=status.HTTP_404_NOT_FOUND)
    #     business_deal.category = category

    # if sub_category:
    #     try:
    #         sub_category = SubCategory.objects.get(id=sub_category)
    #     except Exception as e:
    #         return Response({'success': False, 'response': str(e)},
    #                         status=status.HTTP_404_NOT_FOUND)
    #     business_deal.sub_category = sub_category

    # if sub_sub_category:
    #     try:
    #         sub_sub_category = SubSubCategory.objects.get(id=sub_sub_category)
    #     except Exception as e:
    #         return Response({'success': False, 'response': str(e)},
    #                         status=status.HTTP_404_NOT_FOUND)
    #     business_deal.sub_sub_category = sub_sub_category
    if type(location) == str:
        location = json.loads(location)
        
    business_deal.location.clear()
    for loc in location:
        try:
            locat = StoreLocation.objects.get(id  =loc)
            print(locat)
            business_deal.location.add(locat)
        except Exception as err:
            print(err)
            
        business_deal.save()
    
    if title:
        business_deal.title = title
    if description:
        business_deal.description = description
    if status:
        business_deal.deal_status = status
    # if price:
    #     business_deal.price = price
    if start_date:
        business_deal.start_date = start_date
        
    if start_time:
        business_deal.start_time = start_time
    if end_time:
        business_deal.end_time = end_time
        
    if condition:
        business_deal.condition = condition
    if end_date:
        business_deal.end_date = end_date
    if start_date:
        business_deal.start_date = start_date
        
    if end_date:
        business_deal.end_date = end_date
    business_deal.save()
    #business_deal = BusinessDeal.objects.get(id=business_deal.id, create_by=user.id, is_deleted=False)
    if video:
        vid = DealMedia.objects.filter(business_deal=business_deal)
        if vid:
            for i in vid:
                if i.video:
                    i.delete()
        video_v = DealMedia.objects.create(business_deal=business_deal, video=video)
    if image:
        img = DealMedia.objects.filter(business_deal=business_deal)
        if img:
            for i in img:
                if i.image:
                    i.delete()
        for i in image:
            media = DealMedia.objects.create(business_deal=business_deal, image=i)
        serializer = GetDealSerializer(business_deal)
        return Response({'success': True, 'message': serializer.data})

    # if gender:
    #     business_deal.gender = gender
    # if quantity:
    #     business_deal.quantity = quantity

    serializer = GetDealSerializer(business_deal)
    return Response({'success': True, 'message': serializer.data})
    # return Response({'success': True, 'message': serializer.data},
    #                 status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_single_deal(request):
    single_deal = request.query_params.get('single_deal', None)
    if not single_deal:
        return Response({'success': False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        business_deal = BusinessDeal.objects.get(id=single_deal, is_deleted=False)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    # serializer = GetDealSerializer(business_deal)
    serializer = SingleDealSerializer(business_deal, many=False)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_store_rating(request):
    business_store = request.data['business_store'] if 'business_store' in request.data else None
    review = request.data['review'] if 'review' in request.data else None
    rate = request.data['rate'] if 'rate' in request.data else None
    user = request.user

    if not business_store or not review or not rate:
        return Response({"success": False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        business_store = BusinessStore.objects.get(is_deleted=False, status=True)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    rating = StoreRating.objects.create(business_store=business_store, review=review, rate=rate, user=user)
    serializer = StoreRatingSerializer(rating)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_rating(request):
    business_store = request.query_params.get('business_store', None)
    if not business_store:
        return Response({"success": False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        business_store = BusinessStore.objects.get(id=business_store, is_deleted=False, status=True)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    rating = StoreRating.objects.filter(business_store=business_store)

    serializer = StoreRatingSerializer(rating, many=True)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_store_rating(request):
    store_rating = request.data['store_rating'] if 'store_rating' in request.data else None

    if not store_rating:
        return Response({"success": False, 'response': 'Invalid Data!'},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        store_rating = StoreRating.objects.get(id=store_rating)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)

    store_rating.delete()
    return Response({'success': True, 'message': 'Deleted Successfully!'},
                    status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_store_rating(request):
    store_rating = request.data['store_rating'] if 'store_rating' in request.data else None
    review = request.data['review'] if 'review' in request.data else None
    rate = request.data['rate'] if 'rate' in request.data else None
    user = request.user

    try:
        store_rating = StoreRating.objects.get(id=store_rating)
    except Exception as e:
        return Response({'success': False, 'response': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
    if review:
        store_rating.review = review
    if rate:
        store_rating.rate = rate
    store_rating.save()

    serializer = StoreRatingSerializer(store_rating)
    return Response({'success': True, 'message': serializer.data},
                    status=status.HTTP_200_OK)


class BannerView(viewsets.ViewSet):
    """
    any user can see(list) collection, and retrieve
    """
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            list_banners = Banner.objects.filter(status='True').all()
            serializer = BannerViewSerializer(list_banners, many=True)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class CategoryView(viewsets.ViewSet):
    """
    any user can see(list) collection, and retrieve
    """
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            category = Category.objects.filter(is_deleted=False, status='Active').all()
            serializer = CategoryViewSerializer(category, many=True)

            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class SubCategoryView(viewsets.ViewSet):
    """
    any user can see(list) collection, and retrieve
    """
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        global list_sub_banners
        try:
            category_id = self.request.query_params.get('category_id')
            # category_id = request.data['category_id']
            if category_id != 'all':
                list_sub_banners = SubCategory.objects.filter(
                    category__slug=category_id, status="Active", is_deleted=False
                    # Q(category__id=category_id, status="Active", is_deleted=False)
                )
            if category_id == 'all':
                list_sub_banners = SubCategory.objects.filter(status="Active", is_deleted=False)
            serializer = SubCategoryViewSerializer(list_sub_banners, many=True)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)
            
class SubCategoryViewBusiness(viewsets.ViewSet):
    """
    any user can see(list) collection, and retrieve
    """
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        global list_sub_banners
        try:
            category_id = self.request.query_params.get('category_id')
            # category_id = request.data['category_id']
            if category_id != 'all':
                list_sub_banners = SubCategory.objects.filter(
                    category__id=category_id, status="Active", is_deleted=False
                    # Q(category__id=category_id, status="Active", is_deleted=False)
                )
            if category_id == 'all':
                list_sub_banners = SubCategory.objects.filter(status="Active", is_deleted=False)
            serializer = SubCategoryViewSerializer(list_sub_banners, many=True)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class UserProfile(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def retrievee(self, request, *args, **kwargs):  # alternate of retrive
        try:
            user = request.user
            # user = self.kwargs.get('id')
            # user = self.request.query_params.get('id')
            user_profile = User.objects.filter(id=user.id).first()
            serializer = UserProfileViewSerializer(user_profile)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def partial_updatee(self, request, *args, **kwargs):
        try:
            # user_id = self.kwargs.get('id')
            user = request.user
            # request.data._mutable = True
            # request.data['country'] = Country.objects.filter(id=request.data['country']).first()
            # request.data['city'] = City.objects.filter(id=request.data['city']).first()
            # if user.id == user_id:
            user_profile = User.objects.filter(id=user.id).first()
            serializer = UserProfileViewSerializer(user_profile, data=request.data, partial=True,
                                                   context={'user': user_profile})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class UserChangePasswrodView(viewsets.ViewSet):
    """
    only for Authenticated user can change his/her login password by login
    """
    permission_classes = [IsAuthenticated]

    def updatee(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.is_active:
                password = request.data.get('new_password')
                if len(password) < 8:
                    return Response({
                        "status": False, "status_code": 400, "msg": "Password must be at least 8 characters.",
                        "data": []}, status=status.HTTP_400_BAD_REQUEST)
                serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
                serializer.is_valid(raise_exception=True)
                return Response({
                    "status": True, "status_code": 200, "msg": "Password Reset Successfully",
                    "data": []}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": False, "status_code": 400, "msg": "User is not active user.",
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,
                "msg": [e.args[0]['non_field_errors'][0] if 'non_field_errors' in e.args[0] else e.args[0]][0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class BusinessDealView(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data['create_by'] = request.user.id
            serializer = BusinessDealViewSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": True, "status_code": 200, 'msg': 'User Collection Created Successfully',
                "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400, 'msg': e.args[0],
                "data": []}, status=status.HTTP_400_BAD_REQUEST)


    # def partial_update(self, request, *args, **kwargs):
    #     try:
    #         id = self.kwargs.get('pk')
    #         collection_id = Collection.objects.get(id=id)
    #         if request.user.id == collection_id.create_by.id:
    #             # collection = Collection.objects.get(id=pk)
    #             serializer = UserCollectionSerializer(collection_id, data=request.data, partial=True)
    #             serializer.is_valid(raise_exception=True)
    #             serializer.save()
    #             return Response({
    #                 "status": True, "status_code": 200, 'msg': 'User Collection Update Successfully',
    #                 "data": serializer.data}, status=status.HTTP_200_OK)
    #         else:
    #             return Response({
    #                 "status": False, "status_code": 400, 'msg': 'User not creator of this Collection',
    #                 "data": []}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({
    #             "status": False, "status_code": 400, 'msg': e.args[0],
    #             "data": []}, status=status.HTTP_400_BAD_REQUEST)


class BusinessUserProfile(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrievee(self, request, *args, **kwargs):  # alternate of retrive
        try:
            user = request.user
            # user = self.kwargs.get('id')
            # user = self.request.query_params.get('id')
            user_profile = User.objects.filter(id=user.id).first()
            serializer = BusinessUserProfileViewSerializer(user_profile)
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def partial_updatee(self, request, *args, **kwargs):
        try:
            logo = request.data.get('logo')

            # user_id = self.kwargs.get('id')
            user = request.user
            # request.data._mutable = True
            # request.data['country'] = Country.objects.filter(id=request.data['country']).first()
            # request.data['city'] = City.objects.filter(id=request.data['city']).first()

            user_profile = User.objects.filter(id=user.id).first()
            if logo is not None:
                user_profile.logo = logo
                user_profile.save()
            serializer = BusinessUserProfileViewSerializer(user_profile, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success': True, 'message': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class BusinessUserChangePasswrodView(viewsets.ViewSet):
    """
    only for Authenticated user can change his/her login password by login
    """
    permission_classes = [IsAuthenticated]

    def updatee(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.is_active:
                password = request.data.get('new_password')
                if len(password) < 8:
                    return Response({
                        "status": False, "status_code": 400, "msg": "Password must be at least 8 characters.",
                        "data": []}, status=status.HTTP_400_BAD_REQUEST)
                serializer = UserChangePasswordSerializer(data=request.data, context={'user': request.user})
                serializer.is_valid(raise_exception=True)
                return Response({
                    "status": True, "status_code": 200, "msg": "Password Reset Successfully",
                    "data": []}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": False, "status_code": 400, "msg": "User is not active user.",
                    "data": []}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": False, "status_code": 400,
                "msg": [e.args[0]['non_field_errors'][0] if 'non_field_errors' in e.args[0] else e.args[0]][0], "data": []}, status=status.HTTP_400_BAD_REQUEST)


class SearchAPIView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def search_function(self, request, *args, **kwargs):
        try:
            item = self.request.query_params.get('item')
            # date = datetime.datetime.utcnow()
            # utc_time = calendar.timegm(date.utctimetuple())
            if item:
                queryset = BusinessDeal.objects.filter(title__icontains=item, is_expired=False,
                                        store__store_status='Active', is_deleted=False).order_by('-updated_at')
            else:
                return Response({'success': True, 'message': 'Enter valid data'},
                                status=status.HTTP_404_NOT_FOUND)
            # paginator = CustomPageNumberPagination()
            # result = paginator.paginate_queryset(queryset, request)
            serializer = HomeDealSerializer(queryset, many=True)
            return Response({'success': True, 'message': 'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Top_Offers(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list_top_offers(self, request, *args, **kwargs):
        try:
            user = request.user
            if user.is_authenticated and user.user_type == 'Business':
                top_offers = BusinessDeal.objects.filter(create_by=user.id, is_deleted=False, is_expired=False,
                                            status=True).order_by('-updated_at')
            else:
                top_offers = BusinessDeal.objects.filter(is_deleted=False, is_expired=False,
                                            status=True, store__store_status='Active').order_by('-updated_at')
            #serializer = GetDealSerializer(top_offers, many=True)
            serializer = HomeDealSerializer(top_offers, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Nearby_Deals(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list_nearby_deals(self, request, *args, **kwargs):
        try:
            top_offers = BusinessDeal.objects.filter(is_deleted=False, is_expired=False,
                                                     store__store_status='Active')#.filter(~Q(lat=None, lon=None))

            #serializer = HomeDealSerializer(top_offers, many=True)
            serializer = NearByDealSerializer(top_offers, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Best_Seller(viewsets.ViewSet): # top selles deals
    permission_classes = [AllowAny]
    def list_best_seller(self, request, *args, **kwargs):
        try:
            store_id = self.request.query_params.get('store_id')
            user = request.user
            if store_id and user:
                top_offers = BusinessDeal.objects.filter(store=store_id, user=user.id, is_deleted=False)
            else:
                top_offers = BusinessDeal.objects.filter(is_deleted=False, is_expired=False, store__store_status='Active')
            serializer = HomeDealSerializer(top_offers, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Deals_Of_The_Day(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list_deals_of_the_day(self, request, *args, **kwargs):
        try:
            top_offers = BusinessDeal.objects.filter(is_deleted=False, is_expired=False, store__store_status='Active')
            serializer = HomeDealSerializer(top_offers, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)



class FilterView(viewsets.ModelViewSet):
    queryset = BusinessDeal.objects.all()
    serializer_class = HomeDealSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        global queryset
        try:
            category = request.data['category'] if 'category' in request.data else None
            sub_category = request.data['sub_category'] if 'sub_category' in request.data else None
            min_price = request.data['min_price'] if 'min_price' in request.data else None
            max_price = request.data['max_price'] if 'max_price' in request.data else None
            country = request.data['country'] if 'country' in request.data else None
            city = request.data['city'] if 'city' in request.data else None
            # collection_id = self.request.query_params.get('collection')
            # search = self.request.query_params.get('search')
            # filter_by = self.request.query_params.get('filter_by')
            # listingtime = self.request.query_params.get('listingtime')
            # if nft_tags:
            #     nft_tags_list = nft_tags.split(',')
            #     nft_tags_set = set(list(map(int, nft_tags_list)))
            # nft_tags_set = set(nft_tags_list)
            # check = all(item in List1 for item in List2)
            # a =  NFT.objects.exclude(updated_at=)
            # user = request.user.id
            # collection = Collection.objects.filter(id=collection_id).first()

            # if not nft_sort_by:
            #     if collection and user==collection.create_by.id:
            #         queryset = self.queryset.filter(nft_collection__id=collection_id)
            #     else:
            #         queryset = self.queryset.filter(nft_collection__id=collection_id, is_listed=True, is_minted=True)

            queryset = self.queryset.filter(is_deleted=False, is_expired=False, store__store_status='Active')
            if category != '' and category is not None:
                queryset = queryset.filter(category = category)

            if sub_category != '' and sub_category is not None:
                queryset = queryset.filter(sub_category=sub_category)


            if country != '' and country is not None:
                queryset = queryset.filter(country=country)

            if city != '' and city is not None:
                queryset = queryset.filter(city=city)

            if min_price != '' and min_price is not None and max_price != '' and max_price is not None:
                queryset = queryset.filter(discount_price__gte=min_price, discount_price__lte=max_price)

            serializer = HomeDealSerializer(queryset, many=True)
            return Response({'success': True, 'message':'Filter Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)

            # if min_price:
            #     queryset = queryset.filter(Q(fix_price__gte=min_price) | Q(starting_price__gte=min_price))
            #
            # if max_price:
            #     queryset = queryset.filter(Q(fix_price__lte=max_price) | Q(starting_price__lte=max_price))

        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Single_Store_All_Deals(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def list_deals(self, request, *args, **kwargs):
        try:
            store_id = self.request.query_params.get('store_id')
            user = request.user
            if not store_id and user.is_authenticated:
                # user = request.user  , store__store_status='Active'
                top_offers1 = BusinessDeal.objects.filter(create_by=user.id, deal_status='Active', is_deleted=False)
                serializer1 = HomeDealSerializer(top_offers1, many=True)
                top_offers2 = BusinessDeal.objects.filter(create_by=user.id, deal_status='Inactive', is_deleted=False)
                serializer2 = HomeDealSerializer(top_offers2, many=True)
                top_offers3 = BusinessDeal.objects.filter(create_by=user.id, is_expired=True, is_deleted=False)
                serializer3 = HomeDealSerializer(top_offers3, many=True)
                top_offers4 = BusinessDeal.objects.filter(create_by=user.id, is_featured=True, is_deleted=False)
                serializer4 = HomeDealSerializer(top_offers4, many=True)
                #serializer4 = TestDealSerializer(top_offers4, many=True)
            else:
                top_offers1 = BusinessDeal.objects.filter(store=store_id, create_by=user.id, deal_status='Active', is_deleted=False)
                serializer1 = HomeDealSerializer(top_offers1, many=True)
                top_offers2 = BusinessDeal.objects.filter(store=store_id, create_by=user.id, deal_status='Inactive', is_deleted=False)
                serializer2 = HomeDealSerializer(top_offers2, many=True)
                top_offers3 = BusinessDeal.objects.filter(store=store_id, create_by=user.id, is_expired=True, is_deleted=False)
                serializer3 = HomeDealSerializer(top_offers3, many=True)
                top_offers4 = BusinessDeal.objects.filter(store=store_id, create_by=user.id, is_featured=True, is_deleted=False)
                serializer4 = HomeDealSerializer(top_offers4, many=True)
            return Response({'success': True, 'message':'Deals Listed', 'Active': serializer1.data,
                             'Inactive':serializer2.data, 'Expired':serializer3.data, 'Featured':serializer4.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class AddToCartView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        """create cart fucntion"""
        try:
            # request.data['user'] = user.id
            deal = BusinessDeal.objects.filter(id=request.data['deal_id'], status=True, is_expired=False, is_deleted=False).first()
            options = request.data.get('options') if 'options' in request.data else None

            if options:
                if type(options) == str:
                    options = json.loads(options)

                for option in options:
                    try:
                        deal_option = DifferentDealData.objects.get(id=option['id'])
                    except:
                        pass
                    else:
                        user_cart_item, created = CartItem.objects.get_or_create(
                            user=request.user,
                            deal = deal,
                            store = deal.store,
                            option_id = deal_option,
                        )
                        user_cart_item.discount_price = deal_option.discount_percentage
                        user_cart_item.orignal_price = deal_option.price
                        # user_cart_item.delivery_charges = delivery_charges
                        user_cart_item.quantity = option['quantity']
                        user_cart_item.save()
                return Response({'success': True, 'message':'Add to cart successfully', 'created' : created},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'response': "Deal is not found or not active"},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


    def partial_update(self, request, *args, **kwargs):
        """partial update cart fucntion"""
        try:
            user = request.user
            cart_id = self.kwargs.get('pk')
            cart_instance = CartItem.objects.filter(id=cart_id, user=user.id).first()
            if cart_instance:
                serializer = AddToCartSerializer(cart_instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success': True, 'message': 'Update cart successfully', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'response': "cart not found"},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """list all cart of a single user fucntion"""
        try:
            user = request.user
            cart_instance = CartItem.objects.filter(user=user.id).order_by('-id')
            if cart_instance:
                serializer = AddToCartSerializer(cart_instance, many=True)
                return Response({'success': True, 'message': 'List all cart successfully', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'message': 'Cart is empty'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        """update cart fucntion"""
        try:
            user = request.user
            cart_id = self.kwargs.get('pk')
            cart_instance = CartItem.objects.filter(user=user.id, id=cart_id).first()
            if cart_instance:
                serializer = AddToCartSerializer(cart_instance, many=False)
                return Response({'success': True, 'message': 'List all cart successfully', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'message': 'Cart is empty'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        """update cart"""
        try:
            user = request.user
            cart_id = self.kwargs.get('id', None)
            if cart_id is not None:
                try:
                    cart_instance = CartItem.objects.get(user=user, id=int(cart_id))
                except Exception as err:
                    return Response({'success': False, 'message': 'Cart not found' , 'error_message' : str(err)},
                                    status=status.HTTP_404_NOT_FOUND)
                else:
                    cart_instance.delete()
                    return Response({'success': True, 'message': 'Cart delete successfully'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Please provide ID'},
                                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class OrderPlacedView(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        """create order"""
        try:
            user = request.user
            request.data['user'] = user.id
            cartitem_id = request.data['cartitem_id']
            if cartitem_id:
                cart_item = CartItem.objects.filter(id=cartitem_id, user=user.id).first()
            else:
                return Response({'success': False, 'response': "Cart id not found"},
                                status=status.HTTP_404_NOT_FOUND)
            if cart_item:
                deal = BusinessDeal.objects.filter(id=request.data['deal_id'], status=True, is_expired=False, is_deleted=False).first()
                if deal:
                    request.data['deal'] = deal.id
                    request.data['store'] = deal.store.id
                    serializer = OrderPlacedViewSerializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    # Cart(user=user, product=product).save()
                    cart_item.delete()
                    return Response({'success': True, 'message':'Add to cart successfully', 'data': serializer.data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'response': "Deal is not found or not active"},
                                    status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'success': False, 'response': "Cart item not found"},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """list all orders of a single user"""
        try:
            user = request.user
            orders = OrderPlaced.objects.filter(user=user.id).order_by('-id')
            if orders:
                serializer = OrderPlacedViewSerializer(orders, many=True)
                return Response({'success': True, 'message': 'List all cart successfully', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'message': 'Orders list is empty'},
                                status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


# class BusinessDetailsView(viewsets.ViewSet): #show statacitics of chart of Business
#     """for business user, user can see its bussness detal finatial of one or all bussiness"""
#
#     def list(self, request, *args, **kwargs):
#         """list all buss of a single user fucntion"""
#         try:
#             user = request.user
#             cart_instance = CartItem.objects.filter(user=user.id).order_by('-id')
#             if cart_instance:
#                 serializer = AddToCartSerializer(cart_instance, many=True)
#                 return Response({'success': True, 'message': 'List all cart successfully', 'data': serializer.data},
#                                 status=status.HTTP_200_OK)
#             else:
#                 return Response({'success': True, 'message': 'Cart is empty'},
#                                 status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'success': False, 'response': str(e)},
#                             status=status.HTTP_404_NOT_FOUND)
#
#     def retrieve(self, request, *args, **kwargs):
#         """update cart fucntion"""
#         try:
#             user = request.user
#             cart_id = self.kwargs.get('pk')
#             cart_instance = CartItem.objects.filter(user=user.id, id=cart_id).first()
#             if cart_instance:
#                 serializer = AddToCartSerializer(cart_instance, many=False)
#                 return Response({'success': True, 'message': 'List all cart successfully', 'data': serializer.data},
#                                 status=status.HTTP_200_OK)s
#             else:
#                 return Response({'success': True, 'message': 'Cart is empty'},
#                                 status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'success': False, 'response': str(e)},
#                             status=status.HTTP_404_NOT_FOUND)


class All_Store_Active_Inactive(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def list_stores(self, request, *args, **kwargs):
        try:
            # store_id = self.request.query_params.get('store_id')
            serializer4 = None
            user = request.user
            if user.is_authenticated:
                all_stores = BusinessStore.objects.filter(user=user.id, is_deleted=False)
                serializer1 = StoreGetSerializer(all_stores, many=True)
                active_stores = BusinessStore.objects.filter(user=user.id, store_status='Active', is_deleted=False)#verification_status='Verified')
                serializer2 = StoreGetSerializer(active_stores, many=True)
                inactive_stores = BusinessStore.objects.filter(user=user.id, store_status='Inactive', is_deleted=False)
                serializer3 = StoreGetSerializer(inactive_stores, many=True)
                try:
                    pending_stores = BusinessStore.objects.get(user=user.id, is_deleted=False)#, verification_status='Pending'
                    serializer4 = StoreGetSerializer(pending_stores).data
                except Exception as e:
                    print('*******', e)
                    pass

                return Response({'success': True, 'message': 'Stores Listed', 'All': serializer1.data,
                                 'Active': serializer2.data, 'Inactive': serializer3.data, 'Pending':serializer4}, status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Recent_Orders(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def recent_orders(self, request, *args, **kwargs):
        try:
            orders = []
            user = request.user
            store_id = self.request.query_params.get('store_id')
            if store_id and user:
                orders = OrderPlaced.objects.filter(store=store_id)
            if user and not store_id:
                deals = BusinessDeal.objects.filter(create_by=user.id, status=True, is_deleted=False)
                if deals:
                    for deal in deals:
                        order = OrderPlaced.objects.filter(deal=deal.id)
                        for o in order:
                            orders.append(o)
                else:
                    return Response({'success': False, 'message':'Deals and Reviews not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            serializer = OrderPlacedViewSerializer(orders, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class Recent_Reviews(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def recent_reviews(self, request, *args, **kwargs):
        try:
            reviews = []
            user = request.user
            store_id = self.request.query_params.get('store_id')
            if store_id and user:
                deals = BusinessDeal.objects.filter(store=store_id, create_by=user.id, status=True, is_deleted=False)
                if deals:
                    for deal in deals:
                        review = DealRating.objects.filter(business_deal=deal.id)
                        for r in review:
                            reviews.append(r)
                else:
                    return Response({'success': False, 'message':'Deals and Reviews not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            if user and not store_id:
                deals = BusinessDeal.objects.filter(create_by=user.id, status=True, is_deleted=False)
                if deals:
                    for deal in deals:
                        review = DealRating.objects.filter(business_deal=deal.id)
                        for r in review:
                            reviews.append(r)
                else:
                    return Response({'success': False, 'message':'Deals and Reviews not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            serializer = Recent_Reviews_Serializer(reviews, many=True)
            return Response({'success': True, 'message':'Top Offers Listed', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class UserOrdersListView(viewsets.ViewSet):
    """will show all orders plassed of a single user by authentication token"""
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def user_placed_orders(self, request, *args, **kwargs):
        try:
            user_orders = OrderPlaced.objects.all()
            # user_orders = OrderPlaced.objects.filter(user=request.user.id)
            serializer = UserOrdersListSerializer(user_orders, many=True)
            return Response({'success': True, 'message':'Single user all orders', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

class UpdateOptionView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def update_option(self, request, *args, **kwargs):
        try:
            user = request.user
            # option_id = self.request.query_params.get('option_id')
            option_id = request.data['option_id']
            option = DifferentDealData.objects.filter(id=option_id, is_delete=False, deal__create_by=user.id).first()
            try:
                request.data._mutable = True
            except Exception as e:
                pass
            if option:
                request.data['deal'] = option.deal.id   # to confirm the deal is same
            else:
                return Response({'success': True, 'message': 'Provide the option id'})
            # user_orders = OrderPlaced.objects.filter(user=request.user.id)
            # serializer = UserProfileSerializer(user_id, data=context, partial=True)

            serializer = UpdateOptionViewSerializer(option, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success': True, 'message':'Single user all orders', 'data': serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)


class EmailValidateView(viewsets.ViewSet):
    permission_classes = [AllowAny] # this will is_authentiate
    def email_validate(self, request, *args, **kwargs):
        try:
            email = request.data['email'] if 'email' in request.data else None
            phone = request.data['phone'] if 'phone' in request.data else None

            if email or phone:
                try:
                    validate_email(email)
                except ValidationError as e:
                    return Response({'success': False, 'message': str(e.messages[0])},
                                    status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.filter(Q(email=email) | Q(phone=phone)).first()
                if user:
                    return Response({'success': False, 'message': 'User already exist with this email or phone no.'},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'success': True, 'message': 'User not exist with this email.'},
                                    status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'message': 'Please enter email.'},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

class Category_Deals(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def category_deals(self, request, *args, **kwargs):
        try:
            category_id = self.request.query_params.get('category_id')
            if category_id:
                # user = request.user
                subcategory = SubCategory.objects.filter(category=category_id, status="Active", is_deleted=False)
                serializer1 = SubCategoryViewSerializer(subcategory, many=True)
                deals = BusinessDeal.objects.filter(category=category_id, status=True, is_deleted=False)
                serializer2 = HomeDealSerializer(deals, many=True)

            else:
                return Response(
                    {'success': True, 'message': 'Enter Category id.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'message':'SubCategory and Deals Listed', 'subcategory': serializer1.data, 'deals':serializer2.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)



class SubCategory_Deals(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def subcategory_deals(self, request, *args, **kwargs):
        """by getting sub category id this will show all deals related to given data(id)"""
        try:
            subcategory_id = self.request.query_params.get('subcategory_id')
            if subcategory_id:
                deals = BusinessDeal.objects.filter(sub_category=subcategory_id, status=True, is_deleted=False)
                serializer = HomeDealSerializer(deals, many=True)

            else:
                return Response(
                    {'success': True, 'message': 'Enter SubCategory id.'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'success': True, 'message':'SubCategory and Deals Listed', 'data':serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)



class CurrencyView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def currency_list(self, request, *args, **kwargs):
        try:
            currency = Currency.objects.all()
            serializer =CurrencySerializer(currency, many=True)
            return Response({'success': True, 'message':'Currency Listed', 'data':serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'response': str(e)},
                            status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_user(request):
    email = request.data['email'] if 'email' in request.data else None
    phone = request.data['phone'] if 'phone' in request.data else None

    if email:

    #     user = User.objects.get(email=email)
    #     return Response({'success': False, 'message': 'User already exist with this email.'},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # elif phone:
    #     user = User.objects.get(phone=phone)
    #     return Response({'success': False, 'message': 'User already exist with this mobile number.'},
    #                     status=status.HTTP_400_BAD_REQUEST)
    # else:
    #     return Response({'success': True, 'response': 'User Not exist!'},
    #                     status=status.HTTP_200_OK)


        try:
            user = User.objects.get(email=email)
            return Response({'success': False, 'message': 'User already exist with this email.'},
                            status=status.HTTP_200_OK)
        except:
            pass
    elif phone:
        try:
            user = User.objects.get(phone=phone)
            return Response({'success': False, 'message': 'User already exist with this mobile number.'},
                        status=status.HTTP_200_OK)
        except:
            pass

    return Response({'success': True, 'response': 'User Not exist!'},
                    status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def near_deals(request):
    my_lat = request.query_params.get('lat')
    my_long = request.query_params.get('long')
    my_radius = request.query_params.get('radius')
    if my_lat or my_long:
        my_deals = BusinessDeal.objects.raw(f'SELECT *, "( 6373 * acos( cos( radians({my_lat}) ) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians({my_long}) ) + sin( radians({my_lat}) ) * sin( radians( latitude ) ) ) )" FROM BusinessDeal WHERE "( 6373 * acos( cos( radians({my_lat}) ) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians({my_long}) ) + sin( radians({my_lat}) ) * sin( radians( latitude ) ) ) )" <= 100')

    else:
        my_deals = BusinessDeal.objects.filter(is_deleted=False).order_by('-created_at')
    serializer = HomeDealSerializer(my_deals, many=True)

    return Response({"success": True, 'data': serializer.data,
                                        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def cart_order_checkout(request):
    name = request.data.get('name', None)
    email = request.data.get('email', None)
    phone = request.data.get('phone', None)
    address = request.data.get('address', None)

    card_number = request.data.get('card_number', None)
    card_name = request.data.get('card_name', None)
    exp = request.data.get('exp', None)
    cvv = request.data.get('cvv', None)

    total = request.data.get('total', None)
    reservation_fee = request.data.get('reservation_fee', None)
    discount = request.data.get('discount', None)
    gst = request.data.get('gst', None)
    gross_total = request.data.get('gross_total', None)

    # store_id = item['store']
    # store = BusinessStore.objects.filter(id=store_id, is_deleted=False).first()
    # if store.total_order is None:
    #     store.total_order=0

    # store.total_order += 1
    # store.save()

    cart_details = []
    if request.user.is_authenticated:
        cart_details = CartItem.objects.filter(user=request.user)
        cart_details = [{'id' : itm.option_id.id , 'quantity' : itm.quantity } for itm in cart_details]

        print('authenticated')
    else:
        cookies_cart = request.COOKIES.get('cart_items', None)
        if cookies_cart is not None:
            if type(cookies_cart) == str:
                cookies_cart = json.loads(cookies_cart)
            
            for ky in cookies_cart:
                cart_details.append({'id' : ky , 'quantity' : cookies_cart[ky]['quantity'] })
    
    if len(cart_details) == 0 :
        return Response({'success': False, 'response': 'No Item in the cart'},
                    status=status.HTTP_404_NOT_FOUND)

    order = OrderPlaced(
        # deal = deal,
        # store = store,
        # currency = currency,
        # country = country,
        # city = city,
        # discount_price = discount_price,
        # delivery_charges = delivery_charges,
        # quantity = quantity,
        # status = status,
        name = name,
        email = email,
        phone = phone,
        address = address,
        # payment_method = payment_method,
        reservation_fee = reservation_fee,
    )
    if request.user.is_authenticated:
        order.user = request.user
    order.save()
    for item in cart_details:
        try:
            deal_opt = DifferentDealData.objects.get(id=item['id'])
        except:
            print('item is not in the cart')
            pass
        else:
            order_item = OrderItem(
                order = order,
                deal_option = deal_opt,
                quantity = item['quantity'],
                discount = deal_opt.discount_percentage
            )
            order_item.save()
            deal_opt.quantity -= item['quantity']
            deal_opt.save()
    
    card_details = OrderCardCheckout(
        order = order,
        card_number = 'card_number',
        card_holder = 'card_name',
        # expire_at = f'{exp}-01',
        cvv = 'cvv',
    )
    card_details.save()

    # OrderCardCheckout
    # OrderItem
    try:
        send_mail_thread = Thread(
            target=send_order_email_to_customer, 
            kwargs={
                'data' : {
                    'email' : email, 
                    'order' : order
                }
            }
        )
        send_mail_thread.start()
    except Exception as err:
        ExceptionRecord.objects.create(text=str(err))

        return Response({'success': False, 'response': str(err)},
                    status=status.HTTP_400_BAD_REQUEST)
   
    response = Response({'success': True, 'response': 'Order Placed'},
                    status=status.HTTP_200_OK)

    if request.user.is_authenticated:
        user_cart = CartItem.objects.filter(user=request.user)
        for itm in user_cart:
            itm.delete()
    else:
        response.delete_cookie('cart_items')

    return response

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_login_user(request):
    data = request.data
    email = request.data.get('email').lower().strip() if 'email' in data else None
    password = data['password'] if 'password' in data else None
    if not email or not password:
        return Response({"success": False, 'response': {'message': 'Provide credentials'}},
			        status=status.HTTP_200_OK)
    if email:
        try:
            profile = User.objects.get(email=email)
        except:
            return Response({"success": False, 'response': {'message': 'Sorry! This account does not exist!'}},
                            status=status.HTTP_200_OK)

    if email is not None:
        try:
            profile = User.objects.get(email=email, is_active=True)
            parent_username = profile.username
        except ObjectDoesNotExist:
            return Response({"success": False, 'response': {'message': 'Sorry! Your Profile is not Active'}},
                            status=status.HTTP_200_OK)
                            
        user = authenticate(username=parent_username, password=password)
        if not user:
            return Response({"success": False, 'response': {'message': 'Incorrect User Credentials!'}},
                            status=status.HTTP_200_OK)
    return Response({'success': True, 'response': {'message': 'Login Successfully!'}},
                status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_store_location(request):
    business_store = request.data['business_store'] if 'business_store' in request.data else None
    data = request.data.get('address', None)
    lat = request.data.get('lat', None)
    lng = request.data.get('lng', None)

    if not business_store or not data :
        return Response({"success": False, 'response': {'message': 'Invalid data!'}},
			        status=status.HTTP_200_OK)

    location_list = []
    data = json.loads(data)
    for i in data:
        location = StoreLocation.objects.create(
            business_store_id=business_store, 
            adress=i['address'], 
            status=True,
            city_id=i['city'], 
            location_detail=i['location'],
            lng=i['lng'],
            lat=i['lat'],
        )
        print(i['lat'])
        
        location_list.append(location)
    serializer = GetStoreLocationSerializer(location_list, many=True)
    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_store_location(request):
    business_store = request.GET.get('business_store', None)
    
    if business_store is None:
        return Response(
            {
                'success': False,
                'message': 'fields are required',
                'fields' : 'business_store'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        business = BusinessStore.objects.get(id = business_store)
    except Exception as e:
        return Response({'success': False, 'message': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
    location_list = []
    try:
        business_location = StoreLocation.objects.filter(business_store=business)
        location_list.append(business_location)
        
    except Exception as e:
        return Response({'success': False, 'message': str(e)},
                        status=status.HTTP_404_NOT_FOUND)
    print(business_location)
    serializer = GetStoreLocationSerializer(business_location, many = True)
    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_general_setting(request):
    language = request.data.get('language', None)
    currency = request.data.get('currency', None)
    user = request.user

    if language:
        user.language = language
    if currency:
        # currency = int(currency)
        # try:
        #     currency = Currency.objects.get(id=currency)
        # except:
        #     pass
        user.currency_id = currency
    user.save()
    return Response({"success": True, 'response': 'General settings updated successfully!'
                                        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_locations_by_store(request):
    store_id = request.query_params.get('store_id', None)

    if not store_id:
        return Response({"success": False, 'response': {'message': 'Invalid data!'}},
            status=status.HTTP_200_OK)

    locations = StoreLocation.objects.filter(business_store=store_id)
    serializer = GetStoreLocationSerializer(locations, many=True)
    return Response({"success": True, 'response': serializer.data
                                        }, status=status.HTTP_200_OK)