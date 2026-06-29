from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsPaciente, IsPsicologa
from apps.messaging.selectors import all_conversations, messages_for
from apps.messaging.services import ConversationService, MessageService
from apps.patients.services import PatientService

from .serializers import ConversationSerializer, MessageSerializer


class MyConversationView(APIView):
    """Retorna (ou cria) a conversa do paciente logado.

    Usado pelo frontend para obter o conversation_id antes de abrir o WebSocket.
    """

    permission_classes = [IsPaciente]

    def get(self, request):
        patient = PatientService.ensure_profile(request.user)
        conversation = ConversationService.get_or_create(patient)
        return Response(ConversationSerializer(conversation, context={"request": request}).data)


class ConversationListView(generics.ListAPIView):
    """Lista todas as conversas — acesso da psicóloga."""

    serializer_class = ConversationSerializer
    permission_classes = [IsPsicologa]

    def get_queryset(self):
        return all_conversations()


class MessageListCreateView(APIView):
    """Histórico e envio de mensagens numa conversa.

    - Psicóloga acessa por ?patient=<patient_id>
    - Paciente acessa a própria conversa diretamente
    """

    def get_permissions(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and user.is_psicologa:
            return [IsPsicologa()]
        return [IsPaciente()]

    def _get_conversation(self, request):
        if request.user.is_psicologa:
            from apps.patients.models import Patient
            patient_id = request.query_params.get("patient")
            if not patient_id:
                return None, Response(
                    {"detail": "Parâmetro ?patient= obrigatório."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                patient = Patient.objects.get(pk=patient_id)
            except Patient.DoesNotExist:
                return None, Response(
                    {"detail": "Paciente não encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            patient = PatientService.ensure_profile(request.user)

        conversation = ConversationService.get_or_create(patient)
        return conversation, None

    def get(self, request):
        conversation, err = self._get_conversation(request)
        if err:
            return err
        MessageService.mark_as_read(conversation, request.user)
        msgs = messages_for(conversation)
        return Response(MessageSerializer(msgs, many=True).data)

    def post(self, request):
        conversation, err = self._get_conversation(request)
        if err:
            return err
        conteudo = request.data.get("conteudo", "").strip()
        if not conteudo:
            return Response(
                {"detail": "Mensagem não pode ser vazia."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        msg = MessageService.create(conversation, request.user, conteudo)
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)
