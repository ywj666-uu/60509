from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, CharacterProficiency


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'proficiency_level', 'accuracy_rate', 'is_active')
    list_filter = ('proficiency_level', 'is_active')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_braille_grade', 'is_available_for_pairing')


@admin.register(CharacterProficiency)
class CharacterProficiencyAdmin(admin.ModelAdmin):
    list_display = ('user', 'character', 'accuracy', 'weighted_score', 'total_attempts', 'updated_at')
    list_filter = ('user',)
    readonly_fields = ('weighted_score', 'recent_attempts')
