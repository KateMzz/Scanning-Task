import json
from constants import PaymentPeriod, EmploymentStatus, EmploymentType, PayCycle
from typing import Dict


async def extract_data(
    address_response_json: json, profile_response_json: json, profile_id: str
) -> Dict:
    """forming the data from both APIs to the actual output"""
    contact_main_info = address_response_json["freelancer"]
    address_info = contact_main_info["address"]
    profile_info = profile_response_json["profile"]
    termination_date = profile_info["employmentHistory"][0]["endDate"]
    if termination_date:
        employment_status = EmploymentStatus.terminated
    else:
        employment_status = EmploymentStatus.active

    data = {
        "id": contact_main_info["nid"],
        "account": profile_id,
        "address": {
            "city": address_info["city"],
            "state": address_info["state"],
            "country": address_info["country"],
            "line1": address_info["street"],
            "postal_code": address_info["zip"],
        },
        "first_name": contact_main_info["firstName"],
        "last_name": contact_main_info["lastName"],
        "full_name": profile_info["profile"]["name"],
        "email": contact_main_info["email"]["address"],
        "phone_number": contact_main_info["phone"],
        "picture_url": profile_info["profile"]["portrait"]["portrait"],
        "employment_status": employment_status,
        "employment_type": EmploymentType.full_time,
        "job_title": profile_info["employmentHistory"][0]["jobTitle"],
        "hire_date": profile_info["employmentHistory"][0]["startDate"],
        "termination_date": termination_date,
        "employer": profile_info["employmentHistory"][0]["companyName"],
        "base_pay": {
            "amount": profile_info["stats"]["totalEarnings"],
            "period": PaymentPeriod.annual,
            "currency": profile_info["stats"]["hourlyRate"]["currencyCode"],
        },
        "pay_cycle": PayCycle.weekly,
        "platform_ids": {
            "employee_id": profile_info["identity"]["uid"],
            "position_id": profile_info["employmentHistory"][0]["uid"],
            "platform_user_id": profile_info["identity"]["ciphertext"],
        },
        "created_at": profile_response_json["person"]["creationDate"],
        "updated_at": profile_response_json["person"]["updatedOn"],
    }
    return data
