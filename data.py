import requests
import re

ENDPOINT = "https://api-tokyochallenge.odpt.org/api/v4/"

class DataManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.railway_data = self.request_data("odpt:Railway")
        self.operator_data = self.request_data("odpt:Operator")
        self.train = self.train_status()
        self.passenger = self.passenger_surveys()

    def camel_case_split(self, str):
        return " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', str).split())

    # ----- Requesting data function -----

    def request_data(self, rdf_type):
        # Request the data from API
        data_type = rdf_type + "?"
        params = {
            "acl:consumerKey": self.api_key
        }
        response = requests.get(ENDPOINT + data_type, params=params)
        print(response)
        data = response.json()

        return data

    def get_railway(self, railway, language):
        for info in self.railway_data:
            railway_name = info["owl:sameAs"].split(":")[-1]
            # e.g. Keisei, Seibu, Keikyu exception
            if "." not in railway:
                railway_name = railway_name.split(".")[0]
            if railway == railway_name:
                return info["odpt:railwayTitle"][language]

    def get_operator(self, operator, language):
        for info in self.operator_data:
            operator_name = info["owl:sameAs"].split(":")[-1]
            if operator == operator_name:
                return info["odpt:operatorTitle"][language]

    # ----- Data use in website -----

    def train_status(self):
        data = self.request_data("odpt:TrainInformation")
        railways = [information['owl:sameAs'].split(':')[1].split(".") for information in data]
        operators = list(set([railway[0] for railway in railways]))
        train_dict = {}
        
        # Loop through operators and railways to create dictionary of information
        for i in range(len(operators)):
            train_status = [information['odpt:trainInformationText']['ja'] for information in data if information['owl:sameAs'].split(':')[1].split(".")[0] == operators[i]]
            time = [":".join(information['dc:date'].split('T')[1].split('+')[0].split(":")[:2]) for information in data if information['owl:sameAs'].split(':')[1].split(".")[0] == operators[i]]
            train_dict.update(
                {
                    self.camel_case_split(operators[i]): 
                    {
                        "ja": {
                            "operator": self.get_operator(operators[i], "ja"),
                            "railways": [self.get_railway(".".join(railway), "ja") for railway in railways if railway[0] == operators[i]],
                            "train_status": train_status,
                            "time": time
                        },
                        "en": {
                            "operator": self.camel_case_split(operators[i]),
                            "railways": [self.camel_case_split(railway[-1]) for railway in railways if railway[0] == operators[i]],
                            "train_status": train_status,
                            "time": time
                        }
                    } 
                }
            )

        return train_dict
    
    def passenger_surveys(self):
        data = self.request_data("odpt:PassengerSurvey")
        stations = [information["odpt:station"][0].split(':')[1].split(".") for information in data]
        operators = list(set([information["odpt:operator"].split(":")[-1] for information in data]))
        passenger_dict = {}

        # Loop through operators and railways to create dictionary of information
        for i in range(len(operators)):
            passenger_journeys = [[journey["odpt:passengerJourneys"] for journey in information["odpt:passengerSurveyObject"]][-1] for information in data if information["odpt:operator"].split(":")[-1] == operators[i]]
            passenger_years = [[journey["odpt:surveyYear"] for journey in information["odpt:passengerSurveyObject"]][-1] for information in data if information["odpt:operator"].split(":")[-1] == operators[i]]
            # Split the camel case data to normal format
            passenger_dict.update(
                {
                    self.camel_case_split(operators[i]): {
                        "stations": [self.camel_case_split(station[-1]) for station in stations if station[0] == operators[i]],
                        "passenger_journeys": passenger_journeys,
                        "passenger_years": passenger_years
                    }
                }
            )
        
        return passenger_dict