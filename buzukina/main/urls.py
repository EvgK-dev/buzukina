from django.urls import path
 
from .views import *

urlpatterns = [
    path('', index, name='main_page'), 
    path('booking', booking, name='booking'), 
    path('politic', politic, name='politic'), 
    path('mail_done/', mail_done, name='mail_done'),
    path('send-telegram-message/', send_telegram_message, name='send_telegram_message'), 
    path('submit_booking/', SubmitBookingView.as_view(), name='submit_booking'),
]