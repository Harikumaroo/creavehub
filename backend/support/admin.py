from django.contrib import admin
from .models import FAQCategory, FAQ, SupportTicket, SupportMessage, SupportAttachment, Refund

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'views', 'is_active', 'created_at')
    list_filter = ('is_active', 'category')
    search_fields = ('question', 'answer')

class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('created_at',)

class SupportAttachmentInline(admin.TabularInline):
    model = SupportAttachment
    extra = 0
    readonly_fields = ('created_at',)

class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'user', 'subject', 'status', 'priority', 'assigned_agent', 'created_at')
    list_filter = ('status', 'priority', 'issue_category')
    search_fields = ('ticket_number', 'subject', 'description', 'user__mobile_number', 'user__full_name')
    readonly_fields = ('ticket_number', 'created_at', 'updated_at', 'closed_at')
    inlines = [SupportMessageInline, SupportAttachmentInline, RefundInline]

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'order', 'amount', 'refund_type', 'status', 'created_at')
    list_filter = ('status', 'refund_type', 'reason')
    search_fields = ('ticket__ticket_number', 'transaction_reference')
