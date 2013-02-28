from django.db import models
from flickswitch.api import send_airtime

PAYMENT_CREATED = 0
PAYMENT_SUBMITTED = 1
PAYMENT_SUCCESSFUL = 2
PAYMENT_FAILED = 3

PAYMENT_STATES = (
        (PAYMENT_CREATED, 'Created'),
        (PAYMENT_SUBMITTED, 'Submitted'),
        (PAYMENT_SUCCESSFUL, 'Successful'),
        (PAYMENT_FAILED, 'Failed'),
    )


class FlickSwitchPayment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    msisdn = models.CharField(max_length=20)
    amount = models.PositiveIntegerField()
    fail_reason = models.CharField(max_length=100, blank=True, null=True)
    fail_code = models.CharField(max_length=20, blank=True, null=True)
    state = models.PositiveIntegerField(choices=PAYMENT_STATES,
                                        default=PAYMENT_CREATED)

    def send_airtime(self):
        if self.state == PAYMENT_CREATED or self.state == PAYMENT_FAILED:
            send_airtime.delay(self)
