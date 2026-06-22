from rest_framework import serializers


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    image_base64 = serializers.CharField(required=False, allow_blank=True)
    history = serializers.ListField(
        child=serializers.DictField(), required=False, default=list
    )

    def validate(self, attrs):
        if not attrs.get('message') and not attrs.get('image_base64'):
            raise serializers.ValidationError("Either message or image_base64 must be provided.")
        return attrs


class RecommendationSerializer(serializers.Serializer):
    context = serializers.ChoiceField(
        choices=["home", "search", "post_order"],
        default="home",
        required=False,
    )
