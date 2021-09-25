import requests
import tweepy
import os 

# ここに取得したキーを書く
CONSUMER_KEY = os.getenv("TWITTER_API_KEY_JP")
CONSUMER_TOKEN = os.getenv("TWITTER_API_KEY_SECRET_JP")
ACCESS_KEY = os.getenv("ACCESS_TOKEN_JP")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_SECRET_JP")

# tweepyによるOAuth認証処理
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_TOKEN)
auth.set_access_token(ACCESS_KEY, ACCESS_TOKEN)
api = tweepy.API(auth)

def request_data(rdf_type):
    #tweet内容のopendataのjsonデータをから取り出し
    api_key = os.getenv("API_KEY")
    endpoint = "https://api-tokyochallenge.odpt.org/api/v4/" 
    data_type = rdf_type + "?"
    params = {
        "acl:consumerKey": api_key
    }

    #conditions="&owl:sameAs=odpt.TrainInformation:JR-East.ChuoRapid"
    response = requests.get(endpoint + data_type, params=params)
    print(response)
    data = response.json()
    return data


context = ""
text_count = 140
data = request_data("odpt:TrainInformation")


for i in range(len(data)):
    # If train is delayed, tweet the information
    if (len(data[i]['odpt:trainInformationText']['ja']) > 21):
        railway = data[i]['owl:sameAs'].split(":")[-1].split(".")[-1]
        context += f"{railway}: {data[i]['odpt:trainInformationText']['ja']}\n"
    
        # ----- Currently bugged -----
        # For testing purpose I will cut the text entirely which will not working properly.
        # while len(context) > 140:
        #     api.update_status(context[:text_count])
        #     print(context[:text_count] + "\n")
        #     context = context[text_count:]
        #     text_count += 140
        # text_count = 140

# ツイートの実行
print(context)
# api.update_status(context)
api.update_status("Deploy Test")
