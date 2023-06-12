

from dataclasses import fields
from pyexpat import model
from django.db import transaction
from django.db.models.functions import Concat
from rest_framework import serializers
from store.models import *
from django.conf import settings
from django.db.models import F, Value, CharField
import os


class GetStoreLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreLocation
        fields = [
        'id',
        'business_store',
        'location_detail',
        'city',
        'lng',
        'lat',
        'adress',
        'created_at'
        ]


class StoreLocationSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            return GetStoreLocationSerializer(obj.location, many=True).data
        except Exception as err:
            print('STORE location', err)
    
    class Meta:
        model = StoreLocation
        fields = [
        'id',
        'business_store',
        'city',
        'lng',
        'lat',
        'adress',
        'store_address',
        'created_at',
        'location'
        ]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class DefaultUserSerializer(serializers.ModelSerializer):
    license_document = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()

    def get_language(self,obj):
        if obj.language:
            return obj.language
        else:
            return 'English'


    def get_currency(self, obj):
        if obj.currency:
            return obj.currency.id
        else:
            try:
                currency = Currency.objects.get(name__icontains='Dirham')
                return currency.id
            except:
                currency = None
                return currency

    def get_license_document(self, user):
        if user.license_document:
            file_url = user.license_document
            return f"{settings.S3_BUCKET_LINK}{file_url}"
        else:
            return None

    def get_logo(self, user):
        if user.logo:
            file_url = user.logo
            return f"{settings.S3_BUCKET_LINK}{file_url}"
        else:
            return None

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'is_admin', 'is_active', 'first_name', 'last_name', 'name', 'logo', 'gender',
            'phone', 'dial_code', 'country', 'city', 'business_address', 'user_type', 'reward_point', 'license_id',
            'license_document', 'location_business', 'status', 'is_phone_verified', 'is_email_verified', 'language',
            'currency', "business_status"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.category_id:
            data['category'] = Category.objects.filter(id=instance.category_id).first().name
        if instance.country_id:
            data['country'] = Country.objects.filter(id=instance.country_id).first().name
        if instance.city_id:
            data['city'] = City.objects.filter(id=instance.city_id).first().name

        return data


class AccountOfficerSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        if obj.user:
            return DefaultUserSerializer(obj.user).data
    class Meta:
        model = Account_Officer
        fields = [
                'id',
                'user',
                'account_officer_name',
                'business_store',
                'account_officer_status',
                'image_logo',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField(read_only=True)
    business_logo = serializers.SerializerMethodField()

    def get_subcategory(self, obj):
        try:
            sub = obj.subcategory.all()
            return SubcategorySerializer(sub , many =True).data
        except Exception as err:
            print(err)
            
    def get_business_logo(self, user):
        if user.business_logo:
            file_url = user.business_logo
            return f"{settings.S3_BUCKET_LINK}{file_url}"
        else:
            return None
        
    class Meta:
        model = BusinessStore
        fields = [
                'id',
                'user',
                'category',
                'subcategory',
                'country',
                'currency',
                'city',
                'slug',
                'name',
                'unique_name',
                'description',
                'phone',
                'status',
                'web_url',
                'is_deleted',
                'deal_price',
                'commission',
                'pin_code',
                'verification_status',
                'business_logo',
                'store_address',
                'average_rate',
                'store_status',
                'billing_reccurence',
                'lat',
                'lon',
                'license_id',
                'total_order',
                'license_document',
                'is_account_officer',
                'created_at',
                'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.category_id:
            data['category'] = Category.objects.filter(id=instance.category_id).first().name
        if instance.country_id:
            data['country'] = Country.objects.filter(id=instance.country_id).first().name
        if instance.city_id:
            data['city'] = City.objects.filter(id=instance.city_id).first().name
        if instance.currency_id:
            data['currency'] = Currency.objects.filter(id=instance.currency_id).first().name
        
        # if instance.subcategory_id:
        #     data['subcategory'] = SubCategory.objects.filter(id=instance.subcategory_id).first().name
        # data['media'] = StoreMedia.objects.filter(business_store=instance.id)

        data['image'] = StoreMedia.objects.filter(business_store_id=instance.id).values('id',
                            img=Concat(Value(os.getenv('FRONTEND_SERVER_NAME_s3')),F("image"),output_field=CharField()))

        # data['business_logo'] = BusinessStore.objects.filter(id=instance.id).values(logo=Concat(Value(os.getenv('FRONTEND_SERVER_NAME_s3')),F("business_logo"),output_field=CharField()))
        data['business_logo'] = str(os.getenv('FRONTEND_SERVER_NAME_s3')) + str(data['business_logo'])

        return data

    def create(self, validated_data):
        with transaction.atomic():
            nft = BusinessStore.objects.create(**validated_data)
            data = self.context['request'].data
            if 'images' in data:
                nft_docs = dict(self.context['request'].data.lists())['images']
                for doc in nft_docs:
                    StoreMedia.objects.create(business_store=nft, image=doc)
            return nft

    def update(self, instance, validated_data):
        with transaction.atomic():
            # nft = BusinessStore.objects.get(id=instance.id).update(**validated_data)
            # # nft.update()
            # instance.id = validated_data.get('email', instance.email)
            instance.category = validated_data.get('category', instance.category)
            instance.subcategory = validated_data.get('subcategory', instance.subcategory)
            instance.country = validated_data.get('country', instance.country)
            instance.currency = validated_data.get('currency', instance.currency)
            instance.city = validated_data.get('city', instance.city)
            instance.name = validated_data.get('name', instance.name)
            instance.description = validated_data.get('description', instance.description)
            instance.status = validated_data.get('status', instance.status)
            instance.store_status = validated_data.get('store_status', instance.store_status)
            instance.web_url = validated_data.get('web_url', instance.web_url)
            instance.business_logo = validated_data.get('business_logo', instance.business_logo)
            instance.store_address = validated_data.get('store_address', instance.store_address)
            instance.lat = validated_data.get('lat', instance.lat)
            instance.lon = validated_data.get('lon', instance.lon)
            instance.license_id = validated_data.get('license_id', instance.license_id)
            instance.license_document = validated_data.get('license_document', instance.license_document)
            instance.save()
            data = self.context['request'].data
            if 'images' in data:
                nft_docs = dict(self.context['request'].data.lists())['images']
                if nft_docs:
                    old_img = StoreMedia.objects.filter(business_store=instance)
                    old_img.delete()
                for doc in nft_docs:
                    StoreMedia.objects.create(business_store=instance, image=doc)
            return instance


class StoreGetSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()
    business_logo = serializers.SerializerMethodField()
    account_officer = serializers.SerializerMethodField()
    license_document = serializers.SerializerMethodField()

    def get_license_document(self, obj):
        if obj.license_document:
            return f"{settings.FRONTEND_SERVER_NAME}/{obj.license_document}"

    def get_account_officer(self, obj):
        try:
            officer = Account_Officer.objects.get(business_store=obj.id)
            return AccountOfficerSerializer(officer).data
        except Exception as e:
            print('*', e)
            return None

    def get_subcategory(self, obj):
        if obj.subcategory:
            return SubcategorySerializer(obj.subcategory, many=True).data
    
    def get_business_logo(self, obj):
        if obj.business_logo:
            return f"{settings.FRONTEND_SERVER_NAME}/{obj.business_logo}"

    class Meta:
        model = BusinessStore
        fields = [
                'id',
                'user',
                'category',
                'subcategory',
                'account_officer',
                'country',
                'currency',
                'city',
                'slug',
                'name',
                'unique_name',
                'description',
                'phone',
                'status',
                'web_url',
                'is_deleted',
                'deal_price',
                'commission',
                'pin_code',
                'verification_status',
                'business_logo',
                'store_address',
                'average_rate',
                'store_status',
                'billing_reccurence',
                'lat',
                'lon',
                'license_id',
                'total_order',
                'license_document',
                'is_account_officer',
                'created_at',
                'updated_at'
        ]


class StoreSerializerTemplate(serializers.ModelSerializer):
    class Meta:
        model = BusinessStore
        fields = ['id', 'category', 'country', 'city', 'name', 'subcategory', 'store_address', 'store_status','business_logo', 'phone']


class StoreMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreMedia
        fields = ['image']


class SubCategoryViewSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    web_image = serializers.SerializerMethodField()

    # deal_no = serializers.SerializerMethodField()
    def get_image(self, obj):
        if obj.image:
            return f"{os.getenv('FRONTEND_SERVER_NAME_s3')}{obj.image.url}"

    def get_web_image(self, obj):
        if obj.image:
            return f"{obj.image.url}"

    class Meta:
        model = SubCategory
        fields = ["id", "image", "name", "slug", "status", "is_deleted", "category", 'web_image']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['deal_no'] = BusinessDeal.objects.filter(sub_category=instance.id)
        data['deal_no'] = len(data['deal_no'])
        return data

class GetStoreSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    business_logo = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            return GetStoreLocationSerializer(obj.location, many=True).data
        except Exception as err:
            print('STORE location', err)

    def get_business_logo(self, obj):
        if obj.business_logo:
            return f"{settings.FRONTEND_SERVER_NAME}/{obj.business_logo}"
    
    
    def get_subcategory(self, obj):
        try:
            #data = obj.subcategory.all()
            return SubCategoryViewSerializer(obj.location, many =True).data
        
        except Exception as err:
            print(err)
            
    
    def get_country(self, obj):
        return obj.country.name
    
    def get_city(self, obj):
        return obj.city.name
    
    def get_category(self, obj):
        return obj.category.name

    def get_media(self, obj):
        try:
            media = StoreMedia.objects.filter(business_store=obj).image
            return f"{settings.S3_BUCKET_LINK}{media}"
        except:
            return None

    class Meta:
        model = BusinessStore
        fields = [
            'id', 'user', 'category', 'country', 'city','currency', 'name', 'description', 'status', 'media', 'web_url', 'store_address',
            'slug', 'location',
            'deal_price', 'commission', 'pin_code', 'average_rate', 'billing_reccurence', 'created_at', 'updated_at' , 'subcategory', 'business_logo',
        ]


class DealMediaSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            file_url = obj.image
            return f"{settings.S3_BUCKET_LINK}{file_url}"
        else:
            return None

    class Meta:
        model = DealMedia
        fields = ['id', 'image', 'video']


class DealSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField(read_only = True)

    def get_location(self, obj):
        try:
            loc = obj.location.all()
            return StoreLocationSerializer(loc , many =True).data
        except Exception as err:
            print(err)
    class Meta:
        model = BusinessDeal
        fields = [
                    'id',
                    'location',
                    'create_by',
                    'store',
                    'category',
                    'sub_category',
                    'sub_sub_category',
                    'country',
                    'currency',
                    'city',
                    'term_id',
                    'title',
                    'unique_title',
                    'slug',
                    'description',
                    'condition',
                    'price',
                    'discount_price',
                    'discount_percentage',
                    'quantity',
                    'delivery_charges',
                    'gender',
                    'deal_status',
                    'status',
                    'view_count',
                    'phone',
                    'lat',
                    'lon',
                    'longitude',
                    'latitude',
                    'start_time',
                    'end_time',
                    'start_date',
                    'end_date',
                    'is_expired',
                    'is_featured',
                    'is_deleted',
                    'created_at',
                    'updated_at',
        ]
class DealDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifferentDealData
        fields = '__all__'
class Sub_categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id']


class GetDealSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    dealdata = serializers.SerializerMethodField()
    video = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    
    def get_store(self, obj):
        try:
            busines_store = BusinessStore.objects.get(name = obj.store)
            return GetStoreSerializer(busines_store).data
        except Exception as err:
            print(err)
    
    def get_video(self, obj):
        try:
            media = DealMedia.objects.get(business_deal=obj, image="")           
            serializer = DealMediaSerializer(media).data
            return serializer
        except Exception as err:
            print(err)
            
    def get_category(self, obj):
        try:
            media = Category.objects.get(name = obj.category  )
            return media.name
        except Exception as err:
            print(err)
    
    def get_dealdata(self, obj):
        try:
            deal = DifferentDealData.objects.filter(deal=obj)
            serializer = DealDataSerializer(deal, many=True).data
            return serializer
        except Exception as err:
            print('STORE location', err)
    
    
    def get_images(self, obj):
        try:
            media = DealMedia.objects.filter(business_deal=obj).exclude(image="")
            serializer = DealMediaSerializer(media, many=True).data
            return serializer
        except Exception as err:
            print(err)
        

    def get_location(self, obj):
        try:
            #data = obj.location.all()
            return StoreLocationSerializer(data, many=True).data
        except Exception as err:
            print('STORE location', err)
    
    class Meta:
        model = BusinessDeal
        fields = ['id','gender','create_by', 'store', 'location' , 'title', 'slug', 'description',
                  'condition', 'price', 'gender', 'deal_status', 'status', 'start_time', 'end_time'
                  , 'start_date', 'is_expired', 'created_at', 'dealdata' , 'images' ,'video', 'category' #, 'sub_category' , 'category'
                  ,'store'
                  ]

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     data['store'] = BusinessStore.objects.filter(id=instance.store.id).values("id", "name", "store_address",
    #                     logo=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("business_logo"),output_field=CharField()))[0]

    #     data['media'] = DealMedia.objects.filter(business_deal=instance.id)
    #     if data['media']:
    #         data['media'] = DealMedia.objects.filter(business_deal=instance.id).values("id", "business_deal", "order",
    #                         img=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("image"),output_field=CharField()),
    #                             teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("video"),output_field=CharField()))
    #     # else:
    #     #     data['media'] = []

    #     data['options'] = DifferentDealData.objects.filter(deal=instance.id).values("id", "title", "description",
    #                                                                  "price", "discount_percentage", "quantity")

    #     data['category'] = Category.objects.filter(id=instance.category_id)
    #     if data['category']:
    #         data['category'] = Category.objects.filter(id=instance.category_id).values()[0]['name']

    #     data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id)
    #     if data['sub_category']:
    #         data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id).values('name')[0]['name']
    #     return data


class StoreRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreRating
        fields = ['business_store', 'user', 'review', 'rate', 'created_at']


class BannerViewSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return f"{os.getenv('FRONTEND_SERVER_NAME_s3')}{obj.image.url}"

    class Meta:
        model = BannerMedia
        fields = "__all__"

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['banner'] = Banner.objects.filter(id=instance.banner.id).values()
    #     return data
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['image'] = BannerMedia.objects.filter(id=instance.id).values(img=Concat(Value(os.getenv('FRONTEND_SERVER_NAME_s3')), F("image"), output_field=CharField()))[0]
    #     return data


class CategoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['category'] = Category.objects.filter(id=instance.banner.id).values('id')
    #     return data



class UserProfileViewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "name", "email", "city", "country", "first_name", "last_name", "business_approved",
                  "phone", 'dial_code', "business_address", "gender"]  # "language", "currency"
        # exclude = ('password',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.city_id:
            data['city'] = City.objects.filter(id=instance.city_id).first().name
        if instance.country_id:
            data['country'] = Country.objects.filter(id=instance.country_id).first().name
        # if instance.currency_id:
        #     data['currency'] = Currency.objects.filter(id=instance.currency_id).first().name
        return data


class BusinessUserProfileViewSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True, required=False)
    logo = serializers.SerializerMethodField()

    def get_logo(self, obj):
        if obj.logo:
            file_url = obj.logo
            # return f"{settings.S3_BUCKET_LINK}{file_url}"
            return (str(os.getenv('S3_BUCKET_LINK')) + str(file_url))
        else:
            return None

    class Meta:
        model = User
        fields = ["id", "name", "email", "city", "logo", "country", "first_name", "last_name", "phone", "dial_code",
                  "business_address", "gender", "business_status"]
        # exclude = ('password',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.city_id:
            data['city'] = City.objects.filter(id=instance.city_id).first().name
        if instance.country_id:
            data['country'] = Country.objects.filter(id=instance.country_id).first().name
        return data


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    # confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):

        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        # confirm_password = attrs.get('confirm_password')

        user = self.context.get('user')
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password does't match.")

        # if new_password != confirm_password:
        #     raise serializers.ValidationError("Password and confirm password does't match")
        user.set_password(new_password)
        user.save()

        return attrs


class BusinessDealViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDeal
        fields = ["id", "store", "category", "sub_category", "term_id", "title", "slug", "description", "price",
                  "quantity", "gender", "status", "view_count", "start_date", "end_date", "is_expired", "is_deleted",
                  "created_at", "updated_at"]

class StoreSerializerForMap(serializers.ModelSerializer):
    business_logo = serializers.SerializerMethodField()

    def get_business_logo(self, obj):
        if obj.business_logo:
            return f"{settings.FRONTEND_SERVER_NAME}/{obj.business_logo}"
        
    class Meta:
        model = BusinessStore
        fields = ['name', 'store_address','business_logo']
 
class NearByDealSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    
    def get_images(self, obj):
        try:
            media = DealMedia.objects.filter(business_deal=obj, video ="").first()
            serializer = DealMediaSerializer(media).data
            return serializer
        except Exception as err:
            print(err)
    
    def get_store(self, obj):
        try:
            busines_store = BusinessStore.objects.get(name = obj.store)
            return StoreSerializerForMap(busines_store).data
        except Exception as err:
            print(err)
    class Meta:
        model = BusinessDeal
        fields = ['title', 'slug', 'images' ,'longitude', 'latitude', 'discount_percentage', 'category', 'store']

class HomeDealSerializer(serializers.ModelSerializer):
    """this serializers is used for home page and also for search result"""
    store = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    def get_location(self, obj):
        try:
            
            return GetStoreLocationSerializer(obj.location, many=True).data
        except Exception as err:
            print('STORE location', err)
    
    
    def get_store(self, obj):
        try:
            busines_store = BusinessStore.objects.get(name = obj.store)
            return GetStoreSerializer(busines_store).data
        except Exception as err:
            print(err)
    class Meta:
        model = BusinessDeal
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['media'] = DealMedia.objects.filter(business_deal=instance.id)
        if data['media']:
            data['media'] = data['media'].values("id", "business_deal", "order",img=Concat(Value(os.getenv('S3_BUCKET_LINK')),
                                         F("image"),output_field=CharField()),teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),
                                         F("video"),output_field=CharField()))

        data['video'] = []
        if data['media']:
            for v in data['media']:
                try:
                    if '/Video/' in v['teaser']:
                        data['video'].append(v['teaser'])
                except Exception as e:
                    pass

        if len(data['video']) == 0:
            data['video'] = ''
        else:
            data['video'] = data['video'][0]

        # data['store'] = BusinessStore.objects.filter(id=instance.store.id)
        # if data['store']:
        #     data['store'] = data['store'].values("id", "name", "store_address","category",
        #                                          "subcategory", "country", "city"
        #                                          ,logo=Concat(Value(
        #                                   os.getenv('S3_BUCKET_LINK')),F("business_logo"),output_field=CharField()))[0]

        data['options'] = DifferentDealData.objects.filter(deal=instance.id, is_delete=False)
        if data['options']:
            data['options'] = data['options'].order_by('-discount_percentage').values()
            data['highest_discount'] = data['options'][0]['discount_percentage']

        data['category'] = Category.objects.filter(id=instance.category_id)
        if data['category']:
            data['category'] = data['category'].values()[0]['name']
        else:
            data['category'] = ''

        data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id)
        if data['sub_category']:
            data['sub_category'] = data['sub_category'].values('name')[0]['name']
        else:
            data['sub_category'] = ''
        # data['category'] = Category.objects.filter(id=instance.category_id).values()[0]['name']
        # data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id).values('name')[0]['name']
        data['rating'] = DealRating.objects.filter(business_deal=instance.id)
        if data['rating']:
            data['rating_count'] = len(data['rating'])
            sum = 0
            for i in data['rating']:
                sum = sum + i.rate
            data['rating'] = str(sum / data['rating_count'])
        else:
            data['rating'] = str(0)
            data['rating_count'] = 0
        return data


class SingleDealSerializer(serializers.ModelSerializer):
    """this serializers is used for home page and also for search result"""

    class Meta:
        model = BusinessDeal
        fields =  ['id','gender','create_by', 'store', 'location' , 'title', 'slug', 'description',
                  'condition', 'price', 'gender', 'deal_status', 'status', 'start_time', 'end_time'
                  , 'start_date', 'is_expired', 'created_at', 'dealdata' , 'images' ,'video', 'category' #, 'sub_category' , 'category'
                  ,'store'
                  ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['media'] = DealMedia.objects.filter(business_deal=instance.id).values("id", "business_deal", "order",
                              img=Concat(Value(os.getenv('S3_BUCKET_LINK')), F("image"),output_field=CharField()),
                              teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("video"),output_field=CharField()))

        data['video'] = []
        if data['media']:
            for v in data['media']:
                try:
                    if '/Video/' in v['teaser']:
                        data['video'].append(v['teaser'])
                except Exception as e:
                    pass

        if len(data['video']) == 0:
            data['video'] = ''
        else:
            data['video'] = data['video'][0]

        data['create_by'] = User.objects.filter(id=instance.create_by.id).values('id', 'name', 'phone', 'dial_code')

        data['store'] = BusinessStore.objects.filter(id=instance.store.id).values("id", "name", "store_address",
                                      'user', 'category', 'subcategory','country', 'city', 'currency',
                                      'web_url', 'pin_code','store_status', 'lat', 'lon',
                                      'license_id', 'license_document','created_at', 'updated_at',
                                      logo=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("business_logo"),output_field=CharField()))[0]

        data['options'] = DifferentDealData.objects.filter(deal=instance.id, is_delete=False).values()

        data['deal_rating'] = DealRating.objects.filter(business_deal=instance.id)
        if data['deal_rating']:
            data['deal_rating_count'] = len(data['deal_rating'])
            sum = 0
            for i in data['deal_rating']:
                sum = sum + i.rate
            data['deal_rating'] = str(sum / data['deal_rating_count'])
        else:
            data['deal_rating'] = str(0)
            data['deal_rating_count'] = 0
        return data


