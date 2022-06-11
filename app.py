import json
from flask import Flask, render_template, request, \
    redirect, \
    make_response
from model import Manager
import time
import hashlib

app = Flask(__name__)

manager = Manager()
@app.before_first_request
def a():
    manager.client.ltrim('chat_list',0,0)
    manager.client.lpop('chat_list')
    manager.client.delete('userinfo')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        token = request.cookies.get('token')
        if token:
            for i in manager.client.keys():
                try:
                    flag = manager.client.get(
                        i.decode()).decode()
                except:
                    continue
                if flag == token:
                    return redirect('/admin/' + i.decode())
        return render_template('login.html')
    else:
        nick_name = request.json.get('nickname')
        token = request.cookies.get('token')
        if token:
            if manager.check_token(
                    nick_name).decode() == token:
                res = make_response({'message': nick_name})
                res.status = '200'
                return res

        if manager.check_nickname(nick_name):
            res = make_response({'message': '该昵称已经有人在使用!'})
            res.status = '404'
            return res
        else:
            res = make_response({'message': nick_name})
            token = nick_name + str(time.time())
            token = hashlib.md5(
                token.encode('utf-8')).hexdigest()
            manager.set_token(nick_name, token)
            res.set_cookie('token', token)
            res.status = '200'
            return res


@app.route('/admin/<user>')
def admin(user):
    token_ = manager.check_token(user)
    if not token_:
        return redirect('/')
    token = request.cookies.get('token')
    if token == token_.decode():
        message = [json.loads(i) for i in
                   manager.get_message()]
        return render_template('admin.html', user=user,
                               message=message)
    else:
        return redirect('/')


@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'GET':
        message = [json.loads(i) for i in
                   manager.get_message()]
        return {'message': message}
    else:
        content = request.json.get('content')
        user = request.json.get('user')
        date = time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(time.time()))
        manager.client.rpush('chat_list', json.dumps(
            {'user': user, 'time': date, 'msg': content}))
        return {'message': 'add success'}

@app.route('/logout',methods=['POST'])
def logout():
    res = make_response({'message':'logout success'})
    token = request.cookies.get('token')
    if token:
        nickname = request.json.get('nickname')
        manager.client.delete(nickname)
        manager.client.srem('userinfo',nickname)
        res.delete_cookie('token')

    return res

if __name__ == '__main__':
    app.run()
