from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class User(AbstractUser):
    proficiency_level = models.IntegerField(default=1)
    total_practice_minutes = models.FloatField(default=0.0)
    accuracy_rate = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    preferred_braille_grade = models.IntegerField(default=1)
    is_available_for_pairing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f'{self.user.username} profile'


class CharacterProficiency(models.Model):
    """
    Per-character proficiency tracking.
    Uses a sliding window of the last 10 attempts with exponential decay on errors.
    Each error reduces the weighted score more heavily than a correct answer raises it.
    """
    WINDOW_SIZE = 10
    ERROR_DECAY_WEIGHT = 0.7  # errors count 1.0, correct answers count 0.7 in weight

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='char_proficiencies')
    character = models.ForeignKey(
        'braille.BrailleCharacter', on_delete=models.CASCADE, related_name='proficiencies'
    )
    # Stores last N attempts as JSON: [true, false, true, ...]
    recent_attempts = models.TextField(default='[]')
    accuracy = models.FloatField(default=0.0)
    weighted_score = models.FloatField(default=0.0)
    total_attempts = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'character_proficiency'
        unique_together = ('user', 'character')
        ordering = ['character__character']

    def __str__(self):
        return f'{self.user.username} - {self.character.character}: {self.accuracy:.0%}'

    def record_attempt(self, is_correct):
        """Record a new attempt and recalculate proficiency with decay."""
        attempts = json.loads(self.recent_attempts)
        attempts.append(is_correct)

        # Keep only last WINDOW_SIZE attempts
        if len(attempts) > self.WINDOW_SIZE:
            attempts = attempts[-self.WINDOW_SIZE:]

        self.recent_attempts = json.dumps(attempts)
        self.total_attempts += 1

        # Weighted scoring: more recent attempts weigh more,
        # errors apply a stronger penalty (decay weight)
        self.weighted_score = self._calculate_weighted_score(attempts)
        self.accuracy = self.weighted_score
        self.save()

    def _calculate_weighted_score(self, attempts):
        """
        Calculate weighted accuracy over the sliding window.
        - Each position has a recency weight (newer = higher)
        - Errors get an additional penalty multiplier (each error drags score down harder)
        """
        if not attempts:
            return 0.0

        n = len(attempts)
        total_weight = 0.0
        weighted_correct = 0.0

        for i, correct in enumerate(attempts):
            # Recency weight: linearly increasing (oldest=1, newest=n)
            recency = (i + 1) / n

            if correct:
                # Correct: normal recency weight
                weighted_correct += recency
                total_weight += recency
            else:
                # Error: heavier weight (penalizes more)
                penalty_weight = recency / self.ERROR_DECAY_WEIGHT
                total_weight += penalty_weight
                # weighted_correct += 0 (error contributes nothing positive)

        if total_weight == 0:
            return 0.0

        return round(weighted_correct / total_weight, 4)
