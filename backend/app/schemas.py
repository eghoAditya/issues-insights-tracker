from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime


class Role(str, Enum):
    ADMIN = "ADMIN"
    REPORTER = "REPORTER"
    MAINTAINER = "MAINTAINER"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Status(str, Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# --- Auth ---

class UserCreate(BaseModel):
    email: str
    password: str
    role: Role = Role.REPORTER


class TokenRequest(BaseModel):
    username: str
    password: str


# --- Issue ---

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: Severity = Severity.LOW


class IssueOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    severity: Severity
    status: Status
    reporter_id: int
    created_at: datetime

    class Config:
        orm_mode = True
