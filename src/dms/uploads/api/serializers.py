from rest_framework import serializers


class TUSDHookSerializer(serializers.Serializer):
    """
    Serializer for Tusd webhook requests
    see: https://tus.github.io/tusd/advanced-topics/hooks/#hook-requests-and-responses
    """

    # https://tus.github.io/tusd/advanced-topics/hooks/#list-of-available-hooks
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
