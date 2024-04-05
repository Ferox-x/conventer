from rest_framework import serializers


class ConverterTimeCellSerializer(serializers.Serializer):
    type = serializers.CharField()
    value = serializers.IntegerField()

    def validate_type(self, value):
        if value not in ['open', 'close']:
            raise serializers.ValidationError('Unsupported type')
        return value


class ConverterSerializer(serializers.Serializer):
    monday = ConverterTimeCellSerializer(many=True, allow_null=True)
    tuesday = ConverterTimeCellSerializer(many=True, allow_null=True)
    wednesday = ConverterTimeCellSerializer(many=True, allow_null=True)
    thursday = ConverterTimeCellSerializer(many=True, allow_null=True)
    friday = ConverterTimeCellSerializer(many=True, allow_null=True)
    saturday = ConverterTimeCellSerializer(many=True, allow_null=True)
    sunday = ConverterTimeCellSerializer(many=True, allow_null=True)
