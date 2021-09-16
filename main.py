from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import requests
import os
import re

# App Settings
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")
ENDPOINT = "https://api-tokyochallenge.odpt.org/api/v4/"
Bootstrap(app)

# ---------- Function ----------

def request_data(rdf_type):
    # Request the data from API
    data_type = rdf_type + "?"
    params = {
        "acl:consumerKey": API_KEY
    }
    response = requests.get(ENDPOINT + data_type, params=params)
    print(response)
    data = response.json()

    return data

def camel_case_split(str):
    return " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', str).split())


# ---------- Flask Website ----------

@app.route("/")
def home():
    data = request_data("odpt:TrainInformation")
    railways = [information['owl:sameAs'].split(':')[1].split(".") for information in data]
    operators = list(set([railway[0] for railway in railways]))
    train_dict = {}

    # Loop through operators and railways to create dictionary of information
    for i in range(len(operators)):
        train_status = [information['odpt:trainInformationText']['ja'] for information in data if information['owl:sameAs'].split(':')[1].split(".")[0] == operators[i]]
        time = [":".join(information['dc:date'].split('T')[1].split('+')[0].split(":")[:2]) for information in data if information['owl:sameAs'].split(':')[1].split(".")[0] == operators[i]]
        # Split the camel case data to normal format
        operators[i] = camel_case_split(operators[i])
        train_dict.update(
            {
                operators[i]: {
                    "railways": [camel_case_split(railway[-1]) for railway in railways if camel_case_split(railway[0]) == operators[i]],
                    "train_status": train_status,
                    "time": time
                }
            }
        )

    return render_template("index.html", train_dict=train_dict)


@app.route("/passenger")
def passenger():
    # Make a graph from the Operators
    data = request_data("odpt:PassengerSurvey")
    stations = [information["odpt:station"][0].split(':')[1].split(".") for information in data]
    operators = list(set([information["odpt:operator"].split(":")[-1] for information in data]))
    passenger_dict = {}

    # Loop through operators and railways to create dictionary of information
    for i in range(len(operators)):
        passenger_journeys = [[journey["odpt:passengerJourneys"] for journey in information["odpt:passengerSurveyObject"]][-1] for information in data if information["odpt:operator"].split(":")[-1] == operators[i]]
        passenger_years = [[journey["odpt:surveyYear"] for journey in information["odpt:passengerSurveyObject"]][-1] for information in data if information["odpt:operator"].split(":")[-1] == operators[i]]
        # Split the camel case data to normal format
        operators[i] = camel_case_split(operators[i])
        passenger_dict.update(
            {
                operators[i]: {
                    "stations": [camel_case_split(station[-1]) for station in stations if camel_case_split(station[0]) == operators[i]],
                    "passenger_journeys": passenger_journeys,
                    "passenger_years": passenger_years
                }
            }
        )
    
    return render_template("passenger.html", passenger_dict=passenger_dict, operators_list=[camel_case_split(operator) for operator in operators])


if __name__ == "__main__":
    app.run(debug=True)



    


