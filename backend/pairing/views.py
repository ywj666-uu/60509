from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from .models import PairSession, PairMessage
from .serializers import PairSessionSerializer, PairMessageSerializer, AvailablePartnerSerializer
from braille.models import PracticeSession

User = get_user_model()


class AvailablePartnersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        from accounts.models import UserProfile
        available_profiles = UserProfile.objects.filter(
            is_available_for_pairing=True
        ).exclude(user=request.user)
        users = User.objects.filter(
            id__in=available_profiles.values_list('user_id', flat=True)
        )
        serializer = AvailablePartnerSerializer(users, many=True)
        return Response(serializer.data)


class PairSessionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        sessions = PairSession.objects.filter(
            Q(initiator=request.user) | Q(partner=request.user)
        )
        serializer = PairSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    def post(self, request):
        partner_id = request.data.get('partner_id')
        sentence_id = request.data.get('sentence_id')

        if not partner_id:
            return Response({'error': '请选择练习伙伴'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            partner = User.objects.get(id=partner_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # Create practice sessions for both users
        practice_session = PracticeSession.objects.create(
            user=request.user,
            session_type='pair',
        )

        pair_session = PairSession.objects.create(
            initiator=request.user,
            partner=partner,
            practice_session=practice_session,
            status='active',
        )

        if sentence_id:
            from braille.models import BrailleSentence
            try:
                sentence = BrailleSentence.objects.get(id=sentence_id)
                pair_session.sentence = sentence
                pair_session.save()
            except BrailleSentence.DoesNotExist:
                pass

        serializer = PairSessionSerializer(pair_session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PairSessionDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            session = PairSession.objects.get(
                Q(initiator=request.user) | Q(partner=request.user),
                id=pk
            )
        except PairSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = PairSessionSerializer(session).data
        messages = PairMessage.objects.filter(pair_session=session)
        data['messages'] = PairMessageSerializer(messages, many=True).data
        return Response(data)

    def patch(self, request, pk):
        try:
            session = PairSession.objects.get(
                Q(initiator=request.user) | Q(partner=request.user),
                id=pk
            )
        except PairSession.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status == 'completed':
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()

        return Response(PairSessionSerializer(session).data)
