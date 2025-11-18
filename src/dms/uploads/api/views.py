import logging

from django.utils.timezone import now
from procrastinate.contrib.django import app
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import HookRequest
from .serializers import TUSDHookSerializer


class UploadWebhookAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = TUSDHookSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            action_type = serializer.validated_data.get("Type")
            event = serializer.validated_data.get("Event")

            self.hook = HookRequest.objects.create(
                type=action_type,
                event=event,
                id=event.get("ID"),
                user=self.request.user,
            )

            return getattr(self, f"{action_type.replace('-', '_')}")()
        except AttributeError:
            logging.error(f"{serializer.validated_data('Type')} event type")
            self.hook.completed_at = now()
            self.hook.save()
            return {
                "HTTPResponse": {
                    "StatusCode": 400,
                    "Header": {"Content-Type": "application/json"},
                },
                "RejectUpload": True,
                "StopUpload": True,
            }

    def post_finish(self):
        self.process()
        return Response(data={"status": "ok"})

    def process(self):
        app.configure_task(name="dms.uploads.tasks.process_upload").defer(
            upload_id=str(self.hook.id)
        )

    def pre_create(self):
        self.hook.completed_at = now()
        self.hook.save()

        if self.request.user.is_authenticated:
            return Response(data={})

        return Response(
            data={
                "HTTPResponse": {
                    "StatusCode": 401,
                    "Body": '{"message":"User not authenticated"}',
                    "Header": {"Content-Type": "application/json"},
                },
                "RejectUpload": not self.request.user.is_authenticated,
            }
        )
