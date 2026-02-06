from django.contrib import admin
from .models import Complaint, ComplaintUpdate
from django.contrib.auth.models import User



# 🔹 INLINE UPDATES (appears inside Complaint page)
class ComplaintUpdateInline(admin.TabularInline):
    model = ComplaintUpdate
    extra = 0
    fields = ('status', 'remark', 'media', 'updated_at')
    readonly_fields = ('updated_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    # list view
    list_display = (
        'id',
        'user',
        'category',
        'location',
        'priority',
        'status',
        'created_at',
    )

    list_filter = ('status', 'priority', 'category')
    search_fields = ('category', 'description', 'user__username')

    inlines = [ComplaintUpdateInline]

    # 🔄 Sync main complaint when update is added
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        complaint = form.instance
        latest_update = complaint.updates.order_by('-updated_at').first()

        if latest_update:
            complaint.status = latest_update.status
            complaint.admin_comment = latest_update.remark
            complaint.save()

    # ONLY fields that must be read-only
    readonly_fields = (
        'user',
        'category',
        'other_category',
        'location',
        'description',
        'priority',
        'before_image',
        'created_at',
    )

    fieldsets = (
        ('User Info', {
            'fields': ('user','location')
        }),
        ('Complaint Details (Read Only)', {
            'fields': ('category', 'other_category', 'description', 'priority')
        }),
        ('Attachmetns', {
            'fields': ('before_image',)
        }),
        ('System Info', {
            'fields': ('created_at',)
        }),
    )

    # no adding complaints ❌
    def has_add_permission(self, request):
        return False

    # no deleting complaints ❌
    def has_delete_permission(self, request, obj=None):
        return False

    # allow editing (needed for status & image) ✅
    def has_change_permission(self, request, obj=None):
        return True


# ---------------- USER: READ ONLY ---------------- #

class ReadOnlyUserAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in User._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True


admin.site.unregister(User)
admin.site.register(User, ReadOnlyUserAdmin)
