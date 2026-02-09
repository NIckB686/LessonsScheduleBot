from typing import TYPE_CHECKING

from aiogram.utils.formatting import Bold, ExpandableBlockQuote, Text, as_list

if TYPE_CHECKING:
    import collections.abc
    from datetime import date as dt

    from app.api.models import Lesson


def reformat_lesson(lesson: Lesson) -> Text:
    text = [
        lesson.time,
        lesson.course,
        lesson.type,
        lesson.subgroup,
        *lesson.rooms,  # ty:ignore[not-iterable]
        *lesson.teachers,  # ty:ignore[not-iterable]
    ]

    text = [line for line in text if line and line.strip()]
    return as_list(*text)


def reformat_lessons(
    lessons: collections.abc.Iterable[tuple[str, collections.abc.Iterable[Lesson]]],
    date: dt,
) -> Text:
    res: list[Text] = []
    for day, group in lessons:
        text = as_list(
            Bold(day),
            ExpandableBlockQuote(
                as_list(*[reformat_lesson(lesson) for lesson in group], sep="\n\n"),
            ),
        )
        res.append(text)
    if not res:
        return as_list(Text(f"Уроков на этой неделе нет: {date.strftime('%d-%m-%Y')}"))
    return as_list(*res)
