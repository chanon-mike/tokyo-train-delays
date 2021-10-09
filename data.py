from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import requests
import json
import re

OPENDATA_ENDPOINT = "https://api-tokyochallenge.odpt.org/api/v4/"
IBM_ENDPOINT = "https://api.au-syd.language-translator.watson.cloud.ibm.com/instances/96e3285a-e20c-40e4-8562-8fc9a454209d"

class DataManager:
    def __init__(self, opendata_api_key, ibm_api_key):
        self.opendata_api_key = opendata_api_key
        self.ibm_api_key = ibm_api_key

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
            "acl:consumerKey": self.opendata_api_key
        }
        response = requests.get(OPENDATA_ENDPOINT + data_type, params=params)
        print(response)
        data = response.json()

        return data

    def get_railway(self, railway, language):
        # e.g. Keisei, Seibu, Keikyu exception
        if railway == "Seibu" or railway == "Keisei" or railway == "Keikyu":
            station_exception = {"Seibu":"西武鉄道各線", "Keisei":"京成線", "Keikyu":"京急線"}
            return station_exception[railway]
        for info in self.railway_data:
            railway_name = info["owl:sameAs"].split(":")[-1].split(".")[-1]
            if railway == railway_name:
                return info["odpt:railwayTitle"][language]

    def get_operator(self, operator, language):
        for info in self.operator_data:
            operator_name = info["owl:sameAs"].split(":")[-1]
            if operator == operator_name:
                return info["odpt:operatorTitle"][language]

    # ----- Watson IBM translating -----

    def translate(self, text):
        if ("平常" in text) or (text == "現在、１５分以上の遅延はありません。"):
            return "Service on schedule"

        model_id = 'ja-en'

        # Prepare the Authenticator
        authenticator = IAMAuthenticator(self.ibm_api_key)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator
        )
        language_translator.set_service_url(IBM_ENDPOINT)

        # Translate
        translation = language_translator.translate(
            text=text,
            model_id=model_id).get_result()
            
        return json.loads(json.dumps(translation))["translations"][0]["translation"]

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
                            "railways": [self.get_railway(railway[-1], "ja") for railway in railways if railway[0] == operators[i]],
                            "train_status": train_status,
                            "time": time
                        },
                        "en": {
                            "operator": self.camel_case_split(operators[i]),
                            "railways": [self.camel_case_split(railway[-1]) for railway in railways if railway[0] == operators[i]],
                            # "train_status": [self.translate(status) for status in train_status],
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