class TestDealSerializer(serializers.ModelSerializer):
    """this serializers is used for home page and also for search result"""

    class Meta:
        model = BusinessDeal
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['media'] = DealMedia.objects.filter(business_deal=instance.id).values("id", "business_deal", "order",
                               img=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("image"),output_field=CharField()),
                               teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("video"),output_field=CharField()))

        data['store'] = BusinessStore.objects.filter(id=instance.store.id).values("id", "name", "store_address",
                               logo=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("business_logo"),output_field=CharField()))[0]

        data['rating'] = DealRating.objects.filter(business_deal=instance.id)
        if data['rating']:
            data['rating_count'] = len(data['rating'])
            sum = 0
            for i in data['rating']:
                sum = sum + i.rate
            data['rating'] = str(sum / data['rating_count'])
        else:
            data['rating'] = str(0)
            data['rating_count'] = 0

        data['category'] = Category.objects.filter(id=instance.category_id)
        if data['category']:
            data['category'] = Category.objects.filter(id=instance.category_id).values()[0]['name']

        data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id)
        if data['sub_category']:
            data['sub_category'] = SubCategory.objects.filter(id=instance.sub_category_id).values('name')[0]['name']

        return data


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"


class OrderPlacedViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPlaced
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['deal'] = BusinessDeal.objects.filter(id=instance.deal.id).first().title
        data['user'] = User.objects.filter(id=instance.user.id).values('name', 'first_name', 'last_name', 'logo')[0]
        # data['rate'] = str(instance.rate)
        data['media'] = DealMedia.objects.filter(business_deal=instance.deal.id).values("id", "business_deal",
                                     img=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("image"),output_field=CharField()),
                                     teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("video"),output_field=CharField()))

        data['discount_price'] = (instance.discount_price * instance.quantity) + instance.delivery_charges
        return data


