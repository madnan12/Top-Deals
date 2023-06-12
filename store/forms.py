from django import forms
from django.forms import ModelForm
from django.contrib.auth import authenticate
from store.models import *
from django.forms import inlineformset_factory,modelformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML

from django import forms
from captcha.fields import ReCaptchaField

class NormalUserForm(forms.ModelForm):
    name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your business name', 'autocomplete':'off'}))

    email = forms.CharField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder':'Enter your email address', 'autocomplete':'off'}))

    phone = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'minlength':"8",'maxlength':"12",'class':'pl-2 outline-none w-[4ch] text-sm w-full flex-1','placeholder':'enter username', 'placeholder':'Enter your phone number', 'required':'true','type':'number', 'autocomplete':'off'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength':"8",'class':'border password-show rounded-md text-sm outline-none px-4 py-3 placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]','placeholder':'Enter password', 'autocomplete':'off', 'aria-describedby':'password-addon'}))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength':"8",'class':'border password-show rounded-md text-sm outline-none px-4 py-3 placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'placeholder':'Enter confirm password', 'autocomplete':'off'}))
    
    business_address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your business address', 'autocomplete':'off'}))
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password', 'username' , 'business_address']


    def clean_name(self, *args, **kwargs):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Full name is required for Signup!")
        return name

    def clean_email(self, *args, **kwargs):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required for Signup!")
        return email


    def clean_phone(self, *args, **kwargs):
        phone = self.cleaned_data.get('phone')
        if not phone:
                raise forms.ValidationError("Phone is required for Signup!")
        return phone 

    def clean_password(self, *args, **kwargs):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Password is required for Signup!")
        return password

    def clean_confirm_password(self, *args, **kwargs):
        confirm_password = self.cleaned_data.get('confirm_password')
        if not confirm_password:
            raise forms.ValidationError("Confirm Password is required for Signup!")
        return confirm_password

    def clean_match_password(self, *args, **kwargs):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if confirm_password != password:
            raise forms.ValidationError("Password and Confirm Password not Match!")
        return password

    def raise_duplicate_email_error(self):
        # here I tried to override the method, but it is not called
        raise forms.ValidationError(
            _("An account already exists with this e-mail address."
              " Please sign in to that account."))



class BusinessUserForm(ModelForm):

    first_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your first name', 'autocomplete':'off'}))

    last_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your  lastname', 'autocomplete':'off'}))

    name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your name', 'autocomplete':'off'}))

    email = forms.CharField(max_length=255, required=True, widget=forms.EmailInput(attrs={'id':'email_validation_','class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent email_validation','placeholder':'Enter your email address', 'autocomplete':'off'}))

    phone = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'minlength':"8",'maxlength':"12",'class':'pl-2 outline-none w-[4ch] text-sm w-full flex-1','placeholder':'enter username', 'placeholder':'Enter your phone number', 'required':'true', 'autocomplete':'off','type':'number'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength':"8",'id':'password','class':'border password-show rounded-md text-sm outline-none px-4 py-3 placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]','placeholder':'Enter password', 'autocomplete':'off', 'aria-describedby':'password-addon',"minlength":"8"}))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'minlength':"8",'id':'confirm_password','class':'border password-show rounded-md text-sm outline-none px-4 py-3 placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'placeholder':'Enter confirm password', 'autocomplete':'off',"minlength":"8"}))
    
    business_address = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your business address', 'autocomplete':'off'}))

    license_id = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your license number', 'autocomplete':'off'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'name', 'email', 'phone', 'password', 'country', 'business_address', 'category', 'license_id' , 'username']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].widget.attrs.update({'class':'id_country border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','id':'id_country', 'placeholder':'Enter your name', 'autocomplete':'off','required':'true'})
        self.fields['country'].queryset = Country.objects.all()
        # self.fields['country'].empty_label = Country.objects.get(id=229)

        self.fields['category'].widget.attrs.update({'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent', 'placeholder':'Enter your name', 'autocomplete':'off','required':'true'})
        self.fields['category'].queryset = Category.objects.filter(status='Active').all()
        self.fields['category'].empty_label = 'Select Category'
    
    def raise_duplicate_email_error(self):
        # here I tried to override the method, but it is not called
        raise forms.ValidationError(
            _("An account already exists with this e-mail address."
              " Please sign in to that account."))


