Purpose of this repository
==========================

Evaluate Cinder as a storage backend for K8S.

Tested on Ubuntu 16.04 + Kubespray v2.5.0 on top of OpenStack.

## note

This version of kubespray installs an outdated version of k8s, which
still uses the internal cloud provider. If you use a newer version of
kuberentes (1.12.X) or later you should use the [external cloud provider
for open stack][1]

[1]: https://github.com/kubernetes/cloud-provider-openstack 

Description of the test:
------------------------


## The application

This repository contains a simple web application written in Python.
The application has two end points, one that lists users from a database, and one
which allows to create users via a JSON post.

To run the application:

```
cd demoApplication/src/
python3 manage serve -H 0.0.0.0
```

You can add users to the database via:

```
cd demoApplication/test/
make user MAIL=foo@exmaple.com USER=foo
make user MAIL=bar@exmaple.com USER=bar
```

You can view the users by browsing to the IP address of the machine where the application is running:

```
firefox http://<ip_of_host>:8080
```

### Building a docker image

```
cd demoApplication/src
sudo docker build -t oz123/cinder-test .
```

#### Launch the application with docker

```
sudo docker run --rm -p 8080:8080 --name test-cinder5 oz123/cinder-test
```

Browse to the public IP of the computer on port 8080, you should see an error, 
on the terminal running docker you should see:

```
Traceback (most recent call last):
  File "/app/tiny/peewee.py", line 2569, in execute_sql
    cursor.execute(sql, params or ())
sqlite3.OperationalError: no such table: user

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/tiny/bottle.py", line 1000, in _handle
    out = route.call(**args)
  File "/app/tiny/bottle.py", line 2003, in wrapper
    rv = callback(*a, **ka)
  File "/app/tiny/bottle_peewee.py", line 62, in wrapper
    rv = callback(*args, **kwargs)
  File "/app/app/views.py", line 27, in list
    users='<br>'.join(str(u) for u in User.select())
  File "/app/tiny/peewee.py", line 5648, in __iter__
    self.execute()
  File "/app/tiny/peewee.py", line 1514, in inner
    return method(self, database, *args, **kwargs)
  File "/app/tiny/peewee.py", line 1585, in execute
    return self._execute(database)
  File "/app/tiny/peewee.py", line 1739, in _execute
    cursor = database.execute(self)
  File "/app/tiny/peewee.py", line 2582, in execute
    return self.execute_sql(sql, params, commit=commit)
  File "/app/tiny/peewee.py", line 2576, in execute_sql
    self.commit()
  File "/app/tiny/peewee.py", line 2369, in __exit__
    reraise(new_type, new_type(*exc_args), traceback)
  File "/app/tiny/peewee.py", line 176, in reraise
    raise value.with_traceback(tb)
  File "/app/tiny/peewee.py", line 2569, in execute_sql
    cursor.execute(sql, params or ())
tiny.peewee.OperationalError: no such table: user
```

run the following command to initialize the database:

```
 sudo docker run --rm -e DATABASE_DIR=/app/vol -v $(pwd)/vol:/app/vol -it oz123/cinder-test python3 /app/manage.py initdb
```

Add a user in the database:

```
sudo docker run --rm -p 8080:8080 -e DATABASE_DIR=/app/vol -v $(pwd)/vol:/app/vol -it oz123/cinder-test /app/manage.py adduser foo foo@example.com s3kr35
```

Run the application with:

```
sudo docker run --rm -p 8080:8080 -e DATABASE_DIR=/app/vol -v $(pwd)/vol:/app/vol -it oz123/cinder-test
```

K8S cluster
-----------

Make sure you define two storage classes for the cluster in noris.cloud.
You should apply the files in `k8s/storageClasses`:

```
kubectl apply -f k8s/storageClasses/default-storageClass-de-nbg6-1a.yml
kubectl apply -f k8s/storageClasses/default-storageClass-de-nbg6-1b.yml
```

Building the documentation
--------------------------

You need to have python-sphinx installed. On Debian bases systems do:
```
apt-get install python3-sphinx
```

To build the docs:

```
cd docs
make html # to build html docs
```

