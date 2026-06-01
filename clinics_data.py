"""
Clinic Database - Simulated Mental Health Services Directory.

This module contains a curated list of 25+ simulated mental health clinics
with realistic data for the Clinic Finder feature.

Data includes:
- Clinic name and type
- Geographic coordinates (latitude/longitude)
- Contact information
- Insurance acceptance
- Specializations
"""

CLINICS_DATA = [
    {
        "name": "Serenity Mental Health Center",
        "type": "Clinic",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "phone": "(212) 555-0100",
        "email": "contact@serenitynyc.com",
        "specializations": ["Depression", "Anxiety", "PTSD", "CBT"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://serenitynyc.com"
    },
    {
        "name": "Dr. Sarah Chen - Therapist",
        "type": "Individual Therapist",
        "latitude": 40.7480,
        "longitude": -73.9862,
        "phone": "(212) 555-0101",
        "email": "sarah.chen@therapy.com",
        "specializations": ["Trauma", "DBT", "Mindfulness"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://sarahchencounseling.com"
    },
    {
        "name": "Wellness Psychiatry Associates",
        "type": "Psychiatry",
        "latitude": 40.7505,
        "longitude": -73.9972,
        "phone": "(212) 555-0102",
        "email": "appointments@wellnesspsych.com",
        "specializations": ["Medication Management", "Bipolar", "Schizophrenia"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://wellnesspsych.com"
    },
    {
        "name": "Compassionate Care Counseling",
        "type": "Counseling Center",
        "latitude": 40.7549,
        "longitude": -73.9840,
        "phone": "(212) 555-0103",
        "email": "info@compassionatecareny.com",
        "specializations": ["Family Therapy", "Couples", "Grief Counseling"],
        "insurance": ["Private", "Sliding Scale", "Employee Assistance"],
        "website": "https://compassionatecareny.com"
    },
    {
        "name": "Mindful Healing Therapy",
        "type": "Therapy Center",
        "latitude": 40.7614,
        "longitude": -73.9776,
        "phone": "(212) 555-0104",
        "email": "mindful@healingtherapy.com",
        "specializations": ["Anxiety", "Mindfulness", "Stress Management"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://mindfulfhealing.com"
    },
    {
        "name": "Urban Mental Health Services",
        "type": "Community Health Center",
        "latitude": 40.7282,
        "longitude": -74.0076,
        "phone": "(212) 555-0105",
        "email": "services@urbanmentalhealth.com",
        "specializations": ["PTSD", "Substance Abuse", "Crisis Support"],
        "insurance": ["Medicare", "Medicaid", "Uninsured Welcome"],
        "website": "https://urbanmh.org"
    },
    {
        "name": "Positive Psychology Institute",
        "type": "Therapy Clinic",
        "latitude": 40.7489,
        "longitude": -73.9680,
        "phone": "(212) 555-0106",
        "email": "hello@positivepsych.com",
        "specializations": ["Positive Psychology", "Life Coaching", "Goal Setting"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://positivepsychnyc.com"
    },
    {
        "name": "Trauma Recovery Center",
        "type": "Specialty Clinic",
        "latitude": 40.7505,
        "longitude": -74.0055,
        "phone": "(212) 555-0107",
        "email": "trauma@recoverynyc.com",
        "specializations": ["PTSD", "Trauma", "EMDR", "Somatic Therapy"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://traumarecoverynyc.com"
    },
    {
        "name": "Dr. James Rodriguez - Psychiatrist",
        "type": "Individual Psychiatrist",
        "latitude": 40.7549,
        "longitude": -74.0021,
        "phone": "(212) 555-0108",
        "email": "james.r@psych.com",
        "specializations": ["Depression", "Anxiety", "Medication Management"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://jamesrodriguezmd.com"
    },
    {
        "name": "Integrative Wellness Clinic",
        "type": "Wellness Center",
        "latitude": 40.7614,
        "longitude": -74.0077,
        "phone": "(212) 555-0109",
        "email": "wellness@integrative.com",
        "specializations": ["Holistic Health", "Meditation", "Nutritional Counseling"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://integrativewellnessnyc.com"
    },
    {
        "name": "Child & Adolescent Mental Health",
        "type": "Specialty Clinic",
        "latitude": 40.7282,
        "longitude": -73.9976,
        "phone": "(212) 555-0110",
        "email": "youth@childmentalhealth.com",
        "specializations": ["Child Therapy", "Teen Counseling", "School Issues"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://childmentalhealth.org"
    },
    {
        "name": "Cognitive Behavioral Therapy Institute",
        "type": "Therapy Institute",
        "latitude": 40.7489,
        "longitude": -73.9780,
        "phone": "(212) 555-0111",
        "email": "cbt@cbti.com",
        "specializations": ["CBT", "OCD", "Social Anxiety", "GAD"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://cbtinstitute.org"
    },
    {
        "name": "Addiction Recovery Services",
        "type": "Treatment Center",
        "latitude": 40.7505,
        "longitude": -73.9680,
        "phone": "(212) 555-0112",
        "email": "recovery@addictionservices.com",
        "specializations": ["Substance Abuse", "Addiction", "12-Step Support"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://addictionrecoverynyc.com"
    },
    {
        "name": "Women's Mental Health Center",
        "type": "Specialty Clinic",
        "latitude": 40.7614,
        "longitude": -73.9680,
        "phone": "(212) 555-0113",
        "email": "women@mentalhealth.com",
        "specializations": ["Postpartum Depression", "Women's Issues", "Reproductive Health"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://womensmentalhealth.org"
    },
    {
        "name": "Couples Therapy Center",
        "type": "Therapy Center",
        "latitude": 40.7282,
        "longitude": -74.0021,
        "phone": "(212) 555-0114",
        "email": "couples@therapycenter.com",
        "specializations": ["Couples Therapy", "Family Therapy", "Relationship Counseling"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://couplestherapynyc.com"
    },
    {
        "name": "Crisis Intervention Services",
        "type": "Crisis Center",
        "latitude": 40.7549,
        "longitude": -73.9780,
        "phone": "(212) 555-CRISIS",
        "email": "crisis@intervention.com",
        "specializations": ["Crisis Support", "Emergency Services", "Suicide Prevention"],
        "insurance": ["All", "No Insurance Required"],
        "website": "https://crisisinterventionnyc.org"
    },
    {
        "name": "Life Skills Counseling",
        "type": "Counseling Center",
        "latitude": 40.7505,
        "longitude": -74.0077,
        "phone": "(212) 555-0115",
        "email": "skills@lifecounseling.com",
        "specializations": ["Life Coaching", "Goal Setting", "Career Counseling"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://lifeskillsny.com"
    },
    {
        "name": "Sleep & Anxiety Clinic",
        "type": "Specialty Clinic",
        "latitude": 40.7614,
        "longitude": -73.9976,
        "phone": "(212) 555-0116",
        "email": "sleep@anxietycare.com",
        "specializations": ["Sleep Disorders", "Anxiety", "Insomnia"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://sleepanxietyclinic.com"
    },
    {
        "name": "Dr. Maria Garcia - Psychologist",
        "type": "Individual Psychologist",
        "latitude": 40.7282,
        "longitude": -73.9680,
        "phone": "(212) 555-0117",
        "email": "maria.garcia@psych.com",
        "specializations": ["Depression", "Anxiety", "General Counseling"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://mariagarciapsych.com"
    },
    {
        "name": "LGBTQ+ Affirming Therapy",
        "type": "Specialty Clinic",
        "latitude": 40.7489,
        "longitude": -74.0021,
        "phone": "(212) 555-0118",
        "email": "affirming@lgbtqtherapy.com",
        "specializations": ["LGBTQ+ Support", "Gender Issues", "Identity Counseling"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://lgbtqaffirmingtherapy.org"
    },
    {
        "name": "Geriatric Mental Health Services",
        "type": "Specialty Clinic",
        "latitude": 40.7549,
        "longitude": -74.0077,
        "phone": "(212) 555-0119",
        "email": "seniors@mentalhealth.com",
        "specializations": ["Aging", "Dementia Support", "Elderly Care"],
        "insurance": ["Medicare", "Medicaid", "Private"],
        "website": "https://geriatricmh.org"
    },
    {
        "name": "Neurofeedback & Biofeedback Center",
        "type": "Treatment Center",
        "latitude": 40.7505,
        "longitude": -73.9976,
        "phone": "(212) 555-0120",
        "email": "neurofeedback@center.com",
        "specializations": ["ADHD", "Neurofeedback", "Peak Performance"],
        "insurance": ["Private", "Sliding Scale"],
        "website": "https://neurofeedbackcenter.com"
    },
    {
        "name": "Telehealth Mental Health Services",
        "type": "Virtual Clinic",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "phone": "(844) 555-0121",
        "email": "virtual@telehealth.com",
        "specializations": ["Online Therapy", "Convenient Scheduling", "All Ages"],
        "insurance": ["Private", "Some Insurance Plans"],
        "website": "https://telehealth-mh.com"
    },
    {
        "name": "Grief Support Group & Counseling",
        "type": "Support Center",
        "latitude": 40.7282,
        "longitude": -74.0055,
        "phone": "(212) 555-0122",
        "email": "grief@supportgroup.com",
        "specializations": ["Grief Counseling", "Bereavement", "Loss Support"],
        "insurance": ["Private", "Sliding Scale", "Free Groups"],
        "website": "https://griefsupportny.org"
    },
]


def get_clinics_near_location(latitude: float, longitude: float, radius_miles: float = 10) -> list:
    """
    Get clinics within a specified radius from given coordinates.

    Args:
        latitude: User's latitude
        longitude: User's longitude
        radius_miles: Search radius in miles

    Returns:
        List of clinics within radius
    """
    from math import radians, cos, sin, asin, sqrt

    def haversine(lon1, lat1, lon2, lat2):
        """Calculate great circle distance between two points on earth (in miles)"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 3959  # Radius of earth in miles
        return c * r

    nearby_clinics = []
    for clinic in CLINICS_DATA:
        distance = haversine(longitude, latitude, clinic["longitude"], clinic["latitude"])
        if distance <= radius_miles:
            clinic_copy = clinic.copy()
            clinic_copy["distance"] = round(distance, 2)
            nearby_clinics.append(clinic_copy)

    # Sort by distance
    return sorted(nearby_clinics, key=lambda x: x["distance"])


def get_clinics_by_type(clinic_type: str) -> list:
    """
    Get clinics filtered by type.

    Args:
        clinic_type: Type of clinic to filter by

    Returns:
        List of matching clinics
    """
    return [clinic for clinic in CLINICS_DATA if clinic_type.lower() in clinic["type"].lower()]


def get_clinics_by_specialization(specialization: str) -> list:
    """
    Get clinics that specialize in a particular area.

    Args:
        specialization: Specialization to filter by

    Returns:
        List of matching clinics
    """
    return [
        clinic for clinic in CLINICS_DATA
        if any(spec.lower() == specialization.lower() for spec in clinic["specializations"])
    ]
