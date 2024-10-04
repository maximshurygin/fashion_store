# Fashion Store

**Fashion Store** — это полноценный онлайн-магазин одежды, разработанный на Django, позволяющий пользователям просматривать, фильтровать и приобретать различные товары. Проект включает в себя функциональность корзины, избранного, оформления заказов с отправкой подтверждающих писем, а также полноценную систему аутентификации пользователей.

## 🚀 Функциональность

### Основные функции:
- **Просмотр товаров:**
  - Категории: Все товары, Мужские, Женские
  - Детальная информация о каждом товаре
- **Фильтрация товаров:**
  - По полу и категориям
- **Корзина:**
  - Добавление товаров в корзину
  - Обновление количества товаров
  - Удаление товаров из корзины
- **Избранное:**
  - Добавление и удаление товаров из списка избранного
- **Оформление заказа:**
  - Создание и просмотр деталей заказа
  - Отмена заказа
  - Отправка подтверждающего письма на электронную почту
- **Аутентификация пользователей:**
  - Регистрация, вход и выход из системы
  - Активация аккаунта через электронную почту
  - Сброс и изменение пароля
  - Просмотр и редактирование профиля
- **Статические страницы:**
  - О нас, Контакты, Информация о возвратах и других аспектах

## 🎨 Фронтенд

В качестве основы фронтенда был использован бесплатный HTML шаблон, который был адаптирован и кастомизирован под нужды проекта. Основные изменения включают:
- Интеграцию с Django backend'ом
- Адаптацию под функциональность интернет-магазина
- Добавление пользовательских стилей и компонентов

## 🔧 Технологии

- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript (на основе адаптированного шаблона)
- **База данных:** PostgreSQL
- **Асинхронные задачи:** Celery с Redis
- **Контейнеризация:** Docker

## 🛠 Развертывание проекта

### Требования
- Docker
- Docker Compose

### Шаги по развертыванию

1. Клонируйте репозиторий:
```bash
git clone https://github.com/maximshurygin/fashion_store.git
cd fashion_store
```

2. Создайте файл `.env` в корневой директории проекта:
```
# Настройки Django
DEBUG=1
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS='localhost,127.0.0.1'

# Настройки электронной почты
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True

# Настройка базы данных
DB_NAME=fashion_store
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Запустите проект с помощью Docker Compose:
```bash
docker-compose up --build
```

После успешного запуска, приложение будет доступно по адресу: http://localhost:8000

### Что происходит при запуске
- Автоматически разворачиваются все необходимые сервисы:
  - Django приложение
  - База данных PostgreSQL
  - Redis для кэширования
  - Celery для асинхронных задач
- Применяются миграции базы данных
- Создается суперпользователь

### Важные замечания
- Убедитесь, что вы заменили все placeholder'ы в файле `.env` на реальные значения
- Для отправки email необходимо использовать реальные данные SMTP-сервера
- Для остановки всех сервисов используйте:
```bash
docker-compose down
```
- Все сервисы (включая Redis и Celery) настроены автоматически и не требуют дополнительной конфигурации