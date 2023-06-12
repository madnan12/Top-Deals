from locale import currency
from unicodedata import category, name
from django.db import models
# from django.contrib.gis.geos import Point
# from django.db import models
# from django.contrib.gis.db import models
from .models import *
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from store.constant import create_slug, compress_saved_image, upload_to_bucket, unique_item_name
import uuid
from geopy.geocoders import Nominatim
from decimal import Decimal
from django.contrib.auth.models import PermissionsMixin

# Create your models here.

class Country(models.Model):
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    country_code = models.CharField(max_length=32, null=True, blank=True)
    dial_code = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.name



class State(models.Model):
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class City(models.Model):
    counter = models.BigIntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=256)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name


class Currency(models.Model):
    name = models.CharField(max_length=55, null=True, blank=True)
    code = models.CharField(max_length=16, null=True, blank=True)
    currency_symbol = models.CharField(max_length=16, null=True, blank=True)

    def __str__(self):
        return self.name


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser ,PermissionsMixin):
    SOCIAL_PLATFORM_CHOICES = [
        ('Google', 'Google'),
        ('Facebook', 'Facebook'),
    ]
    USER_TYPE = [
        ('Business', 'Business'),
        ('Customer', 'Customer'),
    ]
    USER_LANGUAGE = [
        ('English', 'English'),
        ('Arabic', 'Arabic'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ]

    BUSINESS_STATUSES = [
        ('Pending' , 'Pending'),
        ('Approved' , 'Approved'),
        ('Rejected' , 'Rejected'),
    ]
    # Required Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True, null=False, blank=False)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # User Defined Fields
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    dial_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    business_address = models.CharField(max_length=1000, null=True, blank=True)
    social_account = models.BooleanField(default=False)
    social_platform = models.CharField(max_length=32, choices=SOCIAL_PLATFORM_CHOICES, null=True, blank=True)
    user_type = models.CharField(max_length=32, choices=USER_TYPE, default='Customer', null=True, blank=True)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True, blank=True)
    # business_approved = models.CharField(max_length=255, choices=BUSINESS_STATUS, null=True, blank=True, default='Pending')
    language = models.CharField(max_length=255, choices=USER_LANGUAGE, null=True, blank=True, default='English')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    logo = models.ImageField(upload_to='Business_logo/logo/%Y/%m',null=True, blank=True)
    category = models.ForeignKey('store.Category', on_delete=models.CASCADE, null=True, blank=True, related_name='user_category')
    subcategory = models.ForeignKey('store.SubCategory', on_delete=models.CASCADE, null=True, blank=True, related_name='user_subcategory')
    terms_condition = models.TextField(null=True, blank=True)

    reward_point = models.IntegerField(null=True, blank=True)
    license_id = models.CharField(max_length=32, null=True, blank=True)
    license_document = models.FileField(upload_to='Business/docs/%Y/%m',null=True, blank=True)
    location_business = models.CharField(max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    business_approved = models.BooleanField(default=False)
    is_account_officer = models.BooleanField(default=False)
    business_status = models.CharField(choices=BUSINESS_STATUSES, default='Pending', max_length=20)
    facebook_link = models.CharField(max_length=255, null=True, blank=True, default='')
    instagram_link = models.CharField(max_length=255, null=True, blank=True, default='')
    twitter_link = models.CharField(max_length=255, null=True, blank=True, default='')



    is_email_verified = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_finance =models.BooleanField(default=False)
    is_customer_service = models.BooleanField(default=False)
    is_account_management =models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyAccountManager()

    def __str__(self):
        if self.username:
            return self.username
        else:
            return self.email

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def get_name(self):
        if ' ' in self.name:
            name = self.name.split(' ')[0]
        else:
            name = self.name
        return name

class UserAccountHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="useraccounthistory_user")
    current_status = models.BooleanField(default=False)
    next_valid_status = models.BooleanField(default=False)
    next_fail_status = models.BooleanField(default=False)
    next_change_status = models.BooleanField(default=False)
    comments = models.CharField(max_length=1000, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    

class UserReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userreminder_user")
    title = models.CharField(max_length=500, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    redirect_url = models.CharField(max_length=1000, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    


class UserKpi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userkpi_user")
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_saved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.user.username
    


class UserWallet(models.Model):
    TYPE_WALLET = [
        ('RewardPoint', 'Reward Point'),
        ('Balance', 'Balance')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userwallet_user")
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=500, choices=TYPE_WALLET ,blank=True, null=True)
    amount = models.IntegerField(null=True, blank=True)
    redeemed = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.user.username
    

STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="category_user", null=True, blank=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=50, choices=STATUS, default='Active')

    image = models.ImageField(upload_to='Business/Category/%Y/%m',null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(Category.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(Category, self).save(*args, **kwargs)


    def __str__(self):
        return self.name
    

STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)
class SubCategory(models.Model):
    # ForignKey Field
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategory_category")

    name = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    status = models.CharField(max_length=50, choices=STATUS, default='Active')

    image = models.ImageField(upload_to='Business/SubCategory/%Y/%m',null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(SubCategory.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    



class SubSubCategory(models.Model):

    # ForignKey Field
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="subsubcategory_sub_category")

    name = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)

    image = models.ImageField(upload_to='Business/SubSubCategory/%Y/%m',null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)  

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(SubSubCategory.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        super(SubSubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    
class VerificationCode(models.Model):
    # Foreign Key
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    code = models.CharField(max_length=20, null=True, blank=True)
    used = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    reset_pass = models.BooleanField(default=False)

    # WHO Columns
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.code) + " " + str(self.user)

    def get_username(self):
        return str(self.user.username) if self.user else 'N/A'



class Banner(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    country =models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)    
    status = models.BooleanField(default=True)
    company = models.CharField(max_length=55, null=True, blank=True)
    phone = models.CharField(max_length=55, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    redirect_url = models.CharField(max_length=1000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)


    def __str__(self):
        return str(self.id)

class BannerMedia(models.Model):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, null=True, blank=True, related_name='bannermedia_banner')
    image = models.ImageField(upload_to='Banner/BannerMedia/%Y/%m',null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.banner.id)
    

class DeleteAccountRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='deleteaccountrequest_user')
    is_approved = models.BooleanField(default=False) 
    
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


STORE_STATUS = (
    ('Pending', 'Pending'),
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)
class BusinessStore(models.Model):
    BILLING_CHOICES = [
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    VERIFICATION_STATUS = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]
    # Foreign Keys
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='businessstore_user')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,related_name='categorystore_category')
    subcategory = models.ManyToManyField(SubCategory, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)

    name = models.CharField(max_length=255, null=True, blank=True)
    unique_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)
    web_url = models.CharField(max_length=1000, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission = models.IntegerField(null=True, blank=True)
    pin_code = models.IntegerField(null=True, blank=True)
    verification_status = models.CharField(max_length=255, choices=VERIFICATION_STATUS, default='Pending', null=True, blank=True)
    business_logo = models.ImageField(upload_to='BusinessLogo/Logo/%Y/%m',null=True, blank=True)
    store_address = models.CharField(max_length=255, null=True, blank=True)
    average_rate = models.IntegerField(null=True, blank=True)
    store_status = models.CharField(max_length=50, choices=STORE_STATUS, default='Pending')
    billing_reccurence = models.CharField(max_length=100, choices=BILLING_CHOICES, null=True, blank=True)
    lat=models.CharField(max_length=20,null=True, blank=True, default=None)
    lon=models.CharField(max_length=20,null=True, blank=True, default=None)
    license_id = models.CharField(max_length=32, null=True, blank=True)
    total_order = models.IntegerField(null=True, blank=True)
    license_document = models.FileField(upload_to='Business/docs/%Y/%m', null=True, blank=True)
    
    commission_fee = models.IntegerField(null=True, blank=True)
    reservation_fee = models.IntegerField(null=True, blank=True)

    is_account_officer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     geolocator=Nominatim(user_agent="geoapiExercises")
    #     location=geolocator.geocode(int(self.pincode))
    #     self.lat=location.latitude
    #     self.lon=location.longitude
    #     super(BusinessStore,self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(BusinessStore.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.name, slugs=slugs)
        # if not self.unique_name:
        #     name_a = BusinessStore.objects.filter(name=self.name).last()
        #     self.unique_name = unique_item_name(name=self.name)
        #     # self.unique_name = self.name + "-1"
        #     if name:
        #         if "-" in name.unique_name:
        #             count = name.split('-')[-1]
        #             count = int(count)+1
        #             self.unique_name = name[:-1] + str(count)
        #     else:
        #         self.unique_name = self.name + "-1"
        if not self.unique_name:
            p_id = BusinessStore.objects.last()
            if not p_id:
                self.unique_name = self.name + "-1"
            else:
                self.unique_name = self.name + "-" + str(p_id.id+1)
        super(BusinessStore, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class StoreLocation(models.Model):
    business_store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storelocation_business_store')

    location_detail = models.JSONField(default='')
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=55, null=True, blank=True)
    adress = models.CharField(max_length=500, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True, related_name='storelocation_city')
    area = models.CharField(max_length=500, null=True, blank=True)
    status = models.BooleanField(default=False)
    quantity = models.IntegerField(null=True, blank=True)

    lng = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    lat = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.adress)


class StoreKpi(models.Model):
    business_store = models.OneToOneField(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storekpi_business_store')
    published = models.BooleanField(default=False)
    redeemed = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_store)


class StoreService(models.Model):
    business_store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storeservice_business_store')
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.store)

class StoreMedia(models.Model):
    business_store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storemedia_business_store')
    image = models.ImageField(upload_to='StoreMedia/Images/%Y/%m',null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_store)

class StoreOpening(models.Model):
    store_location = models.ForeignKey(StoreLocation, on_delete=models.CASCADE, null=True, blank=True, related_name='storeopening_store_location')
    start_time = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.store_location)


class StoreLicense(models.Model):
    business_store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storelicense_business_store')
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='storelicense_user')
    license_document = models.FileField(upload_to='StoreLicense/docs/%Y/%m',null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_store)


class StoreRating(models.Model):
    business_store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, null=True, blank=True, related_name='storerating_business_store')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='storerating_user')
    review = models.TextField(null=True, blank=True)
    rate = models.FloatField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_store)


class Ticket(models.Model):
    # ForeignKey
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket_admin_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='ticket_user')

    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

class TicketHistory(models.Model):
    # ForeignKey
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='tickethistory_ticket')
    dmin_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tickethistory_admin_user')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tickethistory_user')

    status = models.BooleanField(default=False)
    comment = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


