import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SupportTicket, SupportMessage
from accounts.models import User

class SupportChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope['url_route']['kwargs']['ticket_id']
        self.room_group_name = f'ticket_{self.ticket_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'send_message':
            message = text_data_json.get('message')
            user_id = text_data_json.get('user_id')
            
            # Save message to database
            msg_obj, should_trigger_ai, history = await self.save_message(self.ticket_id, user_id, message)
            
            if msg_obj:
                # Send user message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender_id': user_id,
                        'message_id': str(msg_obj.id),
                        'created_at': msg_obj.created_at.isoformat()
                    }
                )

                if should_trigger_ai:
                    # Show typing indicator
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'typing_indicator',
                            'user_id': 'ai_agent'
                        }
                    )
                    
                    # Generate AI response
                    ai_response = await self.get_ai_response(user_id, message, history)
                    
                    if ai_response:
                        ai_msg_obj = await self.save_ai_message(self.ticket_id, ai_response)
                        
                        # Send AI message to room group
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': ai_response,
                                'sender_id': 'ai_agent',
                                'message_id': str(ai_msg_obj.id),
                                'created_at': ai_msg_obj.created_at.isoformat()
                            }
                        )
                    
        elif action == 'typing':
            user_id = text_data_json.get('user_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': user_id
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'message_id': event['message_id'],
            'created_at': event['created_at']
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id']
        }))

    @database_sync_to_async
    def save_message(self, ticket_id, user_id, message):
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            user = User.objects.get(id=user_id)
            sender_type = SupportMessage.SenderType.AGENT if user.is_staff else SupportMessage.SenderType.USER
            msg_obj = SupportMessage.objects.create(
                ticket=ticket,
                sender=user,
                sender_type=sender_type,
                message=message
            )
            
            should_trigger_ai = ticket.status == SupportTicket.Status.OPEN and not ticket.assigned_agent and not user.is_staff
            history = []
            
            if should_trigger_ai:
                history = [
                    {"role": "user" if m.sender_type == "user" else "assistant", "content": m.message}
                    for m in ticket.messages.all().order_by("created_at")
                ]
                
            return msg_obj, should_trigger_ai, history
        except Exception as e:
            import logging
            logging.error(f"WebSocket save_message error: {e}")
            return None, False, []

    @database_sync_to_async
    def get_ai_response(self, user_id, message, history):
        try:
            from ai_engine.services import AIService
            user = User.objects.get(id=user_id)
            return AIService.food_chat(user, message, history)
        except Exception as e:
            import logging
            logging.error(f"WebSocket AI error: {e}")
            return None

    @database_sync_to_async
    def save_ai_message(self, ticket_id, response_text):
        try:
            ticket = SupportTicket.objects.get(id=ticket_id)
            return SupportMessage.objects.create(
                ticket=ticket,
                sender_type=SupportMessage.SenderType.AI,
                message=response_text
            )
        except Exception as e:
            return None