class LoginForm(forms.Form):
    email = forms.CharField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class':'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder':'Enter your email address', 'autocomplete':'off'}))

    password = forms.CharField(required=True,widget=forms.PasswordInput(attrs={'minlength':"8",'class':'border password-show rounded-md text-sm outline-none px-4 py-3 placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]','placeholder':'Enter password', 'autocomplete':'off', 'aria-describedby':'password-addon'}))

    class Meta:
        model = User
        fields = ['email', 'password']

    def raise_duplicate_email_error(self):
        # here I tried to override the method, but it is not called
        raise forms.ValidationError(
            _("An account already exists with this e-mail address."
              " Please sign in to that account."))

    def clean(self):
        email = self.cleaned_data.get('eamil')
        password = self.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email, is_active=True).username
        except:
            raise forms.ValidationError("User is not found!")

        user = authenticate(username=user, password=password)
        if not user or not user.is_admin:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email, is_active=True).username
        except:
            raise forms.ValidationError("User is not found!")
        user = authenticate(username=user, password=password)
        return user


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Both', 'Both'),
    ('Other', 'Other')
)

STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    

class BusinessDealForm(ModelForm):
    title = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'new_title border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Enter Deal title', 'autocomplete': 'off'}))
    gender = forms.ChoiceField(choices = GENDER_CHOICES,required=False, widget=forms.Select(attrs={'class': 'new_gender border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Select Gender', 'autocomplete': 'off'}))
    deal_status = forms.ChoiceField(choices = STATUS_CHOICES,required=False,widget=forms.Select(attrs={'class': 'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Select Status', 'autocomplete': 'off'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'type':'text', 'placeholder':'Enter detail about the deal', 'rows':'5','class':'new_desc deal_description resize-none border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent'}))
    condition = forms.CharField(required=False, widget=forms.Textarea(attrs={'type':'text','id':'condition', 'placeholder':'Enter terms and conditions about the deal', 'rows':'5','class':'new_con deal_description resize-none border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent'}))
    phone = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'minlength':"8",'maxlength':"12",'class': 'new_phn px-4 py-3 border-l w-full outline-none text-sm','placeholder': 'Enter your phone number',  'autocomplete': 'off', 'type': 'number'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_date border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_da border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'date'}))
    
    start_time = forms.TimeField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_date border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'time'}))
    end_time = forms.TimeField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_da border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'time'}))
    class Meta:
        model = BusinessDeal
        fields = ['store','category','sub_category','country','city','title','gender','deal_status','status','description','condition','start_date','end_date','phone', 'start_time', 'end_time']

    def __init__(self,*args, **kwargs):
        super(BusinessDealForm, self).__init__(*args, **kwargs)

        self.fields['store'].widget.attrs.update({'class': 'border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['store'].queryset = BusinessStore.objects.all()
        self.fields['store'].empty_label = 'Select Store'

        self.fields['category'].widget.attrs.update({'class': 'new_category id_category border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['category'].queryset = Category.objects.filter(status='Active').all()
        self.fields['category'].empty_label = 'Select Category'

        self.fields['sub_category'].widget.attrs.update({'class': 'border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['sub_category'].queryset = SubCategory.objects.all()
        self.fields['sub_category'].empty_label = 'Select SubCategory'

        self.fields['country'].widget.attrs.update({'class': 'id_country new_country border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['country'].queryset = Country.objects.all()
        self.fields['country'].initial = Country.objects.get(id=229)

        self.fields['city'].widget.attrs.update({'class': 'cities_dropdown border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['city'].queryset = City.objects.all()
        self.fields['city'].empty_label = 'Select City'

    def clean_status(self, *args, **kwargs):
        status = self.cleaned_data.get('deal_status')
        if status == 'Active':
            status = True
        else:
            status = False
        return status



class DealMediaForm(ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'img_render_inp border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','type': 'file', 'autocomplete': 'off','accept':'image/*','hidden':'','id':'Upload'}))
    video = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'img_render_inp border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','type': 'file', 'accept':'video/*','hidden':'','id':'Upload_Video','for':'Upload_Video'}))
    class Meta:
        model = DealMedia
        fields = ['image','video']

    def __init__(self, *args, **kwargs):
        super(DealMediaForm, self).__init__(*args, **kwargs)
        self.fields['video'].required = False

class DifferentDealDataForm(ModelForm):
    class Meta:
        model = DifferentDealData
        fields = '__all__'
        exclude = ('deal',)


DifferentDealDataFormset = inlineformset_factory(BusinessDeal, DifferentDealData, fields=["title", "description","price","discount_percentage","quantity"], extra=1, can_delete=True)
Deals = modelformset_factory(BusinessDeal, exclude=(), extra=14)

# class UpdateDifferentDealDataForm(ModelForm):
#     class Meta:
#         model = DifferentDealData
#         fields = [
#                     'deal',
#                     'title',
#                     'description',
#                     'price',
#                     'discount_percentage',
#                     'quantity']


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Both', 'Both'),
    ('Other', 'Other')
)

STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
class UpdateBusinessDealForm(ModelForm):
    title = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'new_title border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Enter Deal title', 'autocomplete': 'off'}))
    gender = forms.ChoiceField(choices = GENDER_CHOICES,required=False, widget=forms.Select(attrs={'class': 'new_gender border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Select Gender', 'autocomplete': 'off'}))
    deal_status = forms.ChoiceField(choices = STATUS_CHOICES,required=False,widget=forms.Select(attrs={'class': 'border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent','placeholder': 'Select Status', 'autocomplete': 'off'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'type':'text', 'placeholder':'Enter detail about the deal', 'rows':'5','class':'new_desc deal_description resize-none border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent'}))
    condition = forms.CharField(required=False, widget=forms.Textarea(attrs={'type':'text', 'id':'condition','placeholder':'Enter terms and conditions about the deal', 'rows':'5','class':'new_con deal_description resize-none border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]  bg-transparent'}))
    phone = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'minlength':"8",'maxlength':"12",'class': 'new_phn px-4 py-3 border-l w-full outline-none text-sm','placeholder': 'Enter your phone number',  'autocomplete': 'off', 'type': 'number'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_date border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'date'}))

    start_time = forms.TimeField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_date border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'time'}))
    end_time = forms.TimeField(required=False, widget=forms.DateInput(attrs={'class': 'new_str_da border rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]', 'autocomplete': 'off', 'type': 'time'}))

    class Meta:
        model = BusinessDeal
        fields = ['category','sub_category','country','city', 'start_time', 'end_time', 'title','gender','deal_status','status','description','condition','start_date','end_date','phone']

    def __init__(self,*args, **kwargs):
        super(UpdateBusinessDealForm, self).__init__(*args, **kwargs)
        # self.fields['store'].widget.attrs.update({'class': 'border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        # self.fields['store'].queryset = BusinessStore.objects.all()
        # self.fields['store'].empty_label = 'Select Store'

        self.fields['category'].widget.attrs.update({'class': 'new_category id_category border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['category'].queryset = Category.objects.filter(status='Active').all()
        self.fields['category'].empty_label = 'Select Category'

        self.fields['sub_category'].widget.attrs.update({'class': 'border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['sub_category'].queryset = SubCategory.objects.all()
        self.fields['sub_category'].empty_label = 'Select SubCategory'

        self.fields['country'].widget.attrs.update({'class': 'id_country new_country border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['country'].queryset = Country.objects.all()
        self.fields['country'].initial = Country.objects.get(id=229)

        self.fields['city'].widget.attrs.update({'class': 'cities_dropdown border bg-transparent rounded-md text-sm outline-none lg:px-4 px-2 lg:py-3 py-[0.6rem] placeholder:text-[#A1A1A1] text-[#101928] focus:border-[#205a42] ease-in transition-all focus:border-l-[7px]'})
        self.fields['city'].queryset = City.objects.all()
        self.fields['city'].empty_label = 'Select City'

    def clean_status(self, *args, **kwargs):
        status = self.cleaned_data.get('deal_status')
        if status == 'Active':
            status = True
        else:
            status = False
        return status



class FormWithCaptcha(forms.Form):
    captcha = ReCaptchaField()
