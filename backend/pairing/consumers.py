import json
from channels.generic.websocket import AsyncWebSocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class PairPracticeConsumer(AsyncWebSocketConsumer):
    async def connect(self):
        if isinstance(self.scope['user'], AnonymousUser):
            await self.close()
            return

        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'pair_{self.session_id}'
        self.user = self.scope['user']

        is_valid = await self.validate_session()
        if not is_valid:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'system_message',
            'message': f'{self.user.username} 已加入练习',
            'user_id': self.user.id,
        })

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'system_message',
            'message': f'{self.user.username} 已离开练习',
            'user_id': self.user.id,
        })

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'braille_challenge':
            await self.save_message('braille_challenge', data)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'challenge_message',
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sentence': data.get('sentence', ''),
                'braille_text': data.get('braille_text', ''),
            })

        elif msg_type == 'text':
            await self.save_message('text', data)
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'text_message',
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'message': data.get('message', ''),
            })

        elif msg_type == 'audio_result':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'result_message',
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'is_correct': data.get('is_correct'),
                'confidence': data.get('confidence'),
                'predicted_character': data.get('predicted_character', ''),
                'target_character': data.get('target_character', ''),
            })

    async def challenge_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'braille_challenge',
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sentence': event['sentence'],
            'braille_text': event['braille_text'],
        }))

    async def text_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'text',
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'message': event['message'],
        }))

    async def result_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'audio_result',
            'sender_id': event['sender_id'],
            'sender_name': event.get('sender_name', ''),
            'is_correct': event['is_correct'],
            'confidence': event['confidence'],
            'predicted_character': event['predicted_character'],
            'target_character': event.get('target_character', ''),
            'session_accuracy': event.get('session_accuracy'),
        }))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system',
            'message': event['message'],
            'user_id': event['user_id'],
        }))

    @database_sync_to_async
    def validate_session(self):
        from .models import PairSession
        from django.db.models import Q
        return PairSession.objects.filter(
            Q(initiator=self.user) | Q(partner=self.user),
            id=self.session_id,
            status__in=['pending', 'active'],
        ).exists()

    @database_sync_to_async
    def save_message(self, msg_type, data):
        from .models import PairSession, PairMessage
        try:
            session = PairSession.objects.get(id=self.session_id)
            PairMessage.objects.create(
                pair_session=session,
                sender=self.user,
                message_type=msg_type,
                content=data,
            )
        except PairSession.DoesNotExist:
            pass
