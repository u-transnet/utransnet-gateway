# UTRANSNET-GATEWAY

Шлюз для перевода средств из BitShares в Transnet и обратно, реализованный на Django.
Для данного шлюза так же имеется отдельный [репозиторий](https://github.com/u-transnet/utransnet-gateway-dockerfiles) с docker'ом для упрощения развертывания шлюза.

## Предустановки

Для запуска проекта Вам необходимо создать файл конфигураций settings/local.py
Содержание файла должны иметь следующий вид.
```
from .base import *
from .development import *  # или production

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'public', 'static')
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'public', 'media')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your_own_random_secret_key_keep_it_safe'

BLOCKCHAIN_NOBROADCAST = False  # Используется,
# если необходимо не отсылать транзакции в блокчейн

# Конфигурации для сервиса Twillio

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_CALLER_ID = ''  # Номер телефона, который будет использоваться

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# Конфигурация базы данных

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

```

## Двухфакторная авторизация

В проект добавлена двухфакторная авторизация для обеспечения более высокого уровня
безопасноти доступа к панели администратора. <br>
Для функционирования двухфакторной авторизации необходим платный аккаунт в Twillio.
Платный аккаунт необходим потому, что пробная версия имеет ограниченный набор 
номеров телефона на который могут отправлены смс.
Описанные ниже конфигурации можно найти в настройках аккаунта в Twillio.

```
TWILIO_ACCOUNT_SID = ''  # ID Вашего аккаунта
TWILIO_AUTH_TOKEN = ''  # Auth token
TWILIO_CALLER_ID = ''  # Номер телефона, который будет использоваться
```

## Запуск шлюза

Управление шлюзом происходит с помощью с management-команд Django.
```
python3 manage.py activate_gateway --help

python3 manage.py activate_gateway bitshares_transnet
python3 manage.py activate_gateway transnet_bitshares
```