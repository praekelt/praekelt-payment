from celery import task
import requests
import json
from django.conf import settings
from praekeltpayment.flickswitch.models import PAYMENT_SUBMITTED, PAYMENT_FAILED
from praekeltpayment.flickswitch.utils import get_network_operator

SUCCESS = '0000'


def login():
    if not hasattr(settings, 'PRAEKELT_PAYMENT'):
        raise Exception('Imporperly configured. Please check your settings file.')

    username = settings.PRAEKELT_PAYMENT.get('flickswitch_username')
    password = settings.PRAEKELT_PAYMENT.get('flickswitch_password')
    url = settings.PRAEKELT_PAYMENT.get('flickswitch_url')

    if not username or not password or not url:
        raise Exception('Imporperly configured. Please check your settings file.')

    params = {
        'username': username,
        'password': password,
        'as_json': True
        }
    result = json.loads(requests.post('%slogin/' % url, params).text)

    if not result.get('status') == SUCCESS:
        raise Exception('Flicksitch: Invalid username or password')

    return result.get('token')


@task(ignore_result=True)
def send_aritime(instance):
    url = settings.PRAEKELT_PAYMENT.get('flickswitch_url')

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
            'reference': network_operator,
            'network code': instance.pk,
            'as_json': True,
        }
    result = json.loads(requests.post('%srecharge/' % url, params).text)

    if result.get('status') == SUCCESS:
        instance.state = PAYMENT_SUBMITTED
        instance.save()
    else:
        instance.state = PAYMENT_FAILED
        instance.fail_reason = result.get('message')
        instance.fail_code = result.get('status')
        instance.save()
