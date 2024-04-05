from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import execptions, serializers, services


class ConverterViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
        if self.action == 'get_raw_data':
            return serializers.ConverterSerializer

    @action(methods=['post'], detail=False, url_path='raw-data')
    def get_raw_data(self, request):
        serializer = self.get_serializer_class()(data=self.request.data)
        if serializer.is_valid():
            try:
                result = services.ConverterService(
                    data=serializer.data,
                ).humanize_data()
            except execptions.ConverterException as e:
                return Response(e.error, status=status.HTTP_400_BAD_REQUEST)
            return Response(result, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
