from django.conf import  settings
from .models import *
from store.forms import  NormalUserForm, BusinessUserForm
import json

from Constants.Location import get_user_current_location
from Constants.Flags import WORLD_FLAGS, ENABLED_COUNTRIES, ENABLED_COUNTRIES_DICT

def globle_functon(request):
    form = NormalUserForm(request.POST)
    form = BusinessUserForm(request.POST)
    parent_category = Category.objects.all()
    parent_category_by_order = Category.objects.order_by('-id')
    business_store = BusinessStore.objects.filter(is_account_officer=False, status=True)
    all_countries = Country.objects.all()
    
    all_currency = Currency.objects.all()
    parent_category_filter_by_status = Category.objects.filter(status='Active')
    parent_category_filter_by_status_with_limit = Category.objects.filter(status='Active')[:8]
    category = Category.objects.filter(status='Active')
    get_sub_category = SubCategory.objects.filter(status='Active')

    # business_profile = User.objects.filter(is_active=True).exclude(license_document='')
    front_url = settings.FRONTEND_SERVER_NAME

    context = {}
    context['parent_category'] = parent_category
    context['parent_category_by_order'] = parent_category_by_order
    context['parent_category_filter_by_status'] = parent_category_filter_by_status
    context['parent_category_filter_by_status_with_limit'] = parent_category_filter_by_status_with_limit
    context['form'] = form
    context['business_store'] = business_store
    context['get_sub_category'] = get_sub_category

    context['category'] = category
    context['all_countries'] = all_countries
    context['all_currency'] = all_currency
    context['allowed_countries'] = ENABLED_COUNTRIES

    if request.user.is_authenticated:
        context['cart_options'] = CartItem.objects.filter(user=request.user).count()
    else:
        cart_items = request.COOKIES.get('cart_items' , [])
        if type(cart_items) == str:
            cart_items = json.loads(cart_items)
        context['cart_options'] = len(cart_items)

    context['front_url'] = front_url
    context['query_params'] = dict(request.GET)
    listed_query_params = ''
    for index, query in enumerate(dict(request.GET).items()):
        ky, val = query
        if index == 0:
            listed_query_params += '?'
        else:
            listed_query_params += '&'

        listed_query_params += f'{ky}={val[0]}'
    context['listed_query_params'] = listed_query_params

    country_code = request.META.get('country_code' , None)
    if country_code is None:
        user_location = get_user_current_location(request)
        country_code = user_location['country_code'].lower()

    selected_country = ENABLED_COUNTRIES_DICT.get(country_code)
    context['selected_country'] = selected_country

    current_path = request.META['PATH_INFO']
    current_path = current_path.split('/')
    current_path = current_path[2:-1]
    current_path = '/'.join(current_path)
    context['current_path'] = current_path


    if country_code is not None:
        all_cities = City.objects.filter(state__country__country_code__icontains=country_code)
    else:
        all_cities = []
    
    context['cities'] = all_cities


    search_queries = {}
    for query, val in request.GET.items():
        search_queries[query] = val

    context['search_queries'] = search_queries


    selected_category = search_queries.get('category' , None)
    selected_category_sub_categories = []
    if selected_category is not None:
        selected_category_sub_categories = SubCategory.objects.filter(category__slug=selected_category , status='Active')

    context['selected_category_sub_categories'] = selected_category_sub_categories
    



    return context