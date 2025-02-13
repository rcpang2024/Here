import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ..home.models import Conversation, Message
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender']

        sender = await sync_to_async(User.objects.get)(id=sender_id)
        conversation = await sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        message_obj = await sync_to_async(Message.objects.create)(conversation=conversation, sender=sender, text=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'message': message,
                'timestamp': message_obj.timestamp.strftime('%m-%d-%Y %I:%M %p')
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))