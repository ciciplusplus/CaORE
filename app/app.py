import werkzeug.serving

class LenientHandler(werkzeug.serving.WSGIRequestHandler):
    def parse_request(self):
        self.raw_requestline = self.raw_requestline.replace(b"http/1.1", b"HTTP/1.1")
        return super().parse_request()

# monkey-patch BEFORE flask.cli starts the server
werkzeug.serving.WSGIRequestHandler = LenientHandler

from flask import Flask, make_response, request, send_file, jsonify
from flask.logging import logging

from blob_codec import MY_String2Blob, MY_Blob2String
import io

spammy_logs = [] #["Get /WebAPI.php?action=addLog", "Get /WebAPI.php?action=logConnectStatus"]
class SpammyLogs(logging.Filter):
    def filter(self, record):
        for x in spammy_logs:
            if x in record.getMessage():
                return False
        return True
logging.getLogger("werkzeug").addFilter(SpammyLogs())

app = Flask(__name__)

@app.route("/ope/ServerConfig.php")
def server_config():
    args = request.args
    b = args.get('b')
    #return "Bad request!", 400
    if b is None:
        return "Bad request! 1", 400

    cmd = MY_Blob2String(b)
    print(cmd)

    resp = make_response('f|1|r|s|configured|307|XplayerURL|http://gllive.gameloft.com/ope/GenericXPlayer_v1.php|type|2|XPPHPVerNo|4|WebAPIURL|http://gllive.gameloft.com/WebAPI.php|')

    resp.headers['Content-Type'] = 'text/html'
    resp.headers['Connection'] = 'keep-alive'
    return resp

@app.route("/ope/GenericXPlayer_v1.php", methods=['GET'])
def generic_xplayer():
    #print(request.args)
    args = request.args
    b = args.get('b')
    #return "Bad request!", 400
    if b is None:
        return "Bad request! 1", 400

    cmd = MY_Blob2String(b)
    print(cmd)

    cmd_split = cmd.split('|')
    if cmd_split[0] != 'f':
        return "Bad request! 2", 400

    match cmd_split[1]:
        case "123":
            #resp = make_response('f|-100|r|s|\0') # touchHLE only?
            resp = make_response('f|123|r|s|0|http://gllive.gameloft.com/empty\0')
        case "124":
            #resp = make_response('f|124|r|s|\0') # touchHLE only?
            resp = make_response('f|124|r|s|0|http://gllive.gameloft.com/empty\0')
        # Login
        case "15":
            resp = make_response('f|15|r|s|u|abc|t|1|tk|t-o-k-e-n|tke|3600|un|1|n|1|')
        # Apple user info
        case "115":
            resp = make_response('f|115|r|s|\0')
        case _:
            resp = make_response('f|53|r|e|102')

    resp.headers['Content-Type'] = 'text/html'
    resp.headers['Connection'] = 'keep-alive'
    return resp

@app.get("/empty")
def empty_file():
    """
    Responds with a 4-byte file named `empty.txt` with a NUL.
    """
    empty_buf = io.BytesIO(b"\0\0\0\0") # Important to return 4 bytes!
    empty_buf.seek(0)

    return send_file(
        empty_buf,
        as_attachment=True,              # triggers “download” in the browser
        download_name="empty.txt",       # filename shown to the user
        mimetype="application/octet-stream"
    )

@app.route("/WebAPI.php", methods=['GET'])
def web_api():
    args = request.args
    action = args.get('action')

    match action:
        case 'addLog':
            return {}
        case 'logConnectStatus':
            return {}
        case 'getconsumedinfo':
            return {
                "action": "getconsumedinfo",
                "msg": "OK1",
                "message": "OK2",
                #"error": 0,
                "rune": 98,
                "gold": 99,
                #"time": "1749676618",
                "subscription_status": 1,
                "sub_expired": "2025-06-11 21:12:00",
                "time": "2025-05-11 21:12:00"
            }
        case 'getusercharacter':
            return {
                "action": "getusercharacter",
                "msg": "OK3",
                "message": "OK4",
                "characters": [
                    {
                        "id": 24, #25, #24, #29, #1, #24, #1, # 8
                        "cname": "Derek1",
                        "vserver": "A1",
                        "vsname": "a1",
                        "vstatus": 1,
#                        "creation_room": 6,
#                        "last_login_room": 6
                    },
                    {
                        "id": 25,
                        "cname": "Derek1",
                        "vserver": "A1",
                        "vsname": "a1",
                        "vstatus": 1,
                    },
                    {
                        "id": 29,
                        "cname": "Derek1",
                        "vserver": "A1",
                        "vsname": "a1",
                        "vstatus": 1,
                    }
                ],
                # "subscription_status": 0,
                # "sub_expired": False
            }
        case 'getserverslist':
            return {
                "action": "getserverslist",
                "msg": "OK5",
                "message": "OK6",
                "serverlist": [
                    { "datacenter": "A1", "name": "a1" }
                ],
            }
        case 'getworldsinfo':
            return {
                "action": "getworldsinfo",
                "msg": "OK7",
                "message": "OK8",
                "list": [
                    { "id": 1, "name": "F1", "type": "B1", "amount": 999 }
                ],
            }
        case 'getlobbyinfo':
            # return {}
            return {
                #"status": 0,
                #"error": 0,
                #"action": "getlobbyinfo",
                "msg": "OK9",
                "message": "OK10",
                "domain": "192.168.1.78",
                "port": 9999,
                "expire": 3600,
                "token": "token-2",
                #"list": []
                # "list": [
                #     { "type": "Tunnel ", "amount": 1 }
                # ]
                # "list": [
                #     { "type": "B1", "amount": 999 }
                # ],
            }

    return "ACK", 200