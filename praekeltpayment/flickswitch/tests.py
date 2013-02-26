import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'praekeltpayment.flickswitch.settings'

from django.test import TestCase
from praekeltpayment.flickswitch.utils import get_network_operator
from praekeltpayment.flickswitch.models import *


class FlickSwitchPaymentTestCase(TestCase):
    def test_network_operator_mapping(self):
        op = get_network_operator('27829000000')
        self.assertEqual(op, 'VOD')
        op = get_network_operator('27729000000')
        self.assertEqual(op, 'VOD')
        op = get_network_operator('27714000000')
        self.assertEqual(op, 'VOD')

        op = get_network_operator('27719000000')
        self.assertEqual(op, 'MTN')
        op = get_network_operator('27839000000')
        self.assertEqual(op, 'MTN')

        op = get_network_operator('27849000000')
        self.assertEqual(op, 'CELLC')
        op = get_network_operator('27749000000')
        self.assertEqual(op, 'CELLC')

        op = get_network_operator('27811000000')
        self.assertEqual(op, '8TA')
        op = get_network_operator('27814000000')
        self.assertEqual(op, '8TA')

    def test_invalid_msisdn(self):
        op = get_network_operator('27754000000')
        self.assertEqual(op, None)

    def test_send_airtime_task(self):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)
