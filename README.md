# Агроусадьба "БузукИнА" – Система бронирования коттеджей

**Buzukina** — веб-приложение, созданное на базе Django и Django REST Framework (DRF) для бронирования коттеджей, бань и дополнительных услуг в агроусадьбе "БузукИнА". 
Система включает веб-интерфейс для пользователей, API для управления бронированиями и Telegram-бот для обработки запросов администратором.

🌐 Сайт используется реальной организацией: [https://Buzukina.by](https://Buzukina.by)

## 🧰 Технологический стек
- **Бэкенд**: Python, Django, Django REST Framework
- **Фронтенд**: HTML, CSS, JavaScript (vanilla JS для календаря и динамических взаимодействий)
  - **Веб-интерфейс**: Позволяет пользователям просматривать доступные коттеджи, проверять занятость дат, бронировать дома, оплачивать услуги и оставлять отзывы.
- **База данных**: MySQL
- **Статические файлы**: Организованная структура для CSS, JS, изображений и шрифтов
- **Интеграции**: Telegram Bot API
  - Уведомляет администраторов о новых заказах, позволяет подтверждать, отменять или изменять бронирования, а также просматривать забронированные даты.
- **Безопасность**: CSRF-защита, валидация данных, безопасная обработка пользовательских запросов и иное
- **API**: Обеспечивает управление бронированиями, проверку доступности и отмену заказов.

## ⚙️ Основные особенности проекта и стек разработки

### 🔐 Безопасность и доступ
- Реализована защита от CSRF для форм бронирования и обратной связи.
- Валидация входных данных на стороне клиента и сервера (например, формат дат, корректность номеров телефонов).
- Ограничение операций бронирования и отмены только для авторизованных запросов через API и Telegram-бота.

### 📅 Управление бронированиями
- Интерактивный календарь с отображением занятых дат и расчётом стоимости.
- CRUD-операции для домов, бронирований и дополнительных услуг через Django ORM.
- RESTful API для подтверждения, отмены и проверки бронирований с использованием JSON.
- Интеграция с Telegram-ботом для уведомлений администраторов и управления заказами.

### 🌟 Интерфейс и UX
- Адаптивный дизайн с кастомной стилизацией (CSS) для десктопов и мобильных устройств.
- Интерактивный календарь бронирования на чистом JavaScript с проверкой доступности дат.
- Слайдер изображений домов и услуг для удобного просмотра.
- Интуитивная навигация с мобильным меню ("burger") и плавной прокруткой.

### 🏗️ Архитектура и организация кода
- Чёткое разделение логики: бэкенд (Django), фронтенд (HTML/CSS/JS), API (DRF), Telegram-бот.
- Оптимизированные запросы к базе данных с использованием Prefetch и select_related.
- Модульная структура: отдельные приложения `main` (веб-интерфейс), `api` (API) и `telegram_bot` (бот).
- Чистый и поддерживаемый код с логированием операций.

### 🔧 Функциональность и расширяемость
- **Telegram-бот для администраторов**: подтверждение/отмена бронирований, просмотр занятых дат за неделю/месяц.
- Поддержка загрузки файлов (например, чеков об оплате) через веб-форму и их отправка в Telegram.
- Возможность расширения: добавление новых домов, услуг, аналитики пользовательских бронирований.
- Алгоритмы проверки доступности дат и расчёта стоимости на основе цен за будни/выходные.

## 💼 Для работодателей

Этот проект я размещаю на GitHub как часть своего портфолио для работодателей.  
Беру на себя полный цикл разработки — от дизайна и клиентской части до серверной логики и деплоя.  
Если вам нужен такой специалист, буду рад обсудить сотрудничество.

## 🤝 Контакты
- Telegram: [@EvgenyKrup](https://t.me/EvgenyKrup)
- Email: engeny.krup@gmail.com
- Телефон: +375 44 416 08 65
- Местоположение: Минск, Беларусь
