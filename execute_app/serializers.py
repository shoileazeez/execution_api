from rest_framework import serializers

class TestCaseSerializer(serializers.Serializer):
    input_data = serializers.JSONField()
    expected_output = serializers.JSONField()

class CodeExecutionSerializer(serializers.Serializer):
    code = serializers.CharField()
    test_cases = TestCaseSerializer(many=True)  # Accept multiple test cases
