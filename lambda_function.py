import json
import requests

HAPI_FHIR_PATIENT_URL = "http://56.228.70.213:8080/fhir/Patient"
HAPI_FHIR_OBSERVATION_URL = "http://56.228.70.213:8080/fhir/Observation"

def convert_to_fhir_patient(data):
    return {
        "resourceType": "Patient",
        "id": data["patient_id"],
        "text": {
            "status": "generated",
            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'>{data['text']}</div>"
        },
        "identifier": [{
            "system": "http://hospital.smarthealth.org/patient-ids",
            "value": data["identifier"]
        }],
        "name": [{
            "use": "official",
            "text": data["name"]
        }],
        "gender": data["gender"],
        "birthDate": data["birth_date"]
    }

def convert_to_fhir_observation(data):
    return {
        "resourceType": "Observation",
        "text": {
            "status": "generated",
            "div": f"<div xmlns='http://www.w3.org/1999/xhtml'>{data['text']}</div>"
        },
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "8867-4",
                "display": "Heart rate"
            }]
        },
        "subject": {
            "reference": f"Patient/{data['patient_id']}"
        },
        "performer": [{
            "reference": f"Patient/{data['patient_id']}"
        }],
        "effectiveDateTime": data["timestamp"],
        "valueQuantity": {
            "value": data["heart_rate"],
            "unit": "beats/minute",
            "system": "http://unitsofmeasure.org",
            "code": "/min"
        }
    }

def put_to_fhir_server(resource, base_url):
    try:
        resource_id = resource["id"]
        put_url = f"{base_url}/{resource_id}"
        headers = {"Content-Type": "application/fhir+json"}

        print(f"\n[PUT] Sending Patient resource to {put_url}")
        print("Payload:", json.dumps(resource))

        response = requests.put(put_url, headers=headers, json=resource)
        
        # Raise exception if status is not OK
        response.raise_for_status()

        print("Response status:", response.status_code)
        print("Response body:", response.text)
        return response

    except requests.exceptions.HTTPError as http_err:
        print("HTTPError occurred while sending to FHIR server:")
        print(f"Status code: {response.status_code}")
        print(f"Response body: {response.text}")
        raise http_err

    except Exception as err:
        print("Unexpected error occurred in put_to_fhir_server():", str(err))
        raise err

def post_to_fhir_server(resource, url):
    headers = {"Content-Type": "application/fhir+json"}

    print(f"\n[POST] Sending Observation to {url}")
    print("Payload:", json.dumps(resource))

    response = requests.post(url, json=resource, headers=headers)
    print("Response status:", response.status_code)
    print("Response body:", response.text)
    return response

def lambda_handler(event, context):
    try:
        print("\n=== Received Event ===")
        print(json.dumps(event))

        if "body" not in event or event["body"] is None:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing request body"})
            }

        json_data = json.loads(event["body"])
        patient_data = json_data.get("patient")
        observation_data = json_data.get("observation")

        # Step 1: Create patient if provided
        if patient_data:
            print("\n--- Creating Patient ---")
            print("Received patient data:", json.dumps(patient_data))
            fhir_patient = convert_to_fhir_patient(patient_data)
            put_to_fhir_server(fhir_patient, HAPI_FHIR_PATIENT_URL)

        # Step 2: Create observation if provided
        if observation_data:
            print("\n--- Creating Observation ---")
            print("Received observation data:", json.dumps(observation_data))
            fhir_observation = convert_to_fhir_observation(observation_data)
            post_to_fhir_server(fhir_observation, HAPI_FHIR_OBSERVATION_URL)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "FHIR resource(s) processed",
                "patient_id": patient_data.get("patient_id") if patient_data else "N/A",
                "observation_id": observation_data.get("observation_id") if observation_data else "N/A"
            })
        }

    except Exception as e:
        print("Unhandled error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }


