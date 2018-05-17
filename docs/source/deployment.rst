Deploying the application to Kubernetes
=======================================

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
   
