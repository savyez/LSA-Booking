from django.contrib import admin
from .models import Parent, LSAProfile
from bookings.models import Booking


class ParentBookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('id', 'lsa', 'booking_date', 'start_time', 'end_time', 'status')
    readonly_fields = ('id', 'lsa', 'booking_date', 'start_time', 'end_time', 'status')
    show_change_link = True


class LSABookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('id', 'parent', 'booking_date', 'start_time', 'end_time', 'status')
    readonly_fields = ('id', 'parent', 'booking_date', 'start_time', 'end_time', 'status')
    show_change_link = True


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ParentBookingInline]


@admin.register(LSAProfile)
class LSAProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'hourly_rate', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'skills')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [LSABookingInline]
