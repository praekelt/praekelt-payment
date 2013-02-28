import json
import requests
from django.conf import settings
from celery import task

from praekeltpayment.flickswitch.api import login
from praekeltpayment.flickswitch.models import (FlickSwitchPayment,
    PAYMENT_SUBMITTED, PAYMENT_FAILED, PAYMENT_SUCCESSFUL)

SUCCESS = '0000'
STATUS_FAILED = '2'
STATUS_SUCCESSFUL = '3'
STATUS_URL = '%sstatus/' % settings.PRAEKELT_PAYMENT.get('flickswitch_url')


def api_check_status(payment):
    token = login()
    params = {
        'token': token,
        'username': settings.PRAEKELT_PAYMENT.get('flickswitch_username'),
        'reference': payment.pk,
        'as_json': True,
    }
    return json.loads(requests.post(STATUS_URL, params).text).get('response')


@task(ignore_result=True)
def update_payment_status():
    for payment in FlickSwitchPayment.objects.filter(state=PAYMENT_SUBMITTED):
        result = api_check_status(payment)

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
