PRAEKELT_PAYMENT = {
    'flickswitch_username': 'praekeltf_test',
    'flickswitch_password': 'praek_1234_eltf',
    # trailing slash included,
    'flickswitch_url': 'http://api.hotsocket.co.za:8080/test/'
}

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'update-recharge-status-every-minute': {
        'task': 'praekeltpayment.flickswitch.tasks.update_payment_status',
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

SECRET_KEY = '_l*l+!!^-t6%kzw*occccczgjdq=cn!*8q*b@&k^zn7spa)#)i'

INSTALLED_APPS = (
    'praekeltpayment.flickswitch',
    'django_nose',
    'south',
    'djcelery',
)

#import djcelery
#djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True
CELERY_IMPORTS = ('praekeltpayment.flickswitch.tasks.update_payment_status',
                    'praekeltpayment.flickswitch.api.send_airtime')
