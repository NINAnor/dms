from rest_framework import serializers


class TUSDHookSerializer(serializers.Serializer):
    Type = serializers.ChoiceField(
        choices=(
            "pre-create",
            "post-create",
            "post-receive",
            "pre-finish",
            "pre-terminate",
            "post-terminate",
            "post-finish",
        )
    )
    Event = serializers.JSONField()
