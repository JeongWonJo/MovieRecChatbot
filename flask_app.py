import json, requests
from flask import Flask, request
import apiai
import pickle

app = Flask(__name__)

# facebook_page_access_token
PAT = 'YOUR TOKEN'
VERIFY_TOKEN = 'hey'

# api_access_key
CLIENT_ACCESS_TOKEN = 'd700c440f36647f4b716cf44516b3dd4'

ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

from pathlib import Path
home = str(Path.home())
movie_rec = pickle.load(open(home + "/mysite/movie_rec.pkl", "rb"))

@app.route('/', methods=['GET'])
def handle_verification():
    '''
    Facebook webhook 인증 올바르게 됐는지 확인
    '''
    if (request.args.get('hub.verify_token', '') == VERIFY_TOKEN):
        print("succefully verified")
        return request.args.get('hub.challenge', '')
    else:
        print("Wrong verification token!")
        return "Wrong validation token"


@app.route('/', methods=['POST'])
def handle_message():
    '''
    페이스북 메신저에서 유저가 보낸 문장, 유저의 아이디 관리
    '''
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]
                    send_message_response(sender_id, parse_user_message(message_text))

    return "ok"


def send_message(sender_id, message_text):
    '''
    유저에게 답장 보내기
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

                      params={"access_token": PAT},

                      headers={"Content-Type": "application/json"},

                      data=json.dumps({
                          "recipient": {"id": sender_id},
                          "message": {"text": message_text}
                      }))


def parse_user_message(user_text):
    '''
    유저가 입력한 문장을 API AI로 보내서 유저가 입력한 문장의 intent 알아보고,
    그에 맞는 답장 보내기
    '''

    request = ai.text_request()
    request.query = user_text

    response = json.loads(request.getresponse().read().decode('utf-8'))
    
    reponseStatus = response['status']['code']
    if responseStatus == 200):
        intent = response['result']['metadata']['intentName']
    
        try:
            if intent == "movie-info":
                input_movie = response['result']['parameters']['movie']
                reply = get_movie_detail(input_movie)
                return reply

            elif intent == "movie-recommend":
                input_movie = response['result']['parameters']['movie']
                input_year = response['result']['parameters']['number']
                reply = movie_rec[(input_movie, input_year)]
                return reply
        except:
            reply = "I don't understand your message."
            return reply



def send_message_response(sender_id, message_text):
    send_message(sender_id, message_text)
    



# omdb에서 먼저 API키 가져와야 함
# http://www.omdbapi.com/apikey.aspx
def get_movie_detail(movie):
    import requests
    import json

    api_key = '94e30dff' # 본인 omdb API키 넣기
    movie_detail = requests.get('http://www.omdbapi.com/?t={0}&apikey={1}'.format(movie, api_key)).content
    movie_detail = json.loads(movie_detail)
    movie_response = """
        Title : {0}
        Released: {1}
        Actors: {2}
        Plot: {3}
    """.format(movie_detail['Title'], movie_detail['Released'], movie_detail['Actors'], movie_detail['Plot'])

    return movie_response




if __name__ == '__main__':
    app.run()
