from django.db import models

from django.utils.html import format_html
# Create your models here.

# изображение заглавное
class TitleImage(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='title_images/')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Главная картинка"
        verbose_name_plural = "Главная картинка"
    
# дома

class Houses(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название дома")
    capacity = models.CharField(max_length=255, verbose_name="Вместимость")
    floors = models.PositiveIntegerField(verbose_name="Этажи")
    rooms = models.PositiveIntegerField(verbose_name="Комнаты")
    kitchen = models.PositiveIntegerField(verbose_name="Кухня")
    toilet = models.PositiveIntegerField(verbose_name="Туалет")
    hot_water = models.CharField(max_length=255, verbose_name="Горячая вода")
    air_conditioner = models.CharField(max_length=255, verbose_name="Кондиционер")
    fireplace = models.CharField(max_length=255, verbose_name="Камин")
    wifi = models.CharField(max_length=255, verbose_name="Wi-Fi")
    appliances = models.CharField(max_length=255, verbose_name="Бытовая техника")
    additional_info = models.TextField(verbose_name="Дополнительная информация")
    weekday_price = models.CharField(max_length=255, verbose_name="Стоимость будние")
    weekend_price = models.CharField(max_length=255, verbose_name="Стоимость выходные")
    children = models.CharField(max_length=255, verbose_name="Дети")
    max_people = models.CharField(max_length=255, verbose_name="Максимальное количество человек")
    group_size = models.CharField(max_length=255, verbose_name="Компания человек")
    pets = models.CharField(max_length=255, verbose_name="Животные")
    check_in = models.CharField(max_length=255, verbose_name="Заезд")
    check_out = models.CharField(max_length=255, verbose_name="Выезд")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "1. КОТТЕДЖИ"
        verbose_name_plural = "1. КОТТЕДЖИ"

# фото домов
class HousePhotos(models.Model):
    house = models.ForeignKey(Houses, on_delete=models.CASCADE, related_name="photos", verbose_name="Дом")
    photo = models.ImageField(upload_to='house_photos/', verbose_name="Фотография")

    def __str__(self):
        return f"Фото для дома {self.house.name}"

    def __str__(self):
        return f"Фото для дома {self.house.name}"

    def image_tag(self):
        return format_html('<img src="{}" width="100" height="100" />'.format(self.photo.url))

    image_tag.short_description = 'Предпросмотр'

    class Meta:
        verbose_name = "3. Фотография дома"
        verbose_name_plural = "3. Фотографии домов"

# забронированные даты

class ReservedDates(models.Model):
    house = models.ForeignKey(Houses, on_delete=models.CASCADE, related_name='reserved_dates', verbose_name="Дом")
    date = models.DateField(verbose_name="Дата бронирования")
    person = models.CharField(max_length=255, verbose_name="Лицо")
    contact = models.CharField(max_length=255, verbose_name="Контакт")
    num_people = models.CharField(max_length=255, verbose_name="Количество человек")
    total_amount = models.CharField(max_length=255, verbose_name="Сумма")
    additional_services = models.TextField(blank=True, verbose_name="Дополнительные услуги")

    def __str__(self):
        return f"{self.house.name} - {self.date}"

    class Meta:
        verbose_name = "2. БРОНИРОВАНИЕ"
        verbose_name_plural = "2. БРОНИРОВАНИЕ"
        unique_together = ['house', 'date']


# дополнительные услуги

class AdditionalService(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    capacity = models.CharField(max_length=255, blank=True, null=True, verbose_name="Количество человек")
    duration = models.CharField(max_length=255, blank=True, null=True, verbose_name="Длительность")
    cost = models.CharField(max_length=255, verbose_name="Стоимость")
    image = models.ImageField(upload_to='additional_service_images/', verbose_name="Изображение")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"


# отзывы
from django.db import models

class Review(models.Model):
    photo = models.ImageField(upload_to='review_photos/', verbose_name="Фотография")
    name = models.CharField(max_length=255, verbose_name="Имя")
    feedback = models.TextField(verbose_name="Отзыв")
    source_choices = [('yandex', 'Yandex'), ('google', 'Google')]
    source = models.CharField(max_length=10, choices=source_choices, verbose_name="Источник")

    def __str__(self):
        return f"{self.name} - {self.source}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


# публичный договор

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Загрузить договор"
        verbose_name_plural = "Загрузить договор"