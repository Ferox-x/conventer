import time

from . import execptions, serializers


class ConverterService:
    def __init__(self, data: serializers.ConverterSerializer.data) -> None:
        self.data = data

    def humanize_data(self) -> dict[str:list]:
        cleaned_data = self._validate_and_clean_data(self.data)
        result = self._reformat_data(cleaned_data)
        return result

    def _validate_and_clean_data(self, data: dict) -> dict:
        prev_timeslot_type = 'close'

        for day, timeslots in self.data.items():
            day: str
            timeslots: list[dict]

            for timeslot in timeslots:
                timeslot_type = timeslot['type']
                # Проверяем правильную последовательность
                if prev_timeslot_type == 'close' and timeslot_type == 'open':
                    pass
                elif prev_timeslot_type == 'open' and timeslot_type == 'close':
                    pass
                else:
                    raise execptions.ConverterException(f'Wrong timeslot type sequence: {day}')
                prev_timeslot_type = timeslot_type
        return data

    def _get_formatted_time(self, seconds: int) -> str:
        return time.strftime('%I:%M %p', time.gmtime(seconds))

    def _reformat_data(self, data: dict) -> dict[str:list]:
        result = {}
        for day, timings in data.items():
            if not timings:
                result[day.capitalize()] = 'Closed'
            else:
                open_time = self._get_formatted_time(timings[0]['value'])
                close_time = self._get_formatted_time(timings[-1]['value'])
                result[day.capitalize()] = f'{open_time} - {close_time}'
        return result
