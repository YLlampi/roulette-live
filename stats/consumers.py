from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Statistic, DataItem

import json
import random
import asyncio

class DashboardConsumer(AsyncWebsocketConsumer):
    connected_users = 0  # Variable de clase para contar los usuarios conectados

    async def connect(self):
        dashboard_slug = self.scope['url_route']['kwargs']['dashboard_slug']
        self.dashboard_slug = dashboard_slug
        self.room_group_name = f'stats-{dashboard_slug}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Inicia la tarea que envía números aleatorios cada 2 segundos
        # self.send_random_number_task = asyncio.create_task(self.send_random_number_periodically())

        DashboardConsumer.connected_users += 1  # Incrementa el contador cuando un usuario se conecta

        # Solo inicia la tarea si es el primer usuario conectado
        if DashboardConsumer.connected_users == 1:
            self.send_random_number_task = asyncio.create_task(self.send_random_number_periodically())
            



    async def disconnect(self, code):
        print(f'Connection closed with code: {code}')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Cancela la tarea cuando el cliente se desconecta
        # self.send_random_number_task.cancel()

        DashboardConsumer.connected_users -= 1  # Decrementa el contador cuando un usuario se desconecta

        # Cancela la tarea cuando el último usuario se desconecta
        if DashboardConsumer.connected_users == 0 and hasattr(self, 'send_random_number_task'):
            self.send_random_number_task.cancel()

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

    async def send_random_number_periodically(self):
        while True:
            random_number = random.randint(1, 100)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'send_random_number',
                'random_number': random_number
            })
            await asyncio.sleep(2)  # espera 2 segundos antes de enviar el próximo número

    # Esto es un manejador personalizado que envía el número aleatorio a todos los consumidores en el grupo
    async def send_random_number(self, event):
        random_number = event['random_number']
        await self.send(text_data=json.dumps({
            'random_number': random_number
        }))