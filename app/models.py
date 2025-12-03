from dataclasses import dataclass

days_of_week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}


@dataclass(frozen=True, slots=True)
class Lesson:
    course: str
    groups: tuple
    is_canceled: bool
    is_moved: bool
    rooms: tuple
    teachers: tuple
    type: str
    subgroup: str
    week_day_number: int
    time: str

    def __str__(self):
        return f"""
{self.time}
{self.course}
{self.type} {'\n' + self.subgroup if self.subgroup else ''}
{'\n'.join(self.rooms)}
{'\n'.join(self.teachers)}
"""