class Recent_Reviews_Serializer(serializers.ModelSerializer):
    class Meta:
        model = DealRating
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = User.objects.filter(id=instance.user.id).values('name', 'first_name', 'last_name', 'logo')[0]
        data['rate'] = str(instance.rate)
        data['media'] = DealMedia.objects.filter(business_deal=instance.business_deal.id).values("id", "business_deal",
                                    img=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("image"),output_field=CharField()),
                                    teaser=Concat(Value(os.getenv('S3_BUCKET_LINK')),F("video"),output_field=CharField()))
        return data


class UserOrdersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPlaced
        fields = ['id', 'deal', 'store', 'user', 'status', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['deal'] = BusinessDeal.objects.filter(id=instance.deal.id).first().title
        data['deal_img'] = DealMedia.objects.values(
            logo=Concat(Value(os.getenv('S3_BUCKET_LINK')), F("image"), output_field=CharField()))[0]['logo']
        data['store'] = BusinessStore.objects.filter(id=instance.store.id).first().name
        data['user'] = User.objects.filter(id=instance.user.id).values('name', 'first_name', 'last_name', 'username')[0]
        data['price'] = (instance.discount_price * instance.quantity) + instance.delivery_charges
        return data


class UpdateOptionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifferentDealData
        fields = '__all__'

class MultipleDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifferentDealData
        fields = ['title','description','price','quantity','discount_percentage']

class BannerViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # data['status'] = Banner.objects.values('status')[0]
        data['img'] = BannerMedia.objects.filter(banner=instance.id).values(
                            logo=Concat(Value(os.getenv('S3_BUCKET_LINK')), F("image"), output_field=CharField()))[0]['logo']
        data['image'] = '/media/'+ BannerMedia.objects.filter(banner=instance.id).values('image')[0]['image']
        return data


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"

class TemplateStoreLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreLocation
        fields = '__all__'
