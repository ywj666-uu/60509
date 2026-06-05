from celery import shared_task
from .models import AudioRecording
from .inference import classify_audio


@shared_task(bind=True, max_retries=3)
def process_audio_recording(self, recording_id):
    try:
        recording = AudioRecording.objects.get(id=recording_id)
        recording.processing_status = 'processing'
        recording.save(update_fields=['processing_status'])

        predicted_char, confidence = classify_audio(recording.audio_file.path)

        recording.predicted_character = predicted_char
        recording.confidence = confidence
        if recording.target_character:
            recording.is_correct = (predicted_char == recording.target_character.character)
        else:
            recording.is_correct = None
        recording.processing_status = 'completed'
        recording.save(update_fields=[
            'predicted_character', 'confidence', 'is_correct', 'processing_status'
        ])

        # Compute lightweight session-scoped accuracy (current sentence only)
        session_accuracy = _compute_session_accuracy(recording.session)

        # Update per-character proficiency
        if recording.target_character and recording.is_correct is not None:
            _update_character_proficiency(recording)

        # Push only current sentence score via WebSocket (lightweight)
        if recording.session.session_type == 'pair':
            _notify_pair_session(recording, session_accuracy)

        return {
            'status': 'success',
            'predicted': predicted_char,
            'confidence': confidence,
            'is_correct': recording.is_correct,
            'session_accuracy': session_accuracy,
        }

    except AudioRecording.DoesNotExist:
        return {'status': 'error', 'message': 'Recording not found'}
    except Exception as exc:
        try:
            recording = AudioRecording.objects.get(id=recording_id)
            recording.processing_status = 'failed'
            recording.error_message = str(exc)
            recording.save(update_fields=['processing_status', 'error_message'])
        except AudioRecording.DoesNotExist:
            pass
        raise self.retry(exc=exc, countdown=30)


def _compute_session_accuracy(session):
    """Only compute accuracy for the current session, not all history."""
    completed = AudioRecording.objects.filter(
        session=session, processing_status='completed'
    )
    total = completed.count()
    if total == 0:
        return 0.0
    correct = completed.filter(is_correct=True).count()
    return round(correct / total, 4)


def _update_character_proficiency(recording):
    """Update per-character proficiency based on this recording."""
    from accounts.models import CharacterProficiency
    proficiency, _ = CharacterProficiency.objects.get_or_create(
        user=recording.user,
        character=recording.target_character,
    )
    proficiency.record_attempt(recording.is_correct)


def _notify_pair_session(recording, session_accuracy):
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from pairing.models import PairSession

    pair_session = PairSession.objects.filter(
        practice_session=recording.session,
        status='active'
    ).first()

    if not pair_session:
        return

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'pair_{pair_session.id}',
        {
            'type': 'result_message',
            'sender_id': recording.user_id,
            'is_correct': recording.is_correct,
            'confidence': recording.confidence,
            'predicted_character': recording.predicted_character,
            'target_character': recording.target_character.character if recording.target_character else '',
            'session_accuracy': session_accuracy,
        }
    )
