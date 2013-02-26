from celery import task
import requests
import json
from django.conf import settings
from praekeltpayment.flickswitch.models import (FlickSwitchPayment,
    PAYMENT_SUBMITTED, PAYMENT_FAILED, PAYMENT_SUCCESSFUL)
from praekeltpayment.flickswitch.utils import get_network_operator

SUCCESS = '0000'
STATUS_FAILED = 2
STATUS_SUCCESSFUL = 3

LOGIN_URL = '%slogin/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')
RECHARGE_URL = '%srecharge/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')
STATUS_URL = '%sstatus/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')


def login():
    if not hasattr(settings, 'PRAEKELT_PAYMENT'):
        raise Exception('Imporperly configured. Please check your settings file.')

    username = settings.PRAEKELT_PAYMENT.get('flickswitch_username')
    password = settings.PRAEKELT_PAYMENT.get('flickswitch_password')

    if not username or not password:
        raise Exception('Imporperly configured. Please check your settings file.')

    params = {
        'username': username,
        'password': password,
        'as_json': True
        }
    result = json.loads(requests.post(LOGIN_URL, params).text)

    if not result.get('status') == SUCCESS:
        raise Exception('Flicksitch: Invalid username or password')

    return result.get('token')


@task(ignore_result=True)
def send_aritime(instance):
    network_operator = get_network_operator(instance.msisdn)
    if not network_operator:
        instance.state = PAYMENT_FAILED
        instance.fail_reason = 'Unknown network operator'
        instance.save()
        return

    try:
        token = login()
    except:
        instance.state = PAYMENT_FAILED
        instance.fail_reason = 'Flickswitch login failed'
        instance.save()
        return

    params = {
            'token': token,
            'username': settings.PRAEKELT_PAYMENT.get('flickswitch_username'),
            'recipient_msisdn': instance.msisdn,
            'product_code': 'AIRTIME',
            'denomination': instance.amount,
            'reference': instance.pk,
            'network_code': network_operator,
            'as_json': True,
        }
    result = json.loads(requests.post(RECHARGE_URL, params).text)

    if result.get('status') == SUCCESS:
        instance.state = PAYMENT_SUBMITTED
        instance.save()
    else:
        instance.state = PAYMENT_FAILED
        instance.fail_reason = result.get('message')
        instance.fail_code = result.get('status')
        instance.save()


@task(ignore_result=True)
def update_payment_status():
    token = login()

    for payment in FlickSwitchPayment.objects.filter(state=PAYMENT_SUBMITTED):
        params = {
            'token': token,
            'username': settings.PRAEKELT_PAYMENT.get('flickswitch_username'),
            'reference': payment.pk,
            'as_json': True,
        }
        result = json.loads(requests.post(STATUS_URL, params).text)

        if result.get('status') == SUCCESS:
            if result.get('recharge_status_cd') == STATUS_FAILED:
                payment.state = PAYMENT_FAILED
                payment.fail_code = STATUS_FAILED
                payment.fail_reason = result.get('recharge_status')
                payment.save()
            elif result.get('recharge_status_cd') == STATUS_SUCCESSFUL:
                payment.state = PAYMENT_SUCCESSFUL
                payment.fail_code = None
                payment.fail_reason = None
                payment.save()
