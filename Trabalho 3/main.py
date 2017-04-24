from bottle import run, get, post, view, request, redirect, route, static_file, template
from frozendict import frozendict
import bottle
import json
import threading
import requests
import time
import sys

class VC:
    def __init__(self, name):
        self.name = name
        self.vectorClock = { self.name: 0 }

    def __repr__(self):
        return "V%s" % repr(self.vectorClock)

    def increment(self):
        self.vectorClock[self.name] += 1
        return self

    def update(self, t):
        self.increment()
        for k, v in t.items():
            if k not in vc.vectorClock or vc.vectorClock[k] < t[k]:
                vc.vectorClock[k] = v


mensagens = set([])
peers = ['localhost:' + p for p in sys.argv[2:]]
lock = threading.Lock()
vc = VC('http://localhost:' + sys.argv[1]);

allmsg = []

def menor(a, b):
    keys  = list(set(a[2].keys()).union(b[2].keys()))
    keys.sort()
    a = tuple(a[2][k] if k in a[2] else 0 for k in keys)
    b = tuple(b[2][k] if k in b[2] else 0 for k in keys)
    for i in range(0, len(a)):
        if a < b: return True
        if b < a: return False
    return False


def ordenar():
    global allmsg
    for i in range(1, len(allmsg)):
        chave = allmsg[i]
        k = i
        while k > 0 and menor(chave, allmsg[k - 1]):
            allmsg[k] = allmsg[k - 1]
            k -= 1
            allmsg[k] = chave


@get('/cliente') # or @route('/login')
@view('cliente')
def login():
    global allmsg
    allmsg = list(mensagens)
    ordenar()
    return dict(msg = list(allmsg))

@post('/servidor') # or @route('/login', method='POST')
def do_login():
    t = request.forms.getunicode('text')
    u = request.forms.getunicode('username')

    vc.increment()
    a = (u, t, frozendict(vc.vectorClock))
    mensagens.add(a)
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
    return json.dumps([(n, m, dict(t)) for (n, m, t) in mensagens])

def getMessagesFrom(p):
    link = "http://" + p + "/messages"
    try:
        r = requests.get(link)
        if r.status_code == 200:
            obj = json.loads(r.text)
            setT = set((a, b, frozendict(c)) for [a, b, c] in obj)
            return setT
    except:
        print("Connection Error")
    return set([])

def attmessage():
    while True:
        time.sleep(1)
        global mensagens
        for p in peers:
            time.sleep(1)
            m = getMessagesFrom(p)
            for (n, m, t) in m.difference(mensagens):
                vc.update(t)
                mensagens.add((n, m, t))

t = threading.Thread(target=client)
t.start()

t1 = threading.Thread(target=attmessage)
t1.start()

run(host = 'localhost', port = int(sys.argv[1]))