class BusinessDeal(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Both', 'Both'),
        ('Other', 'Other')
    ]
    DEAL_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    create_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_in_deals')
    store = models.ForeignKey(BusinessStore, on_delete=models.SET_NULL, null=True, blank=True, related_name='businessdeal_store')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='businessdeal_category')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='businessdeal_sub_category')
    sub_sub_category = models.ForeignKey(SubSubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='businessdeal_sub_sub_category')
    location = models.ManyToManyField(StoreLocation, null=True, blank=True, default='')

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)

    term_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=500, null=True, blank=True)
    unique_title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    condition = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    discount_price = models.IntegerField(null=True, blank=True)
    discount_percentage = models.IntegerField(null=True, blank=True, default='0')
    quantity = models.IntegerField(null=True, blank=True)
    delivery_charges = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=255, choices=GENDER_CHOICES, null=True, blank=True)
    deal_status = models.CharField(max_length=255, choices=DEAL_STATUS_CHOICES, null=True, blank=True, default='Active')
    status = models.BooleanField(default=True)
    view_count = models.BigIntegerField(default=0)
    phone = models.CharField(max_length=20, null=True, blank=True, default=None)

    lat = models.CharField(max_length=20,null=True, blank=True, default=None)
    lon = models.CharField(max_length=20,null=True, blank=True, default=None)
    
    # location = models.PointField(srid=4326, geography=True, blank=True, null=True)

    longitude = models.DecimalField(max_digits=30, decimal_places=16, null=True, blank=True)
    latitude = models.DecimalField(max_digits=30, decimal_places=16,  null=True, blank=True)
    start_time = models.TimeField(auto_now_add=False, null=True, blank=True)
    end_time = models.TimeField(auto_now_add=False, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_continue = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    class Meta:
        db_table = 'BusinessDeal'

    @property
    def image(self):
        deal_medias = DealMedia.objects.filter(business_deal__id=self.id)
        if len(deal_medias) > 0:
            return deal_medias[0].image.url

        return ''

    def get_discount_price(self):
        discount_price_by_offer = (100-self.discount_percentage)
        actual_discount_price = (self.price / 100) * discount_price_by_offer
        return actual_discount_price

    def get_highest_discount(self):
        discount_list = []
        discount_by_offer = DifferentDealData.objects.filter(deal=self.id)
        if discount_by_offer:
            for discount in discount_by_offer:
                discount_list.append(discount.discount_percentage)
        if len(discount_list) > 0:
            discount_list.sort()
            return discount_list[-1]
        else:
            return

    def deal_rating(self):
        all_rating = DealRating.objects.filter(business_deal=self.id).all()
        if all_rating:
            rating_count = len(all_rating)
            sum = 0
            for i in all_rating:
                sum = sum + i.rate
            rating = sum / rating_count
        else:
            rating = 0
            rating_count = 0
        return rating

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(BusinessDeal.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.title, slugs=slugs)
        # if self.lon and self.lat:
        #     self.location = Point(self.lon, self.lat)
        super(BusinessDeal, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)

class DifferentDealData(models.Model):
    deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, related_name='businessdeal_data')
    title = models.CharField(max_length=500, default='')
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(default='')
    price = models.IntegerField(default=0)


    discount_percentage = models.IntegerField(default=0)


    no_seats = models.IntegerField(default=0, verbose_name = 'No of seats')
    no_seats_booked = models.IntegerField(default=0, verbose_name = 'No of seats booked ')


    quantity = models.IntegerField(default=0)
    reservation_fee = models.IntegerField(default=0)

    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    def get_discount_price(self):
        discount_price_by_offer = (100-self.discount_percentage)
        actual_discount_price = (self.price / 100 ) * discount_price_by_offer
        return actual_discount_price

    def save(self, *args, **kwargs):
        if not self.slug:
            slugs = list(DifferentDealData.objects.all().values_list('slug', flat=True))
            self.slug = create_slug(name=self.title, slugs=slugs)
        super(DifferentDealData, self).save(*args, **kwargs)
    
    @property
    def image(self):
        deal_medias = DealMedia.objects.filter(business_deal=self.deal)
        if len(deal_medias) > 0:
            return deal_medias[0].image.url

        return ''

    @property
    def location(self):
        try:
            store_locations = StoreLocation.objects.filter(business_store=self.deal.store)
            if len(store_locations) > 0 :
                return store_locations[0].adress
            else:
                return 'No Location'
        except Exception as err:
            return 'No Location'

    def __str__(self):
        return self.title


