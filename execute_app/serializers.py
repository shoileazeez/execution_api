from rest_framework import serializers

class CodeExecutionSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False)
    input_data = serializers.JSONField(required=False, default={})
    expected_output = serializers.JSONField(required=False, allow_null=True)
    language = serializers.ChoiceField(choices=['python', 'javascript', 'java'], default='python')
