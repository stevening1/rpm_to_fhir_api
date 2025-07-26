# rpm_to_fhir_api
An RPM-to-EHR integration system I created to convert simulated remote patient monitoring data to an FHIR JSON format, which can be stored in a HAPI FHIR server for easy integration with hospital electronic health record systems. 

client.py
- Creates simulated heart rate data in JSON format
- Creates tests of variable duration and users using Locust to record the API's performance metrics. Measures response times for the API to convert the simulated heart rate data into FHIR resources and store the resources in a HAPI FHIR server hosted on an EC2 instance
- Creates a CSV file with the API performance metrics of all test runs.

lambda_function.py
- A Python script that is added to AWS Lambda that converts simulated heart data into FHIR patient and observation resources
- Sends the created resources to a HAPI FHIR server
- Sends a response back to client.py to record API performance metrics

analyze_locust_data.py
- Uses pandas and matplotlib to calculate API response time summary statistics and to generate tables and figures to visualize the results
