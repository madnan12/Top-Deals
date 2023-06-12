from django.urls import path, include
from store.views import api, custom_view
from django.contrib.auth import views as auth_views

from store.views.api import *
from store.views.custom_view import *
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required
router = DefaultRouter()
#

urlpatterns = [
    #Subcategory search
    path('api/get_subcategory_deals/', api.get_subcategory_deals),
    path('api/sub_category_view_busines/', SubCategoryViewBusiness.as_view({'get': 'list'}), name="sub_category_view"),

    
    # API URL 
    path('api/register/', api.register),
    path('api/login/', api.login),
    path('api/verify_email/', api.verify_email),
    path('api/resend_code/', api.resend_code),
    path('api/reset_password/', api.reset_password),
    path('api/change_password/', api.change_password),
    path('api/get_user_profile/', api.get_user_profile),
    # path('api/delete_profile/', api.delete_profile),
    path('api/update_profile/', api.update_profile),
    # path('api/update_profile/', api.web_dynamic_content),

    path('api/create_category/', api.create_category),
    path('api/get_all_categories/', api.get_all_categories), 
    path('api/delete_category/', api.delete_category),
    path('api/update_category/', api.update_category),
    path('api/near_deals/', api.near_deals),

    path('api/create_store/', api.create_store),
    path('api/delete_store/', api.delete_store), # work on it
    path('api/get_user_stores/', api.get_user_stores),
    path('api/update_store/', api.update_store),
    # path('api/all_store_active_inactive/', api.All_Store_Active_Inactive),
    path('api/all_store_active_inactive/', All_Store_Active_Inactive.as_view({'get': 'list_stores'}), name="list_stores"),

    # Deal URL
    path('api/add_deal/', api.add_deal),
    path('api/get_store_deals/', api.get_store_deals),
    path('api/delete_deal/', api.delete_deal),
    path('api/update_deal/', api.update_deal),
    path('api/get_single_deal/', api.get_single_deal),
    path('api/list_deals_by_four/', Single_Store_All_Deals.as_view({'get': 'list_deals'}), name="list_deals_by_four"),

    path('api/create_social_login/', api.create_social_login),
    path('api/get_countries/', api.get_countries),
    path('api/get_cities/', api.get_cities),
    path('api/update_general_setting/', api.update_general_setting),


    path('api/add_store_rating/', api.add_store_rating),
    path('api/get_store_rating/', api.get_store_rating),
    path('api/delete_store_rating/', api.delete_store_rating),
    path('api/update_store_rating/', api.update_store_rating),
    path('api/get_currency/', api.get_currency),


    path('api/validate_login_user/', api.validate_login_user),
    path('api/get_locations_by_store/', api.get_locations_by_store),


    path('api/logout/', Logout.as_view(), name="logout"),
    path('api/banner_view/', BannerView.as_view({'get': 'list'}), name="banner_view"),
    path('api/category_view/', CategoryView.as_view({'get': 'list'}), name="category_view"),
    path('api/category_deals/', Category_Deals.as_view({'get': 'category_deals'}), name="category_deals"),
    path('api/subcategory_deals/', SubCategory_Deals.as_view({'get': 'subcategory_deals'}), name="subcategory_deals"),

    path('api/sub_category_view/', SubCategoryView.as_view({'get': 'list'}), name="sub_category_view"),

    path('api/currency_list/', CurrencyView.as_view({'get': 'currency_list'}), name="currency_list"),

    path('api/user_profile/', UserProfile.as_view({'get': 'retrievee', 'patch': 'partial_updatee'}), name="user_profile"),
    path('api/business_user_profile/', BusinessUserProfile.as_view({'get': 'retrievee', 'patch': 'partial_updatee'}), name="business_user_profile"),
    path('api/change_user_password/', UserChangePasswrodView.as_view({'put': 'updatee'}), name="change_user_password"),
    path('api/business_change_user_password/', BusinessUserChangePasswrodView.as_view({'put': 'updatee'}), name="business_change_user_password"),

    path('api/search_with/', SearchAPIView.as_view({'get': 'search_function'}), name="search_with"),
    path('api/filter_deals/', FilterView.as_view({'post': 'list'}), name="filter_deals"),

    path('api/update_option/', UpdateOptionView.as_view({'patch': 'update_option'}), name="update_option"),

    path('api/email_validation/', EmailValidateView.as_view({'post': 'email_validate'}), name="email_validation"),

    path('api/add_to_cart/', AddToCartView.as_view({'get': 'list', 'post':'create'}), name="add_to_cart"),
    path('api/add_to_cart/<int:id>/', AddToCartView.as_view({'patch': 'partial_update', 'get': 'retrieve', 'delete': 'delete'}), name="filter_deals"),
    path('api/place_order/', OrderPlacedView.as_view({'post': 'create'}), name="filter_deals"),

    path('api/top_offers/', Top_Offers.as_view({'get': 'list_top_offers'}), name="top_offers"),
    path('api/nearby_deals/', Nearby_Deals.as_view({'get': 'list_nearby_deals'}), name="nearby_deals"),
    path('api/list_best_seller/', Best_Seller.as_view({'get': 'list_best_seller'}), name="list_best_seller"), # also use with admin dashbord / bussiness
    path('api/list_deals_of_the_day/', Deals_Of_The_Day.as_view({'get': 'list_deals_of_the_day'}), name="list_deals_of_the_day"),

    # Bussiness Dashboard
    path('api/recent_orders/', Recent_Orders.as_view({'get': 'recent_orders'}), name="recent_orders"),
    path('api/recent_reviews/', Recent_Reviews.as_view({'get': 'recent_reviews'}), name="recent_reviews"),
    path('api/validate_user/', api.validate_user),
    path('api/add_store_location/', api.add_store_location),
    path('api/get_store_location/', api.get_store_location),

    # single user all orders
    path('api/user_placed_orders/', UserOrdersListView.as_view({'get': 'user_placed_orders'}), name="user_placed_orders"),
    path('api/cart_order_checkout/', cart_order_checkout, name="cart_order_checkout"),

    # DJANGO FUNCTION

    # path('business_dashboard/', custom_view.business_dashboard, name='business_dashboard'),
    path('account-officer/', custom_view.account_officer, name='account_officer'),
    path('account_officer_detail/', custom_view.account_officer_detail, name='account_officer_detail'),
    path('account-officer-reviews/', custom_view.account_officer_reviews, name='account-officer-reviews'),
    path('account-officer-complain/', custom_view.account_officer_complain, name='account-officer-complain'),
    path('account-officer-order/', custom_view.account_officer_order, name='account_officer_order'),
    path('load_store_location/', custom_view.load_store_location, name='load_store_location'),


    path('', custom_view.home, name='home'),
    path('accounts/', include('allauth.urls')),
    path('register/', custom_view.register, name='register'),
    path('verify_email/<str:id>/', custom_view.verify_email, name='verify_email'), 
    path('merchant_login/', custom_view.merchant_login, name='merchant_login'), 
    # path('login/', custom_view.login, name='login'),

    path('admin_profile/', custom_view.admin_profile, name='admin_profile'),
    path('site-settings/', custom_view.site_settings, name='site_settings'),
    path('admin-password/', custom_view.admin_password, name='admin_password'),
    path('admin_password_chnage/', custom_view.admin_password_chnage, name='admin_password_chnage'),
    path('social-url/', custom_view.social_url, name='social_url'),
    # path('admin-socials/', custom_view.admin_socials, name='admin_socials'),
    # path('admin-lang_cur/', custom_view.admin_lang_cur, name='admin_lang_cur'),
    path('admin_dashboard/', custom_view.admin_dashboard, name='admin_dashboard'),
    path('customers/', custom_view.customers, name='customers'),
    path('orders/', custom_view.orders, name='orders'),
    path('invoices/', custom_view.invoices, name='invoices'),
    path('credits/', custom_view.credits, name='credits'),
    path('redeem-rewards/', custom_view.redeem_rewards, name='redeem-rewards'),
    path('web_dynamic_content/', custom_view.web_dynamic_content, name='web_dynamic_content'),
    path('add_store_location/<str:slug>/', custom_view.add_store_location, name='add_store_location'),


    path('account_officer/', custom_view.account_officer, name='account_officer'),
    path('add_account_officer/', custom_view.add_account_officer, name='add_account_officer'),
    path('delete_account_officer/<int:id>', custom_view.delete_account_officer, name='delete_account_officer'),
    path('edit_account_officer/<int:id>', custom_view.edit_account_officer, name='edit_account_officer'),
    path('account_officer_update/<int:id>', custom_view.account_officer_update, name='account_officer_update'),
    path('admin_category/', custom_view.admin_category, name='admin_category'),
    path('featured_deals/', custom_view.featured_deals, name='featured_deals'),
    path('logout/', custom_view.logout_view, name='logout'),
    path('ajax/load-cities/', custom_view.load_cities, name='ajax_load_cities'),
    path('ajax/load-categories/', custom_view.load_categories, name='ajax_load_categories'),
    path('resend_code/', custom_view.resend_code, name='resend_code'),
    path('resend_code_reg_user/<str:id>', custom_view.resend_code_reg_user, name='resend_code_reg_user'),
    path('change_password/', custom_view.change_password, name='change_password'),
    path('reset_password/', custom_view.reset_password, name='reset_password'),

    path('update_business_profile/', custom_view.update_business_profile, name='update_business_profile'),
    path('update-business-password/', custom_view.update_business_password, name='update_business_password'),
    path('update-business-len-cur/', custom_view.update_business_len_cur, name='update_business_len_cur'),
    path('search_deals/', custom_view.search_deals, name='search_deals'),

    # banner for mvt end points
    path('banner_create/', custom_view.banner_create, name='banner_create'),
    path('admin_content/', custom_view.admin_content, name='admin_content'),
    path('banner_retrieve/<int:id>', custom_view.banner_retrieve, name='banner_retrieve'),
    path('banner_destroy/<int:id>', custom_view.banner_destroy, name='banner_destroy'),
    path('banner_update/<int:id>', custom_view.banner_update, name='banner_update'),

    path('remove_logo/', custom_view.remove_logo, name='remove-logo'),
    path('remove_logo_business/', custom_view.remove_logo_business, name='remove_logo_business'),

    # category for mvt end points
    path('category_create/', custom_view.category_create, name='category_create'),
    path('category_retrieve/<int:id>', custom_view.category_retrieve, name='category_retrieve'),
    path('category_destroy/<int:id>', custom_view.category_destroy, name='category_destroy'),
    path('category_update/<int:id>', custom_view.category_update, name='category_update'),

    # subcategory for mvt end points
    path('subcategory_create/', custom_view.subcategory_create, name='subcategory_create'),
    path('subcategory_retrieve/<int:id>', custom_view.subcategory_retrieve, name='subcategory_retrieve'),
    path('subcategory_destroy/<int:id>', custom_view.subcategory_destroy, name='subcategory_destroy'),
    path('subcategory_update/<int:id>', custom_view.subcategory_update, name='subcategory_update'),
    path('search_all/', custom_view.search_all, name='search_all'),

    # user profile for mvt end points customer
    path('update_user_profile/', custom_view.update_user_profile, name='update_user_profile'),
    path('user-profile/', custom_view.user_profile, name='user_profile'),
    # path('customer-profile/', custom_view.retrieve_user_profile, name='customer_profile'),

    # business store for mvt
    path('create_store/', custom_view.create_store, name='create_store'),
    path('update_store/<int:id>', custom_view.update_store, name='update_store'),
    path('retrieve_store/<int:id>', custom_view.retrieve_store, name='retrieve_store'),
    path('delete_store/<int:id>', custom_view.delete_store, name='delete_store'),


    # Store Location
    # path('store-location/', custom_view.store_location, name='store-location'),
    path('business-signup/', custom_view.business_signup, name='business-signup'),


    # add to cart
    path('add-to-cart/', custom_view.add_to_cart, name='add_to_cart'),
    path('update-user-leng-cur/', custom_view.update_user_leng_cur, name='update_user_leng_cur'),


    path('cart/', custom_view.cart, name='add_to_cart'),
    path('pay_now/', custom_view.pay_now, name='pay_now'),



    # deals end points for mvt
    path('admin_business/', custom_view.admin_business, name='admin_business'),
    #path('add_deal/', custom_view.add_deal, name='add_deal'),
    path("createdeal/", login_required(DealCreateView.as_view(), login_url='home'), name="DealCreateView"),
    path("create_deal/", login_required(DealCreateView2.as_view(), login_url='home'), name="create_deal"),

    # path('update_deal/<int:id>', custom_view.update_deal, name='update_deal'),
    path("DealUpdateView/<int:pk>", custom_view.DealUpdateView.as_view(), name="DealUpdateView"),
    path('delete_deal/<int:id>', custom_view.delete_deal, name='delete_deal'),
    path('edit_deal_function/<int:id>', custom_view.edit_deal_function, name='edit_deal_function'),
    path('request_verify/', custom_view.request_verify, name='request_verify'),
    path('category/<slug:category_slug>/', custom_view.view_category, name='view_category'),
    path('<str:country_code>/category/<slug:category_slug>/', custom_view.view_category, name='view_category'),
    path('deal/<str:deal_slug>/', custom_view.view_deal, name='view_deal'),
    path('verify_email_for_new_password/', custom_view.verify_email_for_new_password, name='verify_email_for_new_password'),
    # path('subcategory/<slug:category_slug>/<slug:subcategory_slug>/', custom_view.view_subcategory, name='view_subcategory'),
    # path('subcategory/<slug:category_slug>/<slug:subcategory_slug>/', custom_view.view_subcategory, name='view_subcategory'),
    path('search/filter/', custom_view.view_subcategory, name='view_subcategory'),
    path('<str:country_code>/search/filter/', custom_view.view_subcategory, name='view_subcategory'),

    # path('edit_deal/<str:slug>/', custom_view.edit_deal, name='edit_deal'),

    path('sort_deals/', custom_view.sort_deals, name='sort_deals'),
    
    path('get_webcontent/', custom_view.get_webcontent, name='get_webcontent'),

    # business user dashboard
    path('business_dashboard/', custom_view.business_dashboard, name='business_dashboard'),
    # path('single_store_dashboard/<str:slug>/', custom_view.single_store_dashboard, name='single_store_dashboard'),
    path('business_settings/', custom_view.business_settings, name='business_settings'),
    path('user_listed/', custom_view.user_listed, name='user_listed'),
    path('privacy/', custom_view.privacy, name='privacy'),
    path('get_faqs/', custom_view.get_faqs, name='get_faqs'),
    path('get_contact_us/', custom_view.get_contact_us, name='get_contact_us'),
    path('get_about_us/', custom_view.get_about_us, name='get_about_us'),

    path('all-categories/', custom_view.all_cat, name='all_cat'),
    path('ad_faq/', custom_view.ad_faq, name='all_cat'),




    path('news_letter/', custom_view.news_letter, name='news_letter'),

    path('email/view/' , custom_view.view_email),
    # http://127.0.0.1:8000/email/view/?path=email/order_confirmation.html
    path('<str:country_code>/', custom_view.home, name='home'),

]
