from enum import Enum


class PaymentPeriod(str, Enum):
    hourly = "hourly"
    weekly = "weekly"
    biweekly = "biweekly"
    semimonthly = "semimonthly"
    monthly = "monthly"
    annual = "annual"
    salary = "salary"


class EmploymentStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    terminated = "terminated"
    retired = "retired"


class EmploymentType(str, Enum):
    full_time = "full-time"
    part_time = "part-time"
    contractor = "contractor"
    seasonal = "seasonal"
    temporary = "temporary"
    other = "other"


class PayCycle(str, Enum):
    daily = "daily"
    weekly = "weekly"
    biweekly = "biweekly"
    semimonthly = "semimonthly"
    monthly = "monthly"
    quarterly = "quarterly"
