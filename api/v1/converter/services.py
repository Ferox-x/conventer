import enum
import time
from dataclasses import dataclass
from typing import Any

from . import execptions


class EnumType(enum.StrEnum):
    CLOSED: str = 'closed'
    CLOSE: str = 'close'
    OPEN: str = 'open'


class EnumDay(enum.StrEnum):
    MONDAY: str = 'monday'
    TUESDAY: str = 'tuesday'
    WEDNESDAY: str = 'wednesday'
    THURSDAY: str = 'thursday'
    FRIDAY: str = 'friday'
    SATURDAY: str = 'saturday'
    SUNDAY: str = 'sunday'


@dataclass
class Timeslot:
    type: EnumType
    value: int


@dataclass
class TimeslotWithDay(Timeslot):
    day: EnumDay


class WeekIterableMixin:
    def __iter__(self):
        self.days = [
            ('monday', self.monday),
            ('tuesday', self.tuesday),
            ('wednesday', self.wednesday),
            ('thursday', self.thursday),
            ('friday', self.friday),
            ('saturday', self.saturday),
            ('sunday', self.sunday),
        ]
        self.current_day_index = 0
        self.current_timeslot_index = 0
        return self

    def __next__(self) -> tuple[str, Any | None]:
        if self.current_day_index >= len(self.days):
            raise StopIteration

        day_name, day_timeslots = self.days[self.current_day_index]
        if self.current_timeslot_index < len(day_timeslots):
            timeslot = day_timeslots[self.current_timeslot_index]
            self.current_timeslot_index += 1
            return day_name, timeslot
        elif self.current_timeslot_index == 0:
            self.current_day_index += 1
            self.current_timeslot_index = 0
            return day_name, None
        else:
            self.current_day_index += 1
            self.current_timeslot_index = 0
            return self.__next__()

    @classmethod
    def _prev_weekday(cls, day_name):
        day_name = day_name.lower()
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        current_day_index = weekdays.index(day_name)
        next_index = (current_day_index - 1) % 7
        return weekdays[next_index]


@dataclass
class WeekSchedule(WeekIterableMixin):
    monday: list[Timeslot]
    tuesday: list[Timeslot]
    wednesday: list[Timeslot]
    thursday: list[Timeslot]
    friday: list[Timeslot]
    saturday: list[Timeslot]
    sunday: list[Timeslot]

    def __init__(self, row_data: dict) -> None:
        super().__init__()
        for day_of_week, timeslots in row_data.items():
            reformatted_timeslots = []

            for timeslot in timeslots:
                timeslot = Timeslot(**timeslot)
                reformatted_timeslots.append(timeslot)

            setattr(self, day_of_week, reformatted_timeslots)


@dataclass
class WeekScheduleReformatted:
    schedule: list[TimeslotWithDay]


@dataclass
class WeekScheduleWithDay(WeekIterableMixin):
    monday: list[TimeslotWithDay]
    tuesday: list[TimeslotWithDay]
    wednesday: list[TimeslotWithDay]
    thursday: list[TimeslotWithDay]
    friday: list[TimeslotWithDay]
    saturday: list[TimeslotWithDay]
    sunday: list[TimeslotWithDay]

    def __init__(self, week_schedule: WeekScheduleReformatted) -> None:
        super().__init__()
        result = {}
        for timeslot in week_schedule.schedule:
            if timeslot.day not in result:
                if timeslot.type == EnumType.CLOSE:
                    prev_day = self._prev_weekday(timeslot.day)
                    result[prev_day].append(timeslot)
                    result[timeslot.day] = []
                else:
                    result[timeslot.day] = [timeslot]
                continue

            result[timeslot.day].append(timeslot)

        for day_of_week, timeslots in result.items():
            reformatted_timeslots = []

            for timeslot in timeslots:
                reformatted_timeslots.append(timeslot)

            setattr(self, day_of_week, reformatted_timeslots)

    def __next__(self) -> tuple[str, list[TimeslotWithDay]]:
        if self.current_day_index >= len(self.days):
            raise StopIteration

        day_name, day_timeslots = self.days[self.current_day_index]
        if self.current_timeslot_index < len(day_timeslots):
            self.current_day_index += 1
            return day_name, day_timeslots
        else:
            self.current_day_index += 1
            return self.__next__()


class ConverterService:
    def __init__(self, data: dict) -> None:
        self.data = data

    def humanize_data(self) -> dict[str:list]:
        cleaned_data = self._validate_and_clean_data(self.data)
        result = self._reformat_data(cleaned_data)
        return result

    @classmethod
    def _validate_and_clean_data(cls, data: dict) -> WeekSchedule:
        prev_timeslot_type = EnumType.CLOSE
        week_schedule = WeekSchedule(data)
        counter = 1
        for day, timeslot in week_schedule:
            # Проверяем правильную последовательность
            if not timeslot:
                continue
            elif not (
                prev_timeslot_type == EnumType.CLOSE and timeslot.type == EnumType.OPEN
            ) and not (prev_timeslot_type == EnumType.OPEN and timeslot.type == EnumType.CLOSE):
                raise execptions.ConverterException(f'Wrong timeslot type sequence: {day}')
            prev_timeslot_type = timeslot.type
            counter += 1
        return week_schedule

    @classmethod
    def _get_formatted_time(cls, seconds: int) -> str:
        return time.strftime('%I:%M %p', time.gmtime(seconds))

    def _reformat_data(self, week_schedule: WeekSchedule) -> dict[str:str]:
        week_schedule_reformatted = self._reformat_schedule_to_timeslot_with_day(
            week_schedule=week_schedule,
        )

        week_schedule_with_day = WeekScheduleWithDay(
            week_schedule=week_schedule_reformatted,
        )

        formatted_result = {}
        for day, timeslots in week_schedule_with_day:
            if timeslots[0].type == EnumType.CLOSED:
                formatted_result[day.capitalize()] = 'Closed'
                continue

            formatted_time = []
            for index in range(0, len(timeslots), 2):
                open_time = self._get_formatted_time(timeslots[index].value)
                close_time = self._get_formatted_time(timeslots[index + 1].value)
                formatted_time.append(f'{open_time} - {close_time}')
            formatted_result[day.capitalize()] = ', '.join(formatted_time)

        return formatted_result

    @classmethod
    def _reformat_schedule_to_timeslot_with_day(
        cls, week_schedule: WeekSchedule
    ) -> WeekScheduleReformatted:
        week_schedule_reformatted = WeekScheduleReformatted(schedule=[])
        for day, timeslot in week_schedule:
            if not timeslot:
                reformatted_timeslot = TimeslotWithDay(
                    value=-1,
                    type=EnumType.CLOSED,
                    day=EnumDay[day.upper()],
                )
            else:
                reformatted_timeslot = TimeslotWithDay(
                    value=timeslot.value,
                    type=timeslot.type,
                    day=EnumDay[day.upper()],
                )
            week_schedule_reformatted.schedule.append(reformatted_timeslot)
        return week_schedule_reformatted
