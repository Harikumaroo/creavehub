import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FAQCategory, FAQ, SupportTicket, SupportMessage, SupportAttachment, Refund
from .serializers import (
    FAQCategorySerializer, FAQSerializer, SupportTicketSerializer,
    SupportMessageSerializer, RefundSerializer
)
from ai_engine.services import AIService

logger = logging.getLogger(__name__)

# Action signals that the AI embeds in its response
ESCALATE_TAG         = '[ESCALATE]'
WAITING_TAG          = '[WAITING_FOR_CUSTOMER]'


def _parse_ai_response(raw: str):
    """
    Strips action tags from the AI message and returns
    (clean_message, action) where action is one of:
        'escalate' | 'waiting' | None
    """
    action  = None
    message = raw.strip()

    if ESCALATE_TAG in message:
        action  = 'escalate'
        message = message.replace(ESCALATE_TAG, '').strip()
    elif WAITING_TAG in message:
        action  = 'waiting'
        message = message.replace(WAITING_TAG, '').strip()

    return message, action


class FAQCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQCategory.objects.all()
    serializer_class = FAQCategorySerializer
    permission_classes = [permissions.AllowAny]


class FAQViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]


class SupportTicketViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupportTicketSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        ticket = self.get_object()

        # 1. Save user message
        message_text = request.data.get('message')
        if not message_text:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            sender_type=SupportMessage.SenderType.USER,
            message=message_text
        )

        # 2. Get AI response — only when ticket is OPEN and unassigned
        if ticket.status in (SupportTicket.Status.OPEN, SupportTicket.Status.WAITING_FOR_CUSTOMER) \
                and not ticket.assigned_agent:
            try:
                # Build conversation history (exclude system messages)
                history = [
                    {
                        "role": "user" if m.sender_type == "user" else "assistant",
                        "content": m.message,
                    }
                    for m in ticket.messages.filter(
                        sender_type__in=["user", "ai"]
                    ).order_by("created_at")
                ]

                raw_response = AIService.support_chat(
                    request.user,
                    message_text,
                    history,
                    ticket_subject=ticket.subject,
                    ticket_category=ticket.issue_category,
                )

                if raw_response:
                    clean_message, ai_action = _parse_ai_response(raw_response)

                    # Save the clean AI reply (no tags)
                    SupportMessage.objects.create(
                        ticket=ticket,
                        sender_type=SupportMessage.SenderType.AI,
                        message=clean_message,
                    )

                    # ── Handle escalation actions ──────────────────────
                    if ai_action == 'escalate':
                        ticket.status   = SupportTicket.Status.ESCALATED
                        ticket.priority = SupportTicket.Priority.HIGH
                        ticket.save(update_fields=['status', 'priority', 'updated_at'])

                        # Append a visible system notification in the chat
                        SupportMessage.objects.create(
                            ticket=ticket,
                            sender_type=SupportMessage.SenderType.AI,
                            message=(
                                "🔴 FLAGGED FOR REVIEW — Your issue has been flagged "
                                "as high priority. Our team will look into this and "
                                "get back to you shortly. Thank you for your patience."
                            ),
                        )
                        logger.info(
                            "Ticket %s escalated to human support by AI (user=%s)",
                            ticket.ticket_number, request.user.id
                        )

                    elif ai_action == 'waiting':
                        ticket.status = SupportTicket.Status.WAITING_FOR_CUSTOMER
                        ticket.save(update_fields=['status', 'updated_at'])
                        logger.info(
                            "Ticket %s set to WAITING_FOR_CUSTOMER by AI",
                            ticket.ticket_number
                        )

            except Exception as e:
                logger.error("AI support error on ticket %s: %s", pk, e)

        # 3. Return the refreshed full ticket (with all messages)
        ticket.refresh_from_db()
        serializer = self.get_serializer(ticket)
        return Response(serializer.data)


class RefundViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RefundSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Refund.objects.all()
        return Refund.objects.filter(ticket__user=self.request.user)
