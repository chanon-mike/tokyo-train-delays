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

railway_data = request_data("odpt:Railway")

def get_railway(railway, language):
    for info in railway_data:
        railway_name = info["owl:sameAs"].split(":")[-1]
        # e.g. Keisei, Seibu, Keikyu exception
        if "." not in railway:
            railway_name = railway_name.split(".")[0]
        if railway == railway_name:
            return info["odpt:railwayTitle"][language]

operator_data = request_data("odpt:Operator")

def get_operator(operator, language):
    for info in operator_data:
        operator_name = info["owl:sameAs"].split(":")[-1]
        if operator == operator_name:
            return info["odpt:operatorTitle"][language]


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
        train_dict.update(
            {
                camel_case_split(operators[i]): 
                {
                    "ja": {
                        "operator": get_operator(operators[i], "ja"),
                        "railways": [get_railway(".".join(railway), "ja") for railway in railways if railway[0] == operators[i]],
                        "train_status": train_status,
                        "time": time
                    },
                    "en": {
                        "operator": get_operator(operators[i], "en"),
                        "railways": [camel_case_split(railway[-1]) for railway in railways if railway[0] == operators[i]],
                        "train_status": train_status,
                        "time": time
                    }
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
        
    # from pprint import pprint
    # for operator in list(train_dict.keys()):
    #     pprint(len(train_dict[operator]['ja']['railways'])+1)
        # for i in range(len(list(train_dict[operator]["ja"]["railways"]))):
        #     print(train_dict[operator]["ja"]["railways"][i])


    


