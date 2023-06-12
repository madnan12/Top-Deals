from atexit import register
from django.contrib import admin
from store.models import *


class MediaDealInline(admin.TabularInline):
    model = DealMedia
    extra = 2
    
admin.site.register(DifferentDealData)
admin.site.register(OrderItem)
admin.site.register(OrderCardCheckout)
admin.site.register(ExceptionRecord)
admin.site.register(RandomFiles)
admin.site.register(DealMedia)
admin.site.register(Faq)
admin.site.register(DealLocation)

class DifferentDealInline(admin.TabularInline):
    model = DifferentDealData
    extra = 1
@admin.register(BusinessDeal)
class BusinessDealInlineAdmin(admin.ModelAdmin):
    inlines = [
        DifferentDealInline, MediaDealInline
    ]

class BannerMediaInline(admin.TabularInline):
    model = BannerMedia
    extra = 1
@admin.register(Banner)
class BusinessDealInlineAdmin(admin.ModelAdmin):
    inlines = [
       BannerMediaInline
    ]
    # def has_add_permission(self, request):
    #     return False



# Location
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Currency)

# User
admin.site.register(User)
admin.site.register(UserReminder)
admin.site.register(UserKpi)
admin.site.register(UserWallet)
admin.site.register(DeleteAccountRequest)
admin.site.register(UserAccountHistory)
admin.site.register(Account_Officer)

# category
admin.site.register(SubCategory)
admin.site.register(SubSubCategory)
class SubCategoryInline(admin.TabularInline):
    model = SubCategory
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        SubCategoryInline
]


admin.site.register(VerificationCode)




admin.site.register(BusinessStore)
admin.site.register(StoreLocation)
admin.site.register(StoreKpi)
admin.site.register(StoreService)
admin.site.register(StoreMedia)
admin.site.register(StoreOpening)
admin.site.register(StoreLicense)
admin.site.register(StoreRating)


admin.site.register(Ticket)
admin.site.register(TicketHistory)
admin.site.register(DealAvailability)
admin.site.register(DealImpression)
admin.site.register(DealClick)
admin.site.register(DealDiscount)
admin.site.register(PromotedDeal)
admin.site.register(DealRating)
admin.site.register(Transaction)
admin.site.register(TransactionAttchment)
admin.site.register(TransactionHistory)
admin.site.register(CommissionIncoice)
admin.site.register(State)

admin.site.register(CartItem)
admin.site.register(OrderPlaced)
admin.site.register(WebDynamicContent)

admin.site.register(NewsLetter)