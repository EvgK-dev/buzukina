import logging
from datetime import timedelta, datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from main.models import Houses, ReservedDates
from decouple import config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Константы
DATE_FORMAT = config("DATE_FORMAT", default="%d-%m-%Y")
ERROR_MESSAGES = {
    "no_start_date": "⚠️ Дата начала бронирования не указана.",
    "invalid_date": "⚠️ Неверный формат даты. Используйте формат DD-MM-YYYY.",
    "house_not_found": "⚠️ Указанный дом не найден.",
    "dates_reserved": "⚠️ Следующие даты уже забронированы:\n{}",
    "no_houses": "Коттеджи не найдены",
    "missing_params": "Отсутствуют обязательные параметры",
    "invalid_period": "Неверный период",
    "server_error": "Ошибка сервера: {}",
}
SUCCESS_MESSAGES = {
    "confirm": "✅ Бронирование подтверждено!",
    "cancel": "❌ Бронирование успешно отменено на даты: {}",
}
PERIOD_DAYS = {
    "week": 9,  # 9 дней для недели
    "month": 30,  # 30 дней для месяца
}




def get_house(house_name: str) -> Houses:
    """Получение дома по имени."""
    try:
        return Houses.objects.get(name=house_name)
    except Houses.DoesNotExist:
        logger.error(f"Дом не найден: {house_name}")
        raise ValueError(ERROR_MESSAGES["house_not_found"])


def parse_start_date(startdate_str: str) -> datetime.date:
    """Парсинг строки даты в объект date."""
    if not startdate_str:
        raise ValueError(ERROR_MESSAGES["no_start_date"])
    try:
        return datetime.strptime(startdate_str, DATE_FORMAT).date()
    except ValueError:
        logger.error(f"Неверный формат даты: {startdate_str}")
        raise ValueError(ERROR_MESSAGES["invalid_date"])


@api_view(["POST"])
def confirm(request):
    """Подтверждение бронирования."""
    booking_data = request.data
    house_name = booking_data.get("house")
    startdate_str = booking_data.get("startdate")
    day = int(booking_data.get("day", 1))
    person = booking_data.get("person")
    contact = booking_data.get("contact")
    additional_services = booking_data.get("additional_services", "")
    admin_text = booking_data.get("admin_text", "")

    try:
        house = get_house(house_name)
        startdate = parse_start_date(startdate_str)
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Проверка доступности дат
    reserved_dates_info = []
    for i in range(day):
        booking_date = startdate + timedelta(days=i)
        reservation = ReservedDates.objects.filter(house=house, date=booking_date).first()
        if reservation:
            reserved_dates_info.append({
                "date": booking_date,
                "person": reservation.person,
                "contact": reservation.contact,
            })

    if reserved_dates_info:
        reserved_details = "\n".join(
            [f"{info['date']}: {info['person']} ({info['contact']})" for info in reserved_dates_info]
        )
        return Response(
            {"message": ERROR_MESSAGES["dates_reserved"].format(reserved_details)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Создание бронирований
    for i in range(day):
        booking_date = startdate + timedelta(days=i)
        final_additional_services = additional_services
        if admin_text:
            final_additional_services += f"// АДМИН: {admin_text}"
        ReservedDates.objects.create(
            house=house,
            date=booking_date,
            person=person,
            contact=contact,
            num_people="",
            total_amount="",
            additional_services=final_additional_services,
        )

    logger.info(f"Бронирование подтверждено: {house_name}, {startdate}, {day} дней")
    return Response({"message": SUCCESS_MESSAGES["confirm"]}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def cancel(request):
    """Отмена бронирования."""
    booking_data = request.data
    house_name = booking_data.get("house")
    startdate_str = booking_data.get("startdate")
    day = int(booking_data.get("day", 1))
    person = booking_data.get("person")
    contact = booking_data.get("contact")

    try:
        house = get_house(house_name)
        startdate = parse_start_date(startdate_str)
    except ValueError as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    deleted_dates = []
    not_booked_dates = []
    occupied_dates = []

    for i in range(day):
        booking_date = startdate + timedelta(days=i)
        reservation = ReservedDates.objects.filter(house=house, date=booking_date).first()
        if reservation:
            if reservation.person == person and reservation.contact == contact:
                reservation.delete()
                deleted_dates.append(booking_date)
            else:
                occupied_dates.append(booking_date)
        else:
            not_booked_dates.append(booking_date)

    message = ""
    if deleted_dates:
        message += SUCCESS_MESSAGES["cancel"].format(", ".join(map(str, deleted_dates)))
    if not_booked_dates:
        message += f"\n⚠️ Следующие даты не забронированы: {', '.join(map(str, not_booked_dates))}."
    if occupied_dates:
        message += f"\n🚫 Следующие даты заняты другими пользователями: {', '.join(map(str, occupied_dates))}."

    status_code = status.HTTP_200_OK if deleted_dates else status.HTTP_400_BAD_REQUEST
    logger.info(f"Отмена бронирования: {house_name}, {startdate}, {day} дней, успех: {bool(deleted_dates)}")
    return Response({"message": message.strip()}, status=status_code)

@api_view(["POST"])
def check_houses(request):
    """Получение списка домов."""
    houses = Houses.objects.all().values("id", "name")
    if not houses:
        logger.warning("Коттеджи не найдены")
        return Response({"message": ERROR_MESSAGES["no_houses"]}, status=status.HTTP_404_NOT_FOUND)
    return Response(list(houses), status=status.HTTP_200_OK)

@api_view(["POST"])
def get_reserved_dates(request):
    """Получение забронированных дат."""
    data = request.data
    house_id = data.get("house_id")
    period = data.get("period")

    if not house_id or not period:
        logger.error("Отсутствуют параметры: house_id или period")
        return Response({"message": ERROR_MESSAGES["missing_params"]}, status=status.HTTP_400_BAD_REQUEST)

    try:
        house = get_object_or_404(Houses, id=house_id)
        if period not in PERIOD_DAYS:
            logger.error(f"Неверный период: {period}")
            return Response({"message": ERROR_MESSAGES["invalid_period"]}, status=status.HTTP_400_BAD_REQUEST)

        current_date = timezone.now().date()
        start_date = current_date
        end_date = current_date + timedelta(days=PERIOD_DAYS[period])

        reserved_dates = ReservedDates.objects.filter(
            house=house, date__range=[start_date, end_date]
        ).order_by("date")

        result = [
            {
                "date": reservation.date.strftime("%Y-%m-%d"),
                "person": reservation.person,
                "contact": reservation.contact,
                "num_people": reservation.num_people,
                "total_amount": reservation.total_amount,
                "additional_services": reservation.additional_services,
            }
            for reservation in reserved_dates
        ]

        logger.info(f"Получены забронированные даты для дома {house.name}, период: {period}")
        return Response({"house_name": house.name, "reserved_dates": result}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Ошибка при получении дат: {str(e)}")
        return Response({"message": ERROR_MESSAGES["server_error"].format(str(e))}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)