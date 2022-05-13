from enum import Enum


class TermURL(str, Enum):
    """synapse coding system"""

    SYNAPSE = "https://synapse-medicine.com"
    LOINC = "http://loinc.org"
    SNOMED_CT = "http://snomed.info/sct"
