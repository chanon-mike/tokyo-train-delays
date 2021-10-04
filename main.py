from flask import Flask, render_template, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from data import DataManager
import os

# App Settings
app = Flask(__name__)
IBM_API_KEY = os.getenv("IBM_API_KEY")
OPENDATA_API_KEY = os.getenv("OPENDATA_API_KEY")
Bootstrap(app)

# Get the data from DataManager class
data_manager = DataManager(opendata_api_key=OPENDATA_API_KEY, ibm_api_key=IBM_API_KEY)


@app.route("/")
def home():
    return redirect(url_for('train_status', lang_code='ja'))


@app.route("/train/<lang_code>/")
def train_status(lang_code):
    if lang_code not in ['en', 'ja']:
        abort(404)

    train_dict = data_manager.train
    
    return render_template("train.html", train_dict=train_dict, lang_code=lang_code)


@app.route("/passenger/<lang_code>/")
def passenger(lang_code):
    if lang_code not in ['en', 'ja']:
        abort(404)

    passenger_dict = data_manager.passenger

    operators_list_en = []
    operators_list_ja = []
    for operator in passenger_dict.keys():
        operator = "".join(operator.split(" "))
        operators_list_en.append(data_manager.camel_case_split(operator))
        operators_list_ja.append(data_manager.get_operator(operator, "ja"))

    return render_template("passenger.html", passenger_dict=passenger_dict, operators_list_en=operators_list_en, operators_list_ja=operators_list_ja, lang_code=lang_code)


if __name__ == "__main__":
    app.run(debug=True)


    


