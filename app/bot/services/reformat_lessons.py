from typing import TYPE_CHECKING

from aiogram.utils.formatting import Bold, ExpandableBlockQuote, Text, Underline, as_list

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

    text = [line for line in text if line and line.strip()]  # ty:ignore[unresolved-attribute]
    return as_list(*text)


def reformat_lessons(
    lessons: collections.abc.Iterable[tuple[str, collections.abc.Iterable[Lesson]]],
    from_date: dt,
    locale: dict[str, str],
    group_name: str | None,
) -> Text:
    res: list[Text] = []
    for day, group in lessons:
        text = as_list(
            Bold(day),
            ExpandableBlockQuote(
                as_list(*[reformat_lesson(lesson) for lesson in group if not lesson.is_canceled], sep="\n\n"),
            ),
        )
        res.append(text)
    header = (
        as_list(locale["/schedule"], " ", Underline(group_name), ":\n", sep="")
        if group_name
        else Text(locale["no_header"], "\n")
    )
    if not res:
        return as_list(header, Text(locale["no_lessons"].format(date=from_date.strftime("%d-%m-%Y"))))
    return as_list(header, *res)
