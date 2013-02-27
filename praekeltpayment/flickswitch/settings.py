PRAEKELT_PAYMENT = {
    'flickswitch_username': 'praekeltf_test',
    'flickswitch_password': 'praek_1234_eltf',
    # trailing slash included,
    'flickswitch_url': 'http://api.hotsocket.co.za:8080/test/'
}

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'update-recharge-status-every-minute': {
        'task': 'flickswitch.tasks.update_payment_status',
        'schedule': timedelta(seconds=60)
    },
}


# For TEST ONLY
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'my_db.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'flickswitch',
    'django_nose',
    'south',
    'djcelery',
)

#import djcelery
#djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True
CELERY_IMPORTS = ('flickswitch.api.update_payment_status',
                    'flickswitch.api.send_airtime')
