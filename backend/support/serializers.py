from rest_framework import serializers
from .models import FAQCategory, FAQ, SupportTicket, SupportMessage, SupportAttachment, Refund

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class FAQCategorySerializer(serializers.ModelSerializer):
    faqs = FAQSerializer(many=True, read_only=True)
    class Meta:
        model = FAQCategory
        fields = '__all__'

class SupportAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportAttachment
        fields = '__all__'
        read_only_fields = ['uploaded_by']

class SupportMessageSerializer(serializers.ModelSerializer):
    attachments = SupportAttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = SupportMessage
        fields = ['id', 'ticket', 'sender_type', 'message', 'is_read', 'attachments', 'created_at']
        read_only_fields = ['id', 'sender_type', 'is_read', 'created_at', 'ticket']

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ['status', 'transaction_reference', 'processed_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = SupportMessageSerializer(many=True, read_only=True)
    attachments = SupportAttachmentSerializer(many=True, read_only=True)
    refunds = RefundSerializer(many=True, read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'user', 'order', 'issue_category', 'issue_type', 
            'subject', 'description', 'priority', 'status', 'assigned_agent', 
            'closed_at', 'created_at', 'updated_at', 'messages', 'attachments', 'refunds'
        ]
        read_only_fields = ['id', 'ticket_number', 'user', 'status', 'assigned_agent', 'closed_at', 'created_at', 'updated_at']
