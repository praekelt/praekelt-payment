Praekelt Payment
================
**This is a collection of all payment gateways we use**

.. contents:: Contents
    :depth: 4

FlickSwitch
-----------
FlickSwitch allows you to send Pin-less recharging to *most networks in South Africa (MTN, Voda, CellC, 8ta)

This module currently only wraps the Airtime recharge functionality.

Requirements
************

1. Dependencies
~~~~~~~~~~~~~~~

* Django 1.3+
* Celery 3.0+

2. Settings
~~~~~~~~~~~

You have to specify your FlickSwitch account details::

 PRAEKELT_PAYMENT = {
     'flickswitch_username': 'xxx',
     'flickswitch_password': 'xxx',
     'flickswitch_url': 'http://api.hotsocket.co.za:8080/' #trailing slash included,
 }

**Django Celery**

You need to include the scheduler to check for recharge status::

 from datetime import timedelta
 CELERYBEAT_SCHEDULE = {
     'update-recharge-status-every-minute': {
         'task': 'praekeltpayment.flickswitch.tasks.update_recharge_status',
         'schedule': timedelta(seconds=60)
     },
     ...
 }