class DealRating(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='business_deal_in_dealrating')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_in_dealrating')
    review = models.TextField(null=True, blank=True)
    rate = models.FloatField(default=0, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True ,null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)




class DealAvailability(models.Model):
    # Foreign Key
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='dealavailability_business_deal')

    valid_date = models.DateTimeField(null=True, blank=True)
    start_slot = models.DateTimeField(null=True, blank=True)
    end_start = models.DateTimeField(null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    status = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)

    # WHO
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)

class DealImpression(models.Model):
    # Foreign Key
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='dealimpression_business_deal')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='dealimpression_user')

    # WHO
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return str(self.business_deal)



class DealClick(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='dealclick_business_deal')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='dealclick_user')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)




class DealMedia(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='dealmedia_business_deal')
    image = models.ImageField(upload_to='DealMedia/Images/%Y/%m',null=True, blank=True)
    video = models.FileField(upload_to='DealMedia/Video/%Y/%m', null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)
        



class DealDiscount(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='dealdiscount_business_deal')
    voucher_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fix_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    deal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)
        

class PromotedDeal(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='promoteddeal_business_deal')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.business_deal)


class Transaction(models.Model):
    PAYMENT_CHOICES = [
        ('Promo', 'Promo'),
        ('Commission', 'Commission'),
        ('Purchase', 'Purchase'),
    ]
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    ]
    PAYMENT_TYPE_METHOD = [
        ('Card', 'Card'),
        ('Transfer', 'Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_user')
    payment_type = models.CharField(max_length=255, choices=PAYMENT_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, null=True, blank=True)
    transaction_detail = models.JSONField(default='')
    amount = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.SET_NULL, null=True, blank=True, related_name='transaction_business_deal')
    commission_invoice = models.IntegerField(null=True, blank=True)
    promoted_deal_invoice = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=255, choices=PAYMENT_TYPE_METHOD, null=True, blank=True)
    month_period = models.DateTimeField(null=True, blank=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


class TransactionAttchment(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='transactionattchment_transaction')
    scan_bil = models.ImageField(upload_to='TransactionAttchment/Images/%Y/%m',null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.transaction)



class TransactionHistory(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name='transactionhistory_transaction')
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='transactionhistory_admin_user')
    status = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.transaction)


class CommissionIncoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='commissionininvoice_user')
    period = models.IntegerField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=255, null=True, blank=True)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.user)


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_cart_items', null=True, blank=True)
    deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, related_name='deal_cart_items', null=True, blank=True)
    store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, related_name='store_cart_items', null=True, blank=True)
    option_id = models.ForeignKey(DifferentDealData, on_delete=models.CASCADE, related_name='store_cart_items', null=True, blank=True)

    discount_price = models.IntegerField(null=True, blank=True) # single item discounted price
    orignal_price = models.IntegerField(null=True, blank=True) # single item orignal price
    delivery_charges = models.IntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.quantity * self.deal.discount_price

    @property
    def image(self):
        deal_medias = DealMedia.objects.filter(business_deal=self.deal)
        if len(deal_medias) > 0:
            return deal_medias[0].image.url

        return ''

    @property
    def location(self):
        try:
            store_locations = StoreLocation.objects.filter(business_store=self.store)
            if len(store_locations) > 0:
                return store_locations[0].adress
            else:
                return 'No Location'
        except Exception as err:
            return 'No Location'

    @property
    def reservation_fee(self):
        try:
            return self.option_id.reservation_fee
        except Exception as err:
            return 0

