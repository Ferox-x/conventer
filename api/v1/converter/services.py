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

    def _reformat_data(self, old_data: dict) -> dict[str:list]:
        result = {}
        data = []
        closed_days = []
        for key, value in old_data.items():
            for timeslot in value:
                data.append({**timeslot, 'day': key})

            if not value:
                closed_days.append(key)

        for timeslot in data:
            if timeslot['day'] not in result:
                if timeslot['type'] == 'close':
                    prev_day = self._prev_weekday(timeslot['day'])
                    result[prev_day].append(timeslot)
                    result[timeslot['day']] = []
                else:
                    result[timeslot['day']] = [timeslot]
                continue

            result[timeslot['day']].append(timeslot)

        formatted_result = {}
        for day, timeslots in result.items():
            day: str
            formatted_time = []
            for index in range(0, len(timeslots), 2):
                open_time = self._get_formatted_time(timeslots[index]['value'])
                close_time = self._get_formatted_time(timeslots[index]['value'])
                formatted_time.append(f'{open_time} - {close_time}')
            formatted_result[day.capitalize()] = ', '.join(formatted_time)

        for closed_day in closed_days:
            formatted_result[closed_day.capitalize()] = 'Closed'
        return formatted_result

    def _prev_weekday(self, day_name):
        day_name = day_name.lower()
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_day_index = weekdays.index(day_name)
        next_index = (current_day_index - 1) % 7
        return weekdays[next_index]
