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


class FlickSwitchException(Exception):
    pass


class LoginException(FlickSwitchException):
    pass


class BadConfigurationException(FlickSwitchException):
    pass


def login():
    if not hasattr(settings, 'PRAEKELT_PAYMENT'):
        msg = 'Imporperly configured. Please check your settings file.'
        raise BadConfigurationException(msg)

    username = settings.PRAEKELT_PAYMENT.get('flickswitch_username')
    password = settings.PRAEKELT_PAYMENT.get('flickswitch_password')

    if not username or not password:
        msg = 'Imporperly configured. Please check your settings file.'
        raise BadConfigurationException(msg)

    params = {
        'username': username,
        'password': password,
        'as_json': True
        }
    result = json.loads(requests.post(LOGIN_URL, params).text)

    if not result.get('status') == SUCCESS:
        raise LoginException('Invalid username or password')

    return result.get('token')


@task(ignore_result=True)
def send_airtime(payment):
    network_operator = get_network_operator(payment.msisdn)
    if not network_operator:
        payment.state = PAYMENT_FAILED
        payment.fail_reason = 'Unknown network operator'
        payment.save()
        return

    try:
        token = login()
    except LoginException:
        payment.state = PAYMENT_FAILED
        payment.fail_reason = 'Flickswitch login failed'
        payment.save()
        return

    params = {
            'token': token,
            'username': settings.PRAEKELT_PAYMENT.get('flickswitch_username'),
            'recipient_msisdn': payment.msisdn,
            'product_code': 'AIRTIME',
            'denomination': payment.amount,
            'reference': payment.pk,
            'network_code': network_operator,
            'as_json': True,
        }
    result = json.loads(requests.post(RECHARGE_URL, params).text)
    apply_send_airtime(payment, result)


def apply_send_airtime(payment, result):
    if result.get('status') == SUCCESS:
        payment.state = PAYMENT_SUBMITTED
        payment.save()
    else:
        payment.state = PAYMENT_FAILED
        payment.fail_reason = result.get('message')
        payment.fail_code = result.get('status')
        payment.save()


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
        apply_update_payment_status(payment, result)


def apply_update_payment_status(payment, result):
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
