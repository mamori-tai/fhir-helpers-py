patient1 = {
    "resourceType": "Patient",
    "identifier": [
        {
            "type": {
                "coding": [
                    {
                        "system": "http://interopsante.org/CodeSystem/v2-0203",
                        "code": "PI",
                    }
                ]
            },
            "value": "12121313131411515",
        }
    ],
    "name": [{"family": "DUBOIS", "given": ["Marc"]}],
    "gender": "male",
    "birthDate": "1986-02-05",
    "telecom": [{"system": "email", "value": "cramm@hotmaill.fr"}],
    "managingOrganization": {"reference": "Organization/1"},
}
