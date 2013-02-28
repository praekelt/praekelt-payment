from celery import task
import requests
import json
from django.conf import settings
from praekeltpayment.flickswitch.utils import get_network_operator

PAYMENT_FAILED = 3
PAYMENT_SUBMITTED = 1

SUCCESS = '0000'
STATUS_FAILED = '2'
STATUS_SUCCESSFUL = '3'

LOGIN_URL = '%slogin/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')
RECHARGE_URL = '%srecharge/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')


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
    result = json.loads(requests.post(LOGIN_URL, params).text).get('response')

    if not result or not result.get('status') == SUCCESS:
        raise LoginException('Invalid username or password')

    return result.get('token')


def api_recharge(payment, product_code):
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
        'product_code': product_code,
        'denomination': payment.amount,
        'reference': payment.pk,
        'network_code': network_operator,
        'as_json': True,
    }
    return json.loads(requests.post(RECHARGE_URL, params).text).get('response')


@task(ignore_result=True)
def send_airtime(payment):
    result = api_recharge(payment, 'AIRTIME')

    if result.get('status') == SUCCESS:
        payment.state = PAYMENT_SUBMITTED
        payment.save()
    else:
        payment.state = PAYMENT_FAILED
        payment.fail_reason = result.get('message')
        payment.fail_code = result.get('status')
        payment.save()
