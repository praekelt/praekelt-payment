PRAEKELT_PAYMENT = {
    'flickswitch_username': 'xxx',
    'flickswitch_password': 'xxx',
    # trailing slash included,
    'flickswitch_url': 'http://api.hotsocket.co.za:8080/test/'
}

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    'update-recharge-status-every-minute': {
        'task': 'praekeltpayment.flickswitch.tasks.update_recharge_status',
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
