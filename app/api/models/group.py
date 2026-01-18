from datetime import date, datetime

from pydantic import BaseModel, Field, PositiveInt, field_validator


class Group(BaseModel):
    code: str
    date_begin: date = Field(alias="dateBegin")
    date_end: date = Field(alias="dateEnd")
    faculty_id: PositiveInt = Field(alias="facultyId")
    has_specializations: bool = Field(alias="hasSpecializations")
    id: PositiveInt
    qualification_type: PositiveInt = Field(alias="qualificationType")

    @field_validator("date_begin", "date_end", mode="before")
    @classmethod
    def parse_date(cls, value: str) -> date:
        return datetime.strptime(value, "%d-%m-%Y").date()


class GroupData(BaseModel):
    rows: list[Group]
    state: bool
