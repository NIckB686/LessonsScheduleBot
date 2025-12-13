from typing import Any, Generator, Iterable

from aiogram.utils.formatting import Bold, ExpandableBlockQuote, Text, as_list

from app.models import Lesson


def reformat_lesson(lesson: Lesson) -> Text:
    text = [
        lesson.time,
        lesson.course,
        lesson.type,
        lesson.subgroup,
        *lesson.rooms,
        *lesson.teachers,
    ]

    res = ExpandableBlockQuote(
        "\n".join(line for line in text if line.strip()),
    )
    return res


def reformat_lessons(
    lessons: Iterable[tuple[str, Iterable[Lesson]]],
) -> Generator[Text, Any, None]:
    for day, group in lessons:
        text = as_list(
            Bold(day),
            *[reformat_lesson(lesson) for lesson in group],
            # sep="\n\n",
        )
        yield text
