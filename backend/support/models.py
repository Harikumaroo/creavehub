import uuid
from django.db import models
from django.conf import settings
from core.models import BaseModel
from orders.models import Order

class FAQCategory(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = "support_faq_category"
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"

    def __str__(self):
        return self.name

class FAQ(BaseModel):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    views = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "support_faq"
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["-views"]

    def __str__(self):
        return self.question

class SupportTicket(BaseModel):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        WAITING_FOR_CUSTOMER = "waiting_for_customer", "Waiting for Customer"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"
        ESCALATED = "escalated", "Escalated"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    ticket_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="support_tickets")
    
    issue_category = models.CharField(max_length=100)
    issue_type = models.CharField(max_length=100)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.LOW)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.OPEN)
    
    assigned_agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "support_tickets_v2"
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            import datetime
            year = datetime.datetime.now().year
            # E.g. CH-TKT-2026-UUID
            self.ticket_number = f"CH-TKT-{year}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"

class SupportMessage(BaseModel):
    class SenderType(models.TextChoices):
        USER = "user", "User"
        AGENT = "agent", "Support Agent"
        AI = "ai", "AI Assistant"

    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sender_type = models.CharField(max_length=10, choices=SenderType.choices, default=SenderType.USER)
    message = models.TextField(blank=True, default="")
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "support_ticket_messages_v2"
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.sender_type} on {self.ticket.ticket_number}"

class SupportAttachment(BaseModel):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="attachments")
    message = models.ForeignKey(SupportMessage, on_delete=models.CASCADE, related_name="attachments", null=True, blank=True)
    file = models.FileField(upload_to='support/attachments/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = "support_ticket_attachments"

    def __str__(self):
        return f"Attachment for {self.ticket.ticket_number}"

class Refund(BaseModel):
    class RefundType(models.TextChoices):
        FULL_REFUND = "full", "Full Refund"
        PARTIAL_REFUND = "partial", "Partial Refund"
        WALLET_CREDIT = "wallet", "Wallet Credit"
        COUPON_COMPENSATION = "coupon", "Coupon Compensation"

    class RefundReason(models.TextChoices):
        ORDER_NOT_DELIVERED = "order_not_delivered", "Order Not Delivered"
        MISSING_ITEM = "missing_item", "Missing Item"
        WRONG_ITEM = "wrong_item", "Wrong Item"
        DAMAGED_ITEM = "damaged_item", "Damaged Item"
        QUALITY_ISSUE = "quality_issue", "Quality Issue"
        PAYMENT_FAILURE = "payment_failure", "Payment Failure"
        OTHER = "other", "Other"

    class RefundStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"

    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name="refunds")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds", null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_type = models.CharField(max_length=20, choices=RefundType.choices)
    reason = models.CharField(max_length=30, choices=RefundReason.choices)
    status = models.CharField(max_length=20, choices=RefundStatus.choices, default=RefundStatus.PENDING)
    
    # Track the Razorpay refund ID or internal transaction reference
    transaction_reference = models.CharField(max_length=100, blank=True, default="")
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "support_refunds"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund for {self.ticket.ticket_number} - {self.amount}"
