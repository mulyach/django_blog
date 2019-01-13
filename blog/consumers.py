from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' %self.room_name

        ##Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
            )
        await self.accept()

    async def disconnect(self, close_code):
        ##Leave the room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
            )

    ##receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message','')
        action = text_data_json.get('action','')
        logs = text_data_json.get('logs','')
        #async_to_sync(self.channel_layer.group_send)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'action': action,
                'logs': logs,
            }
            )

    ##receive message from room group
    async def chat_message(self, event):
        message = event['message']
        action = event['action']
        logs = event['logs']

        await self.send(text_data=json.dumps({
            'message': message,
            'action': action,
            'logs': logs,            
        }))