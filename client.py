
import random
import time
import uuid
import csv 
from locust import HttpUser, task, between, events

# Accept run ID as a command-line argument
run_id = 3
duration = "10m"

# Track request statistics
request_stats = []

# Simulate non-FHIR Patient data
def generate_patient_data(patient_id):
    gender = random.choice(["male", "female"])
    birth_date = "1985-06-15"
    return {
        "patient_id": patient_id,
        "name": f"Patient {patient_id}",
        "birth_date": birth_date,
        "gender": gender,
        "identifier": str(patient_id),
        "text": f"{patient_id} - {gender}, born {birth_date}"
    }

# Simulate non-FHIR Observation data
def generate_observation_data(patient_id):
    heart_rate = random.randint(60, 100)
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return {
        "observation_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "heart_rate": heart_rate,
        "timestamp": timestamp,
        "text": f"Heart rate: {heart_rate} beats/minute observed on {timestamp}"
    }

# Save detailed request data
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    request_stats.append({
        "type": request_type,
        "name": name,
        "response_time_ms": response_time,
        "response_length": response_length,
        "status_code": response.status_code if response else "N/A",
        "success": exception is None,
        "run_id": run_id,
        "duration": duration
    })

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    if not request_stats:
        print("No requests recorded.")
        return

    for r in request_stats:
        r["timestamp"] = time.time()

    with open("locust_results_all.csv", mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=request_stats[0].keys())
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(request_stats)


    print(f"Saved results to locust_results.csv")



class HeartRateUser(HttpUser):
    wait_time = between(0.1, 0.3)
    host = "https://5iq2pe8nmk.execute-api.eu-north-1.amazonaws.com"

    def on_start(self):
        # Use a constant patient ID for all users/devices
        self.patient_id = "patient-1"
        self.patient_data = generate_patient_data(self.patient_id)
        self.start_time = time.time()

        # Send Patient resource once at start
        payload = {
            "patient": self.patient_data
        }
        print("Sending initial patient payload:", payload)
        self.client.post("/jsonToFhirHandler", json=payload)

    @task
    def send_observation(self):
        current_time = time.time()
        elapsed = int(current_time - self.start_time)

        # Send new observation every 10 seconds
        if elapsed % 10 == 0:
            observation_data = generate_observation_data(self.patient_id)
            payload = {
                "observation": observation_data
            }
            print("Sending observation payload:", payload)
            self.client.post("/jsonToFhirHandler", json=payload)
            time.sleep(10)  # match real-time interval




