Deploying the application to Kubernetes
=======================================

Deploying:
----------

On the master issue the following command::

   $ kubectl apply -f demoApplication/k8s/pvc.yml
   persistentvolumeclaim "test-cinder-volume" created

This will create a 3Gi volume in the AZ ``de-nbg6-1a``.
You can see this volume details with::

   $ kubectl get pvc

You can now deploy the application with::

   $ kubectl apply -f demoApplication/k8s/deployment.yml
   deployment.apps "test-cinder" created

   $ kubectl get deployment
   NAME          DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
   test-cinder   1         1         1            0           6s

   $ kubectl get pods
   NAME                          READY     STATUS              RESTARTS   AGE
   test-cinder-568c454cf-x4j87   0/1       ContainerCreating   0          12s

It takes about 1 minute for the container to start and mount the correct
volume::

   NAME                          READY     STATUS    RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-x4j87   1/1       Running   0          2m        10.233.74.3   node-3-nude

You can now see that the pod is running on ``node-3``.

Getting infromation about the pod
---------------------------------

You can get more info on the pod with::

   kubectl describe pod test-cinder-568c454cf-x4j87

This command will output a long YAML. What is really interesting here is the
last section:

.. code:: yaml

   Events:
     Type    Reason                 Age   From                  Message
     ----    ------                 ----  ----                  -------
     Normal  Scheduled              3m    default-scheduler     Successfully assigned test-cinder-568c454cf-x4j87 to node-3-nude
     Normal  SuccessfulMountVolume  3m    kubelet, node-3-nude  MountVolume.SetUp succeeded for volume "default-token-hj8cc"
     Normal  SuccessfulMountVolume  3m    kubelet, node-3-nude  MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
     Normal  Pulling                3m    kubelet, node-3-nude  pulling image "oz123/cinder-test"
     Normal  Pulled                 3m    kubelet, node-3-nude  Successfully pulled image "oz123/cinder-test"
     Normal  Created                3m    kubelet, node-3-nude  Created container
     Normal  Started                3m    kubelet, node-3-nude  Started container

Here we can clearly see which volume was attached to the pod. We also see, that
an open stack volume was created for us without any typing any openstack command.
We can verify this with::

   kubectl get pvc test-cinder-volume

   NAME                 STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS         AGE
   test-cinder-volume   Bound     pvc-12ff0316-53bd-11e8-8b74-fa163e141d50   3Gi        RWO            default-de-nbg6-1a   7d

Using ``openstack`` command line tool::

   $ openstack volume show kubernetes-dynamic-pvc-12ff0316-53bd-11e8-8b74-fa163e141d50

Exposing the application
------------------------

This will add a load balancer to expose the application::

   $ kubectl apply -f cinder-test/demoApplication/k8s/service.yml
   service "test-cinder" created

Then you can find the external IP of the service with::

   $ kubectl get svc test-cinder
   NAME          TYPE           CLUSTER-IP      EXTERNAL-IP    PORT(S)        AGE
   test-cinder   LoadBalancer   10.233.62.244   10.36.60.138   80:31480/TCP   2m

Creating a database
-------------------

At these point the application is still not ready, as it is missing a properly
configure database. Hence if you browse to the external IP address you will
get an error. This is easily fixed with::

   $ kubectl exec test-cinder-568c454cf-x4j87 python manage.py initdb

Now you can add users to the database via the curl command describe in the WebUI
or via ``kubectl exec test-cinder-568c454cf-x4j87  python manage.py adduser``.
