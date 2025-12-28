from typing import Iterable

from aiogram.utils.formatting import Bold, ExpandableBlockQuote, Text, as_list

from app.bot.models import Lesson


def reformat_lesson(lesson: Lesson) -> Text:
    text = [
        lesson.time,
        lesson.course,
        lesson.type,
        lesson.subgroup,
        *lesson.rooms,
        *lesson.teachers,
    ]

    text = [line for line in text if line.strip()]
    res = as_list(*text)
    return res


def reformat_lessons(
    lessons: Iterable[tuple[str, Iterable[Lesson]]],
) -> Text:
    res: list[Text] = []
    for day, group in lessons:
        text = as_list(
            Bold(day),
            ExpandableBlockQuote(
                as_list(*[reformat_lesson(lesson) for lesson in group], sep="\n\n")
            ),
        )
        res.append(text)
    return as_list(*res)
