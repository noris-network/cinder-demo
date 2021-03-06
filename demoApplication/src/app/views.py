import os
import socket

from tiny.bottle import request, HTTPResponse

from .models import User
from .config import app


template = """
<!DOCTYPE html>
<html>
  <head>
     <meta charset="utf-8">
     <title></title>
     <meta name="description" content="">
     <meta name="viewport" content="width=device-width, initial-scale=1">
 </head>
<body>
<div>
{}
<br>
My pod name {}
<br>
My node name {}
</div>
</body>
</html>"""


curl = """
<br>
<code>
curl --header "Content-Type: application/json" \
 --request POST \
 --data '{"name":"${USER}","password":"s3kr3t", "email": "${MAIL}"}' \
 http://Public.Ip.ofThis.Host:8080/usr/
"""


@app.route('/', name='page_finder')
def list(db):
    users = [str(u) for u in User.select()]
    print(users)
    if not users:
        users = "Use the following command to create a user:<p>"
        return users + curl

    users = '<br>'.join(str(u) for u in User.select())
    hostname = '%s' % socket.gethostname()
    nodename = os.getenv('MY_NODE_NAME')
    return template.format(users, hostname, nodename)


@app.post('/usr/', name='insert_user')
def usr(db):
    try:
        data = {k: v for k, v in request.json.items()}
        u = User(**data)
        u.save()
    except Exception as e:
        return HTTPResponse(e.args, 409)
    return HTTPResponse(status=200)
