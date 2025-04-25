from django.urls import path
from .views import *

urlpatterns = [
    path('check_houses/', check_houses, name='check_houses'),
    path('get_reserved_dates/', get_reserved_dates, name='get_reserved_dates'),  

    path('confirm/', confirm, name='confirm'),
    path('cancel/', cancel, name='cancel'),
]