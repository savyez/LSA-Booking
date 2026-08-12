from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'transaction_id', 'amount', 'status', 'created_at')
    list_select_related = ('booking', 'booking__parent', 'booking__lsa')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    search_fields = ('transaction_id', 'booking__id', 'booking__parent__first_name', 'booking__parent__last_name')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'booking__parent', 'booking__lsa')
