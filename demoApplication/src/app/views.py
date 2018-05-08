from tiny import bottle
from tiny.bottle import request, HTTPResponse
import datetime as dt

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
</div>
</body>
</html>"""

@app.route('/', name='page_finder')
def list(db):
    users='<br>'.join(str(u) for u in User.select())
    return template.format(users)
	
@app.post('/usr/', name='insert_user')
def usr(db):
    try:
        data = {k: v for k, v in request.json.items()}
        u = User(**data)
        u.save()
    except Exception as e:
        return HTTPResponse(e.args, 409)
    return HTTPResponse(status=200)
