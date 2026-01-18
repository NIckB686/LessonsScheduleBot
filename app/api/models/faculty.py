from pydantic import BaseModel


class Faculty(BaseModel):
    code: str
    id: int
    name: str


class FacultyData(BaseModel):
    rows: list[Faculty]
    state: bool
