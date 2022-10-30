from flask_cors import CORS
from flask import Flask, render_template, request, redirect, make_response
import requests as req
import six
import base64
import six.moves.urllib.parse as urllibparse
import time
import random

app = Flask('__name__', static_url_path='', static_folder='static', )
CORS(app)


@app.route('/')
def index():
    if not request.cookies.get('sptifycontrolrefreshtoken124452543'):
        scopes = 'user-read-playback-state user-modify-playback-state playlist-read-private'
        payload = {"client_id": "<client_id>", "response_type": "code",
                   "redirect_uri": "http://localhost:5000/controlcallback", "scope": scopes, "show_dialog": True}
        parsed = urllibparse.urlencode(payload)
        time.sleep(3)
        return redirect("https://accounts.spotify.com/authorize?" + parsed)
    if not request.cookies.get('sptifysdkrefreshtoken124452543'):
        scopes = 'user-read-private user-read-email streaming user-modify-playback-state user-read-playback-state'
        payload = {"client_id": "<client_id>", "response_type": "code",
                   "redirect_uri": "http://localhost:5000/sdkcallback", "scope": scopes, "show_dialog": False}
        parsed = urllibparse.urlencode(payload)
        time.sleep(3)
        return redirect("https://accounts.spotify.com/authorize?" + parsed)
    else:
        ref = request.cookies.get('sptifysdkrefreshtoken124452543')
        payload = {"grant_type": "refresh_token", "refresh_token": ref}
        auth_header = base64.b64encode(
            six.text_type("<client_id>" + ":" + "<i_think_the_secret_key>").encode("ascii")
        )
        headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
        resp = req.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)
        text = resp.json()
        sdktoken = text.get("access_token")
        return render_template("index.html", token=sdktoken)


@app.route('/sdkcallback')
def sdkCallback():
    if request.args.get('code'):
        code = request.args.get('code')
        payload = {"grant_type": "authorization_code", "code": code,
                   "redirect_uri": "http://localhost:5000/sdkcallback"}
        auth_header = base64.b64encode(
            six.text_type("<client_id>" + ":" + "<i_think_the_secret_key>").encode("ascii")
        )
        headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
        resp = req.post("https://accounts.spotify.com/api/token", data=payload, headers=headers, verify=True)
        text = resp.json()
        refto = text.get("refresh_token")
        res = make_response(redirect('/'))
        res.set_cookie("sptifysdkrefreshtoken124452543", refto, max_age=60 * 60 * 24 * 365 * 2)
        return res
    else:
        return redirect('/')


@app.route('/controlcallback')
def controllCallback():
    if request.args.get('code'):
        code = request.args.get('code')
        payload = {"grant_type": "authorization_code", "code": code,
                   "redirect_uri": "http://localhost:5000/controlcallback"}
        auth_header = base64.b64encode(
            six.text_type("<client_id>" + ":" + "<i_think_the_secret_key>").encode("ascii")
        )
        headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
        resp = req.post("https://accounts.spotify.com/api/token", data=payload, headers=headers, verify=True)
        text = resp.json()
        reftoken = text.get("refresh_token")
        res = make_response(redirect('/'))
        res.set_cookie("sptifycontrolrefreshtoken124452543", reftoken, max_age=60 * 60 * 24 * 365 * 2)
        return res
    else:
        return redirect('/')


@app.route('/delete')
def deleteCookies():
    res = make_response(redirect('/'))
    res.set_cookie("sptifycontrolrefreshtoken124452543", "", max_age=0)
    res.set_cookie("sptifysdkrefreshtoken124452543", "", max_age=0, )
    return res


@app.route('/ref', methods=['POST'])
def refreshControl():
    ref = request.args.get('ref')
    payload = {"grant_type": "refresh_token", "refresh_token": ref}
    auth_header = base64.b64encode(
            six.text_type("<client_id>" + ":" + "<i_think_the_secret_key>").encode("ascii")
    )
    headers = {"Authorization": "Basic %s" % auth_header.decode("ascii")}
    resp = req.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)
    text = resp.json()
    return text


@app.route('/song')
def songs():
    songlist = []
    song = open('list.txt', 'r')
    for line in song:
        songlist.append(line[:-1])
    inte = random.randint(0, len(songlist)-1)
    return songlist[inte]


if __name__ == '__main__':
    app.run("localhost", 5000)
    app.config.from_pyfile('config.py')
