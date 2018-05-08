Purpose of this repository
==========================

Evaluate Cinder as a storage backend for K8S.

Tested on Ubuntu 16.04 + Kubespray v2.5.0 on top of OpenStack.


Description of the test:
------------------------


1. The application
~~~~~~~~~~~~~~~~~~

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