STATE_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel')
)
PAYMENT_CHOICES = (
    ('Cash', 'Cash'),
    ('Card', 'Card'),
    ('Stripe', 'Stripe'),
    ('Paypal', 'Paypal')
)

class OrderPlaced(models.Model):
    id = models.CharField(editable=False, unique=True, primary_key=True, default=uuid.uuid4, max_length=1000)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_orders_placed')
    # deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, related_name='deal_orders_places')
    # store = models.ForeignKey(BusinessStore, on_delete=models.CASCADE, related_name='store_orders_placed')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)

    # discount_price = models.IntegerField(null=True, blank=True) # single item discounted price
    # delivery_charges = models.IntegerField(null=True, blank=True)
    # quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=50, choices=STATE_CHOICES, default='Accepted')

    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(verbose_name="email", max_length=255, default='')
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=1000, null=True, blank=True)

    qr_image = models.ImageField(upload_to='deals/qr_code_images/', null=True, blank=True)

    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Cash')
    reservation_fee = models.PositiveIntegerField(default=20, verbose_name='Reservation Fee in Dirham')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    @property
    def total_cost(self):
        return self.quantity * self.deal.discount_price
    
    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    id = models.UUIDField(editable=False, unique=True, primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(OrderPlaced, on_delete=models.CASCADE, related_name='order_items')

    deal_option = models.ForeignKey(DifferentDealData, on_delete=models.SET_NULL, null=True, related_name='deal_option_orders')
    quantity = models.PositiveIntegerField(default=1)
    discount = models.IntegerField(default=0, verbose_name='Current Discount in Percentage')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def name(self):
        return self.deal_option.title
    
    @property
    def image(self):
        return self.deal_option.image

    def __str__(self):
        return str(self.id)


class OrderCardCheckout(models.Model):
    id = models.UUIDField(editable=False, unique=True, primary_key=True, default=uuid.uuid4)
    order = models.OneToOneField(OrderPlaced, on_delete=models.PROTECT, related_name='order_checkout')

    card_number = models.CharField(default='', max_length=24)
    card_holder = models.CharField(max_length=100, default='')
    expire_at = models.DateField(null=True, blank=True)
    cvv = models.CharField(max_length=5, default='')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Order Bank Card Checkout Detail'
        verbose_name_plural = 'Order Bank Card Checkout Details'




class Account_Officer(models.Model):
    STATE_CHOICES_OFFICER = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_accountofficer_user")
    account_officer_name = models.CharField(max_length=228, null=True, blank=True)
    business_store = models.ManyToManyField(BusinessStore, null=True, blank=True, related_name='account_officer_business_store')
    account_officer_status = models.CharField(max_length=32, choices=STATE_CHOICES_OFFICER, null=True, blank=True)
    image_logo = models.ImageField(upload_to='Business_logo/AccountOfficer/%Y/%m', null=True, blank=True)

    def __str__(self):
        return self.account_officer_name


class WebDynamicContent(models.Model):
    terms_conditions = models.TextField(null=True, blank=True)
    privacy_policy = models.TextField(null=True, blank=True)
    about_us = models.TextField(null=True, blank=True)
    faq = models.TextField(null=True, blank=True)
    contact_us = models.TextField(null=True, blank=True)


class Faq(models.Model):
    faq_question = models.TextField(null=True, blank=True)
    faq_answer = models.TextField(null=True, blank=True)

class NewsLetter(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_newsletter", null=True, blank=True)
    email = models.CharField(max_length=228, null=False, blank=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class ExceptionRecord(models.Model):
    text = models.TextField()

    def __str__(self):
        return str(self.id)


class RandomFiles(models.Model):
    image = models.ImageField(upload_to='random_images/')

    def __str__(self):
        return str(self.id)


class DealLocation(models.Model):
    business_deal = models.ForeignKey(BusinessDeal, on_delete=models.CASCADE, null=True, blank=True, related_name='deallocation_deal')
    location = models.ForeignKey(StoreLocation, on_delete=models.CASCADE, null=True, blank=True, related_name='deallocation_locations')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)