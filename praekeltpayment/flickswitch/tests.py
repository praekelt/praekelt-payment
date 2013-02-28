from django.test import TestCase
from flickswitch.utils import get_network_operator
from flickswitch.models import (FlickSwitchPayment,
    PAYMENT_CREATED, PAYMENT_SUBMITTED, PAYMENT_FAILED,
    PAYMENT_SUCCESSFUL)
from flickswitch.api import STATUS_FAILED, STATUS_SUCCESSFUL
from flickswitch import tasks
from mock import patch


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

    def test_initial_payment_state(self):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)

    @patch('flickswitch.api.api_recharge')
    @patch('flickswitch.api.login')
    def test_submitted_payment_state(self, mock_login,
        mock_api_recharge):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)

        result = {
            'status': '0000',
        }
        mock_api_recharge.return_value = result
        p.send_airtime()

        p = FlickSwitchPayment.objects.get(pk=p.pk)
        self.assertEqual(p.state, PAYMENT_SUBMITTED)

    @patch('flickswitch.api.api_recharge')
    @patch('flickswitch.api.login')
    def test_failed_payment_submit_state(self, mock_login,
        mock_api_recharge):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)

        mock_login.return_value = 'sampletoken'
        result = {
            'status': '1111',
            'message': 'Invalid',
        }
        mock_api_recharge.return_value = result
        p.send_airtime()

        p = FlickSwitchPayment.objects.get(pk=p.pk)
        self.assertEqual(p.state, PAYMENT_FAILED)
        self.assertEqual(p.fail_code, '1111')
        self.assertEqual(p.fail_reason, 'Invalid')

    @patch('flickswitch.tasks.api_check_status')
    @patch('flickswitch.api.login')
    def test_successful_payment_state(self, mock_login, mock_api_check_status):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)

        p.state = PAYMENT_SUBMITTED  # fake api gateway call
        p.save()

        mock_login.return_value = 'sampletoken'
        result = {
            'status': '0000',
            'recharge_status_cd': STATUS_SUCCESSFUL,
        }
        mock_api_check_status.return_value = result

        tasks.update_payment_status.delay()

        p = FlickSwitchPayment.objects.get(pk=p.pk)
        self.assertEqual(p.state, PAYMENT_SUCCESSFUL)
        self.assertIsNone(p.fail_code)
        self.assertIsNone(p.fail_reason)

    @patch('flickswitch.tasks.api_check_status')
    @patch('flickswitch.api.login')
    def test_failed_payment_state(self, mock_login, mock_api_check_status):
        p = FlickSwitchPayment.objects.create(msisdn='27821234567', amount=500)
        self.assertEqual(p.state, PAYMENT_CREATED)

        p.state = PAYMENT_SUBMITTED  # fake api gateway call
        p.save()

        mock_login.return_value = 'sampletoken'
        result = {
            'status': '0000',
            'recharge_status_cd': STATUS_FAILED,
            'recharge_status': 'Incorrect Network Operator',
        }
        mock_api_check_status.return_value = result
        tasks.update_payment_status()

        p = FlickSwitchPayment.objects.get(pk=p.pk)
        self.assertEqual(p.state, PAYMENT_FAILED)
        self.assertEqual(p.fail_code, STATUS_FAILED)
        self.assertEqual(p.fail_reason, 'Incorrect Network Operator')
