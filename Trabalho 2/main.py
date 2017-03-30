from bottle import run, get, post, view, request, redirect, route, static_file, template
import bottle
import json
import threading
import requests
import time
import sys

mensagens = set([])
peers = ['localhost:' + p for p in sys.argv[2:]]
lock = threading.Lock()

@get('/cliente') # or @route('/login')
@view('cliente')
def login():
    return dict(msg = list(mensagens))

@post('/servidor') # or @route('/login', method='POST')
def do_login():
    t = request.forms.getunicode('text')
    u = request.forms.getunicode('username')

    mensagens.add((u, t))
    redirect("/cliente")
    run(reloader=True)

@get('/peers')
def allpeers():
    return json.dumps(peers)

def client():
    global lock
    time.sleep(5)
    while True:
        time.sleep(1)
        np = []
        for p in peers:
            try:
                r = requests.get(p + '/peers')
                np.append(p)
                np.extend(json.loads(r.text))
            except:
                pass

            time.sleep(1)
        with lock:
            peers.extend(list(set(np)))

@get('/messages')
def msg():
    return json.dumps(list(mensagens))

def getMessagesFrom(p):
    link = "http://" + p + "/messages"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((a, b) for [a,b] in obj)
            return setT
    except:
        print("Connection Error")
    return set([])

def attmessage():
    while True:
        time.sleep(1)
        N = set([])
        global mensagens
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            if m.difference(mensagens):
                N = N.union(m.difference(mensagens))
        mensagens = mensagens.union(N)

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host = 'localhost', port = int(sys.argv[1]))
