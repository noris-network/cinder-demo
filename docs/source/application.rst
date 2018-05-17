The application
===============

A simple web application written in Python is found in
the directory demoApplication_.

.. _demoApplication: https://gitlab.noris.net/PI/cinder-test/tree/master/demoApplication

The application dependencies are also found in the same directory.

The application has two end points, one that lists users from a database, and one
which allows to create users via a JSON Post request.

Running the application locally
-------------------------------
The application can be run locally using Python's built-in webserver:

.. code:: shell

   cd demoApplication/src/
   python3 manage.py initdb
   python3 manage.py serve -H 0.0.0.0

You can view the users by browsing to the IP address of the machine where the
application is running:


.. code::

   firefox http:://localhost:8080


Building a docker image and running the application in docker
-------------------------------------------------------------

Inside the source repository::


   cd demoApplication/src
   sudo docker build -t oz123/cinder-test .

Now you have successfully created a docker image. To run the application you
first need to create a database::

   sudo docker run --rm -e DATABASE_DIR=/app/vol -v $(pwd)/vol:/app/vol \
      -it oz123/cinder-test python3 /app/manage.py initdb

Now add a user to this database with::

   sudo docker run --rm -p 8080:8080 -e DATABASE_DIR=/app/vol \
      -v $(pwd)/vol:/app/vol -it oz123/cinder-test /app/manage.py \
      adduser foo foo@example.com s3kr35

Finally run the application inside docker::

   sudo docker run --rm -p 8080:8080 -e DATABASE_DIR=/app/vol -v $(pwd)/vol:/app/vol -it oz123/cinder-test

Check that the application is running::

   firefox http:://localhost:8080

If everything works well, push the application image to docker with::

   docker login
   docker push oz123/cinder-test
