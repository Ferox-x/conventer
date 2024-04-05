import pytest

from api.v1.converter.execptions import ConverterException
from api.v1.converter.services import ConverterService


def test_get_raw_data_valid(api):
    url = '/api/v1/converter/raw-data/'
    valid_data = {
        'monday': [],
        'tuesday': [{'type': 'open', 'value': 36000}, {'type': 'close', 'value': 64800}],
        'wednesday': [],
        'thursday': [
            {'type': 'open', 'value': 36000},
            {'type': 'close', 'value': 39600},
            {'type': 'open', 'value': 43200},
            {'type': 'close', 'value': 46800},
        ],
        'friday': [{'type': 'open', 'value': 36000}],
        'saturday': [{'type': 'close', 'value': 3600}, {'type': 'open', 'value': 36000}],
        'sunday': [
            {'type': 'close', 'value': 3600},
            {'type': 'open', 'value': 43200},
            {'type': 'close', 'value': 75600},
        ],
    }

    response = api.post(url, data=valid_data)
    assert {
        'Tuesday': '10:00 AM - 10:00 AM',
        'Thursday': '10:00 AM - 10:00 AM, 12:00 PM - 12:00 PM',
        'Friday': '10:00 AM - 10:00 AM',
        'Saturday': '10:00 AM - 10:00 AM',
        'Sunday': '12:00 PM - 12:00 PM',
        'Monday': 'Closed',
        'Wednesday': 'Closed',
    } == response


def test_get_raw_data_invalid(api):
    url = '/api/v1/converter/raw-data/'
    invalid_data = {
        'monday': [{'type': 'open', 'value': 36000}, {'type': 'open', 'value': 64800}],
        'tuesday': [],
        'wednesday': [],
        'thursday': [{'type': 'open', 'value': 36000}, {'type': 'close', 'value': 64800}],
        'friday': [],
        'saturday': [{'type': 'open', 'value': 36000}, {'type': 'close', 'value': 64800}],
        'sunday': [{'type': 'open', 'value': 36000}, {'type': 'close', 'value': 64800}],
    }

    response = api.post(url, data=invalid_data, expected_status_code=400)
    assert {'error': 'Wrong timeslot type sequence: monday'} == response


class TestConverterService:
    @pytest.fixture
    def sample_data(self):
        return {
            'monday': [],
            'tuesday': [{'type': 'open', 'value': 36000}, {'type': 'close', 'value': 64800}],
            'wednesday': [],
            'thursday': [
                {'type': 'open', 'value': 36000},
                {'type': 'close', 'value': 39600},
                {'type': 'open', 'value': 43200},
                {'type': 'close', 'value': 46800},
            ],
            'friday': [{'type': 'open', 'value': 36000}],
            'saturday': [{'type': 'close', 'value': 3600}, {'type': 'open', 'value': 36000}],
            'sunday': [
                {'type': 'close', 'value': 3600},
                {'type': 'open', 'value': 43200},
                {'type': 'close', 'value': 75600},
            ],
        }

    def test_init(self, sample_data):
        service = ConverterService(sample_data)
        assert service.data == sample_data

    def test_get_formatted_time(self):
        service = ConverterService({})
        assert service._get_formatted_time(36000) == '10:00 AM'

    def test_reformat_data_closed(self):
        service = ConverterService({})
        data = {'monday': [], 'tuesday': [], 'wednesday': []}
        result = service._reformat_data(data)
        assert result == {'Monday': 'Closed', 'Tuesday': 'Closed', 'Wednesday': 'Closed'}

    def test_reformat_data_open(self):
        service = ConverterService({})
        data = {'monday': [{'type': 'open', 'value': 36000}]}
        result = service._reformat_data(data)
        assert result == {'Monday': '10:00 AM - 10:00 AM'}

    def test_humanize_data(self, sample_data):
        service = ConverterService(sample_data)
        result = service.humanize_data()
        expected_result = {
            'Tuesday': '10:00 AM - 10:00 AM',
            'Thursday': '10:00 AM - 10:00 AM, 12:00 PM - 12:00 PM',
            'Friday': '10:00 AM - 10:00 AM',
            'Saturday': '10:00 AM - 10:00 AM',
            'Sunday': '12:00 PM - 12:00 PM',
            'Monday': 'Closed',
            'Wednesday': 'Closed',
        }
        assert result == expected_result

    def test_validate_and_clean_data(self):
        data = {'monday': [{'type': 'open', 'value': 36000}, {'type': 'open', 'value': 64800}]}
        service = ConverterService(data)
        with pytest.raises(ConverterException):
            service._validate_and_clean_data(data)
