from django.utils.functional import cached_property
from rest_framework.test import APIClient


class AppTestClient:
    @cached_property
    def api_client(self) -> APIClient:
        client = APIClient()
        return client

    def get(self, *args, expected_status_code=200, **kwargs):
        result = self.api_client.get(*args, **kwargs)
        assert result.status_code == expected_status_code
        return result.json()

    def post(self, *args, expected_status_code=200, **kwargs):
        data = kwargs.pop('data', None)
        if data:
            kwargs['data'] = data
            kwargs['format'] = 'json'
        result = self.api_client.post(*args, **kwargs)
        assert result.status_code == expected_status_code
        return result.json()

    def put(self, *args, expected_status_code=200, **kwargs):
        data = kwargs.pop('data', None)
        if data:
            kwargs['data'] = data
            kwargs['format'] = 'json'
        result = self.api_client.put(*args, **kwargs)
        assert result.status_code == expected_status_code
        return result.json()

    def patch(self, *args, expected_status_code=200, **kwargs):
        data = kwargs.pop('data', None)
        if data:
            kwargs['data'] = data
            kwargs['format'] = 'json'
        result = self.api_client.patch(*args, **kwargs)
        assert result.status_code == expected_status_code
        return result.json()
