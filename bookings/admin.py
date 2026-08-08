from django.contrib import admin
from .models import Booking
from payments.models import Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('id', 'transaction_id', 'amount', 'status', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent', 'lsa', 'booking_date', 'start_time', 'end_time', 'status', 'created_at')
    list_filter = ('status', 'booking_date')
    list_editable = ('status',)
    search_fields = ('id', 'parent__first_name', 'parent__last_name', 'parent__email', 'lsa__first_name', 'lsa__last_name', 'lsa__email')
    date_hierarchy = 'booking_date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PaymentInline]
