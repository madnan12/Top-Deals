import django_filters
from django_filters import *
from .models import *
from django import forms


class BusinessDealFilter(django_filters.FilterSet):
    country = ModelChoiceFilter(queryset=Country.objects.all(), empty_label='Select', widget=forms.Select(attrs={'class': 'py-2 px-2  rounded-lg form-control border border-secondary'}))
    city = ModelChoiceFilter(queryset=City.objects.all(), empty_label='Select', widget=forms.Select(attrs={'class': 'py-2 px-2  rounded-lg form-control border border-secondary'}))
    class Meta:
        model = BusinessDeal
        fields = ''