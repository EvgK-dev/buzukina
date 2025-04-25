from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.urls import reverse
from django.views import View

from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config
import aiohttp

from .models import (
    TitleImage, Houses, AdditionalService, Review,
    Document, ReservedDates, HousePhotos
)
from django.db.models import Prefetch

telegram_bot_token = config('TELEGRAM_BOT_TOKEN')
telegram_group_chat_id = config('TELEGRAM_GROUP_CHAT_ID')


def get_base_context():
    base = reverse('main_page')
    return {
        'main': base,
        'services_list': f"{base}#services_list",
        'houses_list': f"{base}#houses",
        'booking': reverse('booking'),
        'feedback': f"{base}#feedback",
    }


def index(request):
    title_image = TitleImage.objects.first()
    houses = Houses.objects.prefetch_related(
        Prefetch('housephotos_set', queryset=HousePhotos.objects.all())
    )
    additional_services = AdditionalService.objects.all()
    reviews = Review.objects.all()

    for house in houses:
        house.photos_preview = house.housephotos_set.all()[:7]

    context = {
        **get_base_context(),
        'title': 'БузукИнА - агроусадьба со всеми удобствами',
        'title_image': title_image,
        'houses': houses,
        'additional_services': additional_services,
        'reviews': reviews,
        'document': Document.objects.first(),
    }
    return render(request, 'main/index.html', context)


def booking(request):
    houses = Houses.objects.prefetch_related(
        Prefetch('housephotos_set', queryset=HousePhotos.objects.all())
    )
    today = datetime.today()
    current_month = today.replace(day=1)
    two_months_later = (today + timedelta(days=60)).replace(day=1)
    reserved_dates = ReservedDates.objects.filter(
        house__in=houses,
        date__gte=current_month,
        date__lt=two_months_later + timedelta(days=31)
    )

    for house in houses:
        house.photos_preview = house.housephotos_set.all()[:7]

    context = {
        **get_base_context(),
        'title': 'агроусадьба "БузукИнА" - бронирование',
        'houses': houses,
        'reserved_dates': reserved_dates,
    }
    return render(request, 'main/booking.html', context)


def politic(request):
    context = {
        **get_base_context(),
        'title': 'агроусадьба "БузукИнА" - политика конфиденциальности',
    }
    return render(request, 'main/politic.html', context)


def mail_done(request):
    name = request.GET.get('name')
    phone = request.GET.get('phone')
    context = {
        **get_base_context(),
        'title': 'агроусадьба "БузукИнА" - обратная связь',
        'form_data': {'name': name, 'phone': phone},
    }
    return render(request, 'main/mail_done.html', context)


async def send_telegram_message(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    name = request.POST.get('name')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    comment = request.POST.get('comment')

    bot = Bot(token=telegram_bot_token)
    message = (
        f"ПИСЬМО!\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Email: {email}\n"
        f"Комментарий: {comment}"
    )
    await bot.send_message(chat_id=telegram_group_chat_id, text=message)

    query = urlencode({'name': name, 'phone': phone})
    return redirect(f"{reverse('mail_done')}?{query}")


class SubmitBookingView(APIView):
    @async_to_sync
    async def post(self, request, *args, **kwargs):
        form = request.POST

        house_name = form.get('house_name')
        check_in = datetime.strptime(form.get('check_in'), "%Y-%m-%d")
        check_out = datetime.strptime(form.get('check_out'), "%Y-%m-%d")
        selected_days = form.get('selected_days')
        prepayment = form.get('prepayment')
        user_name = form.get('user_name')
        phone_number = form.get('phone_number')
        comment = form.get('comment')

        message = (
            f"ЗАКАЗ!\n\n"
            f"ДОМ: {house_name}\n\n"
            f"ЗАЕЗД: {check_in.strftime('%d-%m-%Y')}\n"
            f"ВЫЕЗД: {check_out.strftime('%d-%m-%Y')}\n"
            f"СУТОК: {selected_days}\n"
            f"МИН.ПРЕДОПЛАТА: {prepayment}\n\n"
            f"ИМЯ: {user_name}\n"
            f"НОМЕР: {phone_number}\n\n"
            f"КОММЕНТАРИЙ: {comment}"
        )

        keyboard = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel")],
            [InlineKeyboardButton("✏️ Изменить", callback_data="change")]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        bot = Bot(token=telegram_bot_token)
        await bot.send_message(chat_id=telegram_group_chat_id, text=message, reply_markup=markup)

        file = request.FILES.get('fileAttachment')
        if file:
            async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('document', file.read(), filename=file.name)
                url = f'https://api.telegram.org/bot{telegram_bot_token}/sendDocument?chat_id={telegram_group_chat_id}'

                async with session.post(url, data=data) as resp:
                    if resp.status != 200:
                        return HttpResponseBadRequest("Ошибка при отправке файла")

        query = urlencode({'name': user_name, 'phone': phone_number})
        return redirect(f"{reverse('mail_done')}?{query}")


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
