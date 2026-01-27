from typing import Any

from pydantic import BaseModel, Field, NonNegativeInt, computed_field, model_validator

days_of_week = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье",
}
subgroup_dict = {
    0: "",
    1: "1-группа",
    2: "2-группа",
}


class Lesson(BaseModel):
    changes: list[str] | dict[str, Any] = Field(exclude=True)
    course_unparsed: dict = Field(alias="course", exclude=True)
    divisions_unparsed: list[dict] = Field(alias="divisions", exclude=True)
    events: list
    groups_unparsed: list[dict] = Field(alias="groups", exclude=True)
    id: int = Field(exclude=True)
    individual_plan: int | None = Field(default=None, alias="individualPlan", exclude=True)
    is_canceled: bool = Field(alias="isCanceled", exclude=True)
    is_moved: bool = Field(alias="isMoved", exclude=True)
    rooms_unparsed: list[dict] = Field(alias="rooms")
    student_amount: int | None = Field(default=None, alias="studentAmount", exclude=True)
    subgroup_unparsed: int | str = Field(alias="subgroup", exclude=True)
    teachers_unparsed: list[dict] = Field(alias="teachers", exclude=True)
    time_chunks: list[NonNegativeInt] = Field(alias="timeChunks", exclude=True)
    type: str
    version_id: NonNegativeInt | None = Field(default=None, alias="versionId", exclude=True)
    week_day_number: int = Field(alias="weekDayNumber", exclude=True)
    time: str | None = None
    date: str | None = Field(default=None)

    @computed_field
    def groups(self) -> list[str]:
        return [group["code"] for group in self.groups_unparsed]

    @computed_field
    def divisions(self) -> list[str]:
        return [division["name"] for division in self.divisions_unparsed]

    @computed_field
    def course(self) -> str:
        return self.course_unparsed["name"]

    @computed_field
    def week_day(self) -> str:
        return days_of_week[self.week_day_number]

    @computed_field
    def rooms(self) -> list[str]:
        if isinstance(self.changes, dict):
            rooms = self.changes.get("rooms", self.rooms_unparsed)
        else:
            rooms = self.rooms_unparsed
        return [room["number"] for room in rooms]

    @computed_field
    def teachers(self) -> list[str]:
        if isinstance(self.changes, dict):
            teachers = self.changes.get("teachers", self.teachers_unparsed)
        else:
            teachers = self.teachers_unparsed
        return [" ".join((teacher["lastName"], teacher["firstName"], teacher["patronymic"])) for teacher in teachers]

    @computed_field
    def subgroup(self) -> str:
        return subgroup_dict[self.subgroup_unparsed]


class OrganizationData(BaseModel):
    id: int = Field(exclude=True)
    lessons: list[Lesson]
    lessons_time_chunks: list[str] = Field(alias="lessonsTimeChunks", exclude=True)
    name: str = Field(exclude=True)

    @model_validator(mode="after")
    def populate_time_strings(self):
        for lesson in self.lessons:
            time_strs = [
                self.lessons_time_chunks[i] for i in lesson.time_chunks if 0 <= i < len(self.lessons_time_chunks)
            ]
            lesson.time = "".join(
                (time_strs[0].split("-")[0], "-", time_strs[-1].split("-")[-1]),
            )

        return self


class Day(BaseModel):
    date: str
    is_study_day: bool = Field(alias="isStudyDay")
    week_day_number: int = Field(alias="weekDayNumber")


class Week(BaseModel):
    days: list[Day]
    number: int
    type: str


class _Rows(BaseModel):
    organizations: list[OrganizationData]
    week: dict[str, Week]

    @model_validator(mode="after")
    def populate_days_of_week(self):
        for org in self.organizations:
            if org.lessons:
                for lesson in org.lessons:
                    lesson.date = self.week["weekTashkent"].days[lesson.week_day_number].date
        return self


class LessonsData(BaseModel):
    rows: _Rows
    state: bool
