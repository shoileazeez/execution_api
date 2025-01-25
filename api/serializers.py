from rest_framework import serializers


class CodeExecutionSerializer(serializers.Serializer):
    language = serializers.ChoiceField(
        choices=[("python", "Python"), ("javascript", "JavaScript")], required=True
    )
    code = serializers.CharField(required=True)
    input_data = serializers.CharField(required=False, default="")

    def validate(self, data):
        if not data["code"].strip():
            raise serializers.ValidationError(
                "Code cannot be empty or contain only whitespace."
            )
        return data
    def validate_code(self, value):
        if len(value) > 1000:  # Example length limit
            raise serializers.ValidationError("Code is too long.")
        return value