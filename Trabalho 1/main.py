from bottle import Bottle, run, template, route, get, post, request, redirect, view

mensagens = []

@get('/cliente') # or @route('/login')
@view('cliente')
def login():
    return dict(msg = mensagens)

@post('/servidor') # or @route('/login', method='POST')
def do_login():
    t = request.forms.getunicode('text')
    u = request.forms.getunicode('username')

    mensagens.append([u, t])
    redirect("/cliente")
    run(reloader=True)

run(host = 'localhost', port = 8081)
