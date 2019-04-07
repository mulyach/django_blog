from channels.generic.websocket import AsyncWebsocketConsumer
import json #, os, base64
#from Cryptodome.Cipher import AES

class ChatConsumer(AsyncWebsocketConsumer):
    """
    key64 = os.environ.get('CHAT_KEY', 'IFYYwIHnJu09t0-aO3u2Vg==')      #in string
    key = base64.urlsafe_b64decode(key64)                               #in byte

    def encrypt(self,message):                                               #input string
        cipher = AES.new(self.key, AES.MODE_EAX)
        ciphertext,tag = cipher.encrypt_and_digest(message.encode())
        comb_byte = cipher.nonce+tag+ciphertext
        return base64.urlsafe_b64encode(comb_byte).decode()             #return string

    def decrypt(self,comb_message):                                          #input string
        comb_byte = base64.urlsafe_b64decode(comb_message)
        nonce,tag,ciphertext = comb_byte[:16],comb_byte[16:32],comb_byte[32:]
        dcipher = AES.new(self.key, AES.MODE_EAX, nonce)
        return dcipher.decrypt_and_verify(ciphertext,tag).decode()      #return string
    """

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
        #print('message 2:',message)        
        #if message:message = self.decrypt(message)
        action = event['action']
        logs = event['logs']

        await self.send(text_data=json.dumps({
            'message': message,
            'action': action,
            'logs': logs,            
        }))

    """
    async def send(self,text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message','')
        action = text_data_json.get('action','')
        logs = text_data_json.get('logs','')

        print('message:',message)
        if message:message = self.encrypt(message)
        print('message:',message)
        text_data=json.dumps({
            'message': message,
            'action': action,
            'logs': logs,            
        })"""