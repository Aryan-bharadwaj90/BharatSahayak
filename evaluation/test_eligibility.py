from src.eligibility import check_eligibility

BASE_PROFILE = {
    "has_cultivable_land_in_family": True,
    "institutional_landholder": False,
    "constitutional_post_holder_in_family": False,
    "minister_or_legislator_or_mayor_or_district_panchayat_chair_in_family": False,
    "government_employee_or_retired_employee_excluding_group_d_mts": False,
    "monthly_pension_10000_or_more_excluding_group_d_mts": False,
    "paid_income_tax_in_last_assessment_year": False,
    "registered_practising_professional_doctor_engineer_lawyer_ca_architect": False
}

def test_empty_profile():
    result = check_eligibility("PM_KISAN", {})
    assert result["status"] == "unknown"

def test_satisfied_profile():
    result = check_eligibility("PM_KISAN", BASE_PROFILE)
    assert result["status"] == "satisfied"

def test_income_tax_exclusion():
    profile = BASE_PROFILE.copy()
    profile["paid_income_tax_in_last_assessment_year"] = True

    result = check_eligibility("PM_KISAN", profile)
    assert result["status"] == "not_satisfied"

if __name__ == "__main__":
    test_empty_profile()
    test_satisfied_profile()
    test_income_tax_exclusion()
    print("ALL 3 ELIGIBILITY TESTS PASSED!")