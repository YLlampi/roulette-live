from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Statistic, DataItem

import json
import random
import asyncio

class DashboardConsumer(AsyncWebsocketConsumer):
    group_tasks = {}  # Diccionario para almacenar las tareas por grupo
    group_users = {}  # Diccionario para contar los usuarios por grupo

    async def connect(self):
        dashboard_slug = self.scope['url_route']['kwargs']['dashboard_slug']
        self.dashboard_slug = dashboard_slug
        self.room_group_name = f'stats-{dashboard_slug}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Incrementa el contador de usuarios para este grupo
        DashboardConsumer.group_users[self.room_group_name] = DashboardConsumer.group_users.get(self.room_group_name, 0) + 1

        # Verifica si el grupo ya tiene una tarea asociada
        if self.room_group_name not in DashboardConsumer.group_tasks:
            # Inicia una nueva tarea para el grupo y la almacena en el diccionario
            task = asyncio.create_task(self.send_random_number_periodically())
            DashboardConsumer.group_tasks[self.room_group_name] = task
            

    async def disconnect(self, code):
        print(f'Connection closed with code: {code}')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Decrementa el contador de usuarios para este grupo
        DashboardConsumer.group_users[self.room_group_name] -= 1

        # Verifica si este es el último usuario en el grupo
        if DashboardConsumer.group_users[self.room_group_name] == 0:
            # Cancela la tarea asociada con el grupo
            task = DashboardConsumer.group_tasks.pop(self.room_group_name, None)
            if task:
                task.cancel()

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