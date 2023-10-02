from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Statistic, DataItem

import json


class DashboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        dashboard_slug = self.scope['url_route']['kwargs']['dashboard_slug']
        self.dashboard_slug = dashboard_slug
        self.room_group_name = f'stats-{dashboard_slug}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        print(f'Connection closed with code: {code}')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = text_data_json['sender']

        print(message, )
        print(sender)

        dashboard_slug = self.dashboard_slug
        await self.save_data_item(sender, message, dashboard_slug)

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'statistics_message',
            'message': message,
            'sender': sender,

        })

    async def statistics_message(self, event):
        message = event['message']
        sender = event['sender']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,

        }))

    @database_sync_to_async
    def create_data_item(self, sender, message, slug):
        obj = Statistic.objects.get(slug=slug)
        return DataItem.objects.create(statistic=obj, value=message, owner=sender)

    async def save_data_item(self, sender, message, slug):
        await self.create_data_item(sender, message, slug)
