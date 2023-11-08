from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from constants import PaymentPeriod, EmploymentStatus, EmploymentType, PayCycle


class MyBaseModel(BaseModel):
    class Config:
        use_enum_values = True


class Address(MyBaseModel):
    city: Optional[str]
    line1: Optional[str]
    line2: Optional[str] = Field(default="not provided")
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]


class BasePay(MyBaseModel):
    amount: Optional[float] = 0.0
    period: PaymentPeriod = Field(default=PaymentPeriod.annual)
    currency: Optional[str]


class PlatformIds(MyBaseModel):
    employee_id: Optional[str]
    position_id: Optional[str]
    platform_user_id: Optional[str]


class Employee(MyBaseModel):
    id: str
    account: str
    address: Address

    first_name: str
    last_name: str
    full_name: str
    birth_date: Optional[str] = Field(default="not provided")
    email: Optional[str]
    phone_number: Optional[str]
    picture_url: Optional[str]
    employment_status: EmploymentStatus = Field(default=EmploymentStatus.active)
    employment_type: EmploymentType = Field(default=EmploymentType.full_time)
    job_title: Optional[str]
    ssn: Optional[str] = Field(default="not provided")
    marital_status: Optional[str] = Field(default="not provided")
    gender: Optional[str] = Field(default="not provided")
    hire_date: Optional[date]
    termination_date: Optional[str]
    termination_reason: Optional[str] = Field(default="not provided")
    employer: Optional[str]
    base_pay: BasePay
    pay_cycle: PayCycle = Field(default=PayCycle.weekly)
    platform_ids: PlatformIds
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    metadata: Optional[dict] = None
