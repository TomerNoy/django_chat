import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import *


class ChatConsumer(WebsocketConsumer):
    def get_msgs(self, data):
        print('get msg')
        msgs = Msg.last_msgs()
        content = {'msgs': self.msgs_to_json(msgs)}
        self.send_msg(content)

    def new_msg(self, data):
        print('new msg', data)
        username = data['from']
        msg = Msg.objects.create(usr=username, content=data['message'])
        content = {'command': 'new_msg', 'message': self.msg_to_json(msg)}
        return self.send_chat_msg(content)

    def msgs_to_json(self, msgs):
        msgs_json = []
        for msg in msgs:
            msgs_json.append(self.msg_to_json(msg))
            return msgs_json

    def msg_to_json(self, msg):
        return {'usr': msg.usr, 'content': msg.content, 'time': str(msg.time)}

    commands = {'get_msgs': get_msgs, 'new_msg': new_msg}

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        data_json = json.loads(text_data)
        self.commands[data_json['command']](self, data_json)

    def send_chat_msg(self, msg):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {'type': 'chat_message', 'message': msg}
        )

    def send_msg(self, msg):
        self.send(text_data=json.dumps(msg))

    # Receive message from room group
    def chat_message(self, event):
        msg = event['message']
        self.send(text_data=json.dumps(msg))
