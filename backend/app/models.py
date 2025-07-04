from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# --- User roles ---
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    REPORTER = "REPORTER"
    MAINTAINER = "MAINTAINER"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.REPORTER, nullable=False)

    issues = relationship("Issue", back_populates="reporter")


# --- Issue severity and status enums ---
class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Status(str, enum.Enum):
    OPEN = "OPEN"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# --- Issue model ---
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_path = Column(String, nullable=True)

    severity = Column(Enum(Severity), default=Severity.LOW)
    status = Column(Enum(Status), default=Status.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="issues")
