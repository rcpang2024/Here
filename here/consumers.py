import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from home.models import Conversation, Message, User
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"chat_{self.conversation_id}"

        # Ensure channel_layer is set
        if not self.channel_layer:
            self.channel_layer = get_channel_layer()

        if self.channel_layer is None:
            print("Error: Channel Layer is not configured correctly.")
            await self.close()
            return

        # Add channel to group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # message = data['message']
        # maybe change back to not using get? - now empty messages being returned
        message = data.get('message', '')
        sender_username = data['sender']
        media_url = data.get('media', None)
        print("message: ", message)
        print("sender_username: ", sender_username)
        print("media_url: ", media_url)
        try:
            sender = await sync_to_async(User.objects.get)(username=sender_username)
        except User.DoesNotExist:
            print(f"Error: User '{sender_username}' does not exist.")  # Debugging log
            await self.send(text_data=json.dumps({
                "error": "User does not exist."
            }))
            return  # Prevents crashing

        conversation = await sync_to_async(Conversation.objects.get)(id=self.conversation_id)
        message_obj = await sync_to_async(Message.objects.create)(conversation=conversation, sender=sender, text=message, media=media_url)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'message': message,
                'media': media_url if media_url else None,
                'timestamp': message_obj.timestamp.strftime('%m-%d-%Y %I:%M %p')
            }
        )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'message': event['message'],
            'media': event['media'],
            'timestamp': event['timestamp']
        }))