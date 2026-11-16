
import json
from pathlib import Path

path = Path("data/schemes.json")

CONTENT = {
    "PM_KISAN": {
        "description": "Central Sector income-support scheme providing financial assistance to eligible landholding farmer families. State and UT authorities verify beneficiary records.",
        "benefits": [
            "Eligible farmer families receive Rs. 6,000 per year.",
            "The amount is paid in three equal instalments of Rs. 2,000 through Direct Benefit Transfer to the beneficiary bank account.",
            "eKYC is mandatory for registered beneficiaries."
        ],
        "eligibility": [
            "The scheme covers eligible landholding farmer families, defined as husband, wife and minor children.",
            "Institutional landholders and specified higher-income or office-holder categories are excluded.",
            "State or UT land records and official beneficiary verification determine entitlement."
        ],
        "documents": [
            "Aadhaar details for identity and eKYC.",
            "Bank account details for DBT.",
            "Landholding and farmer records as required by the State or UT.",
            "Additional documents requested during official verification."
        ],
        "application_process": [
            "Use the New Farmer Registration facility on the PM-KISAN portal or contact the designated State or UT officials or a CSC.",
            "Complete the required identity and eKYC process.",
            "Check application and payment status using Know Your Status on the official portal."
        ]
    },
    "AYUSHMAN_BHARAT_PMJAY": {
        "description": "Government-funded health assurance scheme providing cashless secondary and tertiary hospitalisation cover to eligible beneficiary families at empanelled hospitals.",
        "benefits": [
            "Health cover up to Rs. 5 lakh per eligible family per year.",
            "Cashless treatment at empanelled public and private hospitals.",
            "Covered packages can include hospitalisation, applicable day-care procedures, medicines and pre- and post-hospitalisation expenses under scheme rules.",
            "Benefits are portable across participating States and Union Territories."
        ],
        "eligibility": [
            "Entitlement is based on the official beneficiary database and applicable State-specific expansion rules.",
            "A person's eligibility cannot be confirmed from income, occupation, caste or age alone.",
            "Check beneficiary status through the official NHA beneficiary portal or an authorised channel."
        ],
        "documents": [
            "Ayushman card or beneficiary identification details, where available.",
            "Aadhaar or another accepted identity document for verification.",
            "Ration card or family identification details if requested by the State or verification centre."
        ],
        "application_process": [
            "Check beneficiary status at https://beneficiary.nha.gov.in/ or through an authorised Ayushman Mitra or Common Service Centre.",
            "Complete identity and family verification if listed as an eligible beneficiary.",
            "Use an empanelled hospital and contact its Ayushman Mitra desk before treatment."
        ]
    },
    "PMAY_URBAN": {
        "description": "PMAY-Urban 2.0 supports eligible urban families to construct, purchase or rent affordable housing through four programme verticals.",
        
"benefits": [
    "BLC: Eligible EWS families constructing a new pucca house on their own land can receive assistance up to Rs. 2.5 lakh, subject to State and scheme conditions.",
    "AHP: Eligible EWS beneficiaries purchasing an allotted affordable house in an approved project can receive assistance up to Rs. 2.5 lakh per house, subject to applicable conditions.",
    "ARH: Provides affordable rental housing for eligible EWS and LIG households, including urban migrants, working women and industrial workers. This is rental housing support, not an individual house-purchase grant.",
    "ISS: Eligible EWS, LIG and MIG home-loan borrowers may receive interest subsidy up to Rs. 1.80 lakh, subject to scheme conditions.",
    "Under ISS, the maximum eligible housing loan value is Rs. 25 lakh and the maximum house value is Rs. 35 lakh.",
    "Under BLC, eligible houses generally have a carpet area between 30 and 45 square metres, subject to guidelines."
],
        "eligibility": [
    "The household must live in an urban area and fall within the applicable income category: EWS up to Rs. 3 lakh annual household income, LIG above Rs. 3 lakh and up to Rs. 6 lakh, or MIG above Rs. 6 lakh and up to Rs. 9 lakh.",
    "The beneficiary family must not own a pucca house anywhere in India, subject to applicable scheme guidelines.",
    "The beneficiary or family must not have been allotted a house under a Central Government, State/UT Government or Local Self Government housing scheme during the preceding 20 years, in urban or rural areas.",
    "All eligible family members must provide the required Aadhaar or Aadhaar Virtual ID details.",
    "Final eligibility depends on the selected vertical and verification by the State or Urban Local Body."
        ],
        "documents": [
            "Aadhaar details of the applicant and family members.",
            "Applicant bank account details.",
            "Income proof or income certificate as required.",
            "Eligibility undertaking in the prescribed format.",
            "Land ownership documents for Beneficiary Led Construction applications.",
            "Caste or category certificate where applicable."
        ],
        "application_process": [
            "Apply through the PMAY-U 2.0 Unified Web Portal, a Common Service Centre or the concerned Urban Local Body or Municipality.",
            "Select the applicable scheme vertical and complete the eligibility assessment.",
            "Upload or submit the required documents and undertaking.",
            "Wait for State, ULB and scheme-authority verification and sanction."
        ]
    },
    "PMAY_GRAMIN": {
        "description": "Rural housing assistance programme for eligible rural households identified through the prescribed deprivation, housing and verification process.",
        "benefits": [
            "Eligible beneficiaries may receive Rs. 12,000 for toilet construction through convergence with Swachh Bharat Mission-Gramin.",
            "Beneficiaries may receive 90/95 days of unskilled labour wages through MGNREGS, subject to applicable rules.",
            "Eligible beneficiaries may be facilitated to access institutional loan support under applicable programme provisions."
        ],
        "eligibility": [
            "Beneficiaries are identified through the prescribed SECC and Awaas+ lists and programme exclusion checks.",
            "Rural residence or low income alone does not establish eligibility.",
            "The final beneficiary list and verification by the Gram Sabha and competent authorities are decisive."
        ],
        "documents": [
            "Aadhaar or other accepted identity details.",
            "Bank or post-office account details.",
            "Household and residence details.",
            "Land or site details and other records requested during local verification."
        ],
        "application_process": [
            "Check the beneficiary list through the PMAY-G official portal or Gram Panchayat and Block Development Office.",
            "Contact the Gram Panchayat or Block office if household details require verification.",
            "Follow the official beneficiary verification and construction-stage process."
        ]
    },
    "PMJDY": {
        "description": "National financial-inclusion mission enabling unbanked individuals to access basic banking, savings, remittance and eligible financial services.",
        "benefits": [
            "A basic savings bank deposit account can be opened with no minimum balance requirement.",
            "The account earns interest according to the bank's applicable rate.",
            "RuPay debit card is provided to eligible account holders.",
            "Eligible account holders may receive accident insurance cover linked to the RuPay card; coverage depends on account-opening date and applicable conditions.",
            "Eligible account holders may access an overdraft facility up to Rs. 10,000, subject to bank assessment and scheme conditions.",
            "The account can be used for Direct Benefit Transfer."
        ],
        "eligibility": [
            "Individuals who do not have a bank account can approach a participating bank branch or Bank Mitra.",
            "Applicants must complete the bank's identity and KYC requirements.",
            "Overdraft and insurance benefits have additional eligibility and usage conditions."
        ],
        "documents": [
            "Aadhaar number or another officially accepted identity document.",
            "Address details or an accepted address document, as required by the bank.",
            "A photograph and KYC information.",
            "Where applicable, a small account may be opened under the permitted simplified KYC procedure."
        ],
        "application_process": [
            "Visit a participating bank branch or Bank Mitra outlet.",
            "Request a PMJDY basic savings bank deposit account.",
            "Complete the account-opening and KYC process.",
            "Ask the bank to explain RuPay card, overdraft and insurance conditions."
        ]
    },
    "ATAL_PENSION_YOJANA": {
        "description": "Voluntary, contribution-based pension scheme administered by PFRDA for eligible Indian citizens seeking guaranteed minimum monthly pension after age 60.",
        "benefits": [
            "Subscribers choose a guaranteed minimum monthly pension of Rs. 1,000, Rs. 2,000, Rs. 3,000, Rs. 4,000 or Rs. 5,000 after age 60.",
            "The spouse is entitled to the same pension after the subscriber's death, subject to scheme rules.",
            "After the death of both subscriber and spouse, the accumulated pension wealth is payable to the nominee under scheme rules."
        ],
        "eligibility": [
            "Indian citizens aged 18 to 40 years with a savings bank or post-office savings account may join.",
            "A person who is or has been an income-tax payer is not eligible to open a new APY account from 1 October 2022.",
            "Contribution depends on joining age and selected pension amount."
        ],
        "documents": [
            "Savings bank or post-office savings account details.",
            "Completed APY registration form.",
            "Aadhaar and mobile details as requested by the enrolling institution.",
            "Spouse and nominee details where applicable."
        ],
        "application_process": [
            "Approach the bank or post office holding the savings account.",
            "Complete the APY registration form and select the pension amount.",
            "Authorise periodic contributions from the linked account.",
            "Alternatively, use the official eAPY enrolment facility where available."
        ]
    },
    "PMJJBY": {
        "description": "Renewable one-year term life insurance scheme providing life cover to eligible subscribing bank and post-office account holders.",
        "benefits": [
            "First-time subscribers are subject to a 30-day lien period for non-accidental death claims; accidental death is exempt from this lien period, subject to policy rules."
            "Life insurance cover of Rs. 2 lakh on the insured subscriber's death, subject to policy terms and exclusions.",
            "The scheme is renewable annually for the cover period from 1 June to 31 May.",
            "The published annual premium is Rs. 436; confirm the current premium and applicable tax or policy terms before enrolment."
        ],
        "eligibility": [
            "Individual bank or post-office account holders aged 18 to 50 years may enrol.",
            "The subscriber must provide consent and enable the prescribed auto-debit.",
            "A person with multiple accounts can enrol through only one eligible account."
        ],
        "documents": [
            "Eligible savings bank or post-office account.",
            "Completed consent-cum-declaration or enrolment form.",
            "Identity and nominee details requested by the participating institution."
        ],
        "application_process": [
            "Apply through the participating bank branch, bank channel or post office.",
            "Submit the prescribed consent and auto-debit authorisation.",
            "Check enrolment confirmation and annual renewal status with the bank or post office."
        ]
    },
    "PMSBY": {
        "description": "Renewable one-year personal accident insurance scheme for eligible bank and post-office account holders.",
        "benefits": [
            "Accidental death or permanent total disability cover of Rs. 2 lakh.",
            "Permanent partial disability cover of Rs. 1 lakh, subject to policy definitions.",
            "The published annual premium is Rs. 20; confirm the current premium and policy terms before enrolment."
        ],
        "eligibility": [
            "Individual bank or post-office account holders aged 18 to 70 years may enrol.",
            "The applicant must provide consent and authorise auto-debit.",
            "Only one account can be used for enrolment if the person has multiple accounts."
        ],
        "documents": [
            "Eligible bank or post-office account details.",
            "Completed PMSBY consent-cum-declaration or enrolment form.",
            "Nominee details and identity information requested by the participating institution."
        ],
        "application_process": [
            "Apply through the participating bank branch, bank channel or post office.",
            "Provide consent and auto-debit authorisation.",
            "Retain the acknowledgement and check annual renewal status."
        ]
    },
    "PM_MUDRA": {
        "description": "Pradhan Mantri MUDRA Yojana provides institutional collateral-free credit to eligible micro-enterprises for income-generating business activities.",
        "benefits": [
            "Shishu loans cover requirements up to Rs. 50,000.",
            "Kishor loans cover requirements above Rs. 50,000 and up to Rs. 5 lakh.",
            "Tarun loans cover requirements above Rs. 5 lakh and up to Rs. 10 lakh.",
            "Tarun Plus loans cover requirements above Rs. 10 lakh and up to Rs. 20 lakh for eligible borrowers who have successfully repaid a previous Tarun loan.",
            "Loans are assessed and sanctioned by participating lending institutions; approval is not automatic."
        ],
        "eligibility": [
            "Applicants must have a viable income-generating micro-enterprise proposal in manufacturing, trading, services or eligible allied agricultural activities.",
            "Eligible applicants may include proprietorships, partnerships and other permitted micro-enterprise forms.",
            "The lending institution assesses creditworthiness, business plan and repayment capacity."
        ],
        "documents": [
            "Identity and address proof of applicant and business.",
            "Business address and activity details.",
            "Business plan, quotation or project report where requested.",
            "Bank statements and financial information where requested by the lender.",
            "Category-specific or registration documents where applicable."
        ],
        "application_process": [
            "Approach a participating bank, NBFC or microfinance institution.",
            "Discuss the appropriate loan category and submit the business proposal.",
            "Alternatively, check the JanSamarth portal for an available online application route.",
            "The lender evaluates the application and communicates its decision and terms."
        ]
    },
    "PM_UJJWALA": {
        "description": "PMUY supports eligible adult women from poor households to obtain a deposit-free LPG connection.",
        "benefits": [
            "Eligible beneficiaries receive a deposit-free LPG connection with specified equipment and installation charges covered under the scheme.",
            "The connection package includes a cylinder, pressure regulator, safety hose and consumer booklet, subject to the selected connection type.",
            "The scheme provides the applicable first refill and stove support under current PMUY rules.",
            "The beneficiary may choose an eligible 14.2 kg or 5 kg connection option."
        ],
        "eligibility": [
            "The applicant must be an adult woman aged 18 years or above.",
            "The household must not already have an LPG connection in the name of a family member.",
            "The applicant must belong to an eligible poor household and submit the prescribed deprivation declaration and supporting documents."
        ],
        "documents": [
            "Applicant Aadhaar and completed KYC form.",
            "Ration card or State-issued family-composition document.",
            "Aadhaar details of adult family members listed in the family document.",
            "Bank account passbook copy or cancelled cheque.",
            "Address proof if the current address differs from Aadhaar address.",
            "Prescribed deprivation declaration and migrant self-declaration where applicable."
        ],
        "application_process": [
            "Apply through an LPG distributor of choice or the official PMUY online application facility.",
            "Submit the KYC form, identity, address, family and bank details.",
            "Submit the deprivation declaration and other applicable documents.",
            "The LPG distributor and Oil Marketing Company verify the application before connection release."
        ]
    },
    "PMFBY": {
        "description": "Pradhan Mantri Fasal Bima Yojana provides crop insurance for notified crops and areas against specified risks during notified crop seasons.",
        "benefits": [
            "The scheme provides insurance protection for notified crop losses caused by covered risks under the operational guidelines.",
            "Covered risks can include prevented sowing, standing crop losses from specified non-preventable risks, and post-harvest losses in eligible cases.",
            "Farmer premium rates are generally capped at 2% for Kharif food and oilseed crops, 1.5% for Rabi food and oilseed crops, and 5% for annual commercial and horticultural crops; State notifications and current guidelines apply.",
            "Claim amounts depend on the insured crop, notified area, sum insured, assessed loss and applicable procedure."
        ],
        "eligibility": [
            "Farmers growing notified crops in notified areas and having insurable interest may be covered.",
            "Sharecroppers and tenant farmers may be eligible if they provide the required evidence permitted by the State notification.",
            "Loanee and non-loanee farmer enrolment rules must be checked against the current season's notification and operational guidelines.",
            "The crop, area, insurance window and cut-off date must be notified for the relevant season."
        ],
        "documents": [
            "Aadhaar and bank account details.",
            "Land record or Record of Rights, as applicable.",
            "Sowing certificate or other crop evidence where required.",
            "Lease, agreement or other insurable-interest evidence for tenant or sharecropper farmers, as permitted by the State.",
            "Application and crop details for the notified season."
        ],
        "application_process": [
            "Check the notified crop, insured area, insurance company and enrolment deadline for the relevant State and season.",
            "Ensure the insured crop matches the crop actually sown and the declared land area does not exceed the actual land area.",
            "Keep the application acknowledgement and policy details.",
            "Report crop losses within the applicable notification and operational-guideline deadline through the prescribed channel.",
            "Tenant farmers and sharecroppers must provide acceptable proof of insurable interest."

        ]
    }
}

with path.open("r", encoding="utf-8-sig") as f:
    schemes = json.load(f)

backup = path.with_suffix(".before_enrichment.json")
backup.write_text(
    json.dumps(schemes, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

updated = set()

for scheme in schemes:
    sid = scheme["scheme_id"]
    if sid not in CONTENT:
        continue

    scheme.update(CONTENT[sid])
    scheme["last_verified"] = "2026-11-15"
    scheme["verification_status"] = (
        "official_sources_reviewed_check_current_state_and_scheme_notifications"
    )
    updated.add(sid)

missing = set(CONTENT) - updated
if missing:
    raise ValueError(f"Scheme IDs not found: {sorted(missing)}")

with path.open("w", encoding="utf-8") as f:
    json.dump(schemes, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"SUCCESS: enriched {len(updated)} schemes")
print(f"Backup saved to: {backup}")
for sid in sorted(updated):
    print("-", sid)
