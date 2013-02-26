from django.contrib import admin
from praekeltpayment.flickswitch.models import FlickSwitchPayment


class FlickSwitchPaymentAdmin(admin.ModelAdmin):
    search_fields = ('msisdn',)
    list_display = ('msisdn', 'amount', 'date', 'state', 'fail_reason')
    list_filter = ('state', )
    ordering = ('-date',)
    date_hierarchy = 'date'

admin.site.register(FlickSwitchPayment, FlickSwitchPaymentAdmin)
