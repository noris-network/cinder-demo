Testing Node Failure with Cinder
================================

Deployment update strategies
----------------------------
Kubernetes takes care of scheduling pods on the correct node.
When deploying a stateless application, Kuberentes will upgrade
pods using the default update strategy, which is a rolling update
strategy.
This means that when one tries to delete a pods or update,
Kuberentes will first try to schedule another pod to
replace the pod deleted.
Only when the new updated pod is in place and running, kuberentes
will actually destroy the deleted pod. These guarantees minimal
down time the application.

When using the default update startegy, one can not update stateful
applications in this ways. The reasone for that is that the new
pod can not attach the volume if it is attached to an already running
volume. Hence it will fail to start and might enter a failed state.

This true in Kubernetes version 1.9.X where detaching a volume from
a pod was broken on OpenStack::

  $ kubectl get pods
  NAME                          READY     STATUS    RESTARTS   AGE
  test-cinder-568c454cf-x4j87   1/1       Running   0          3h

  $ kubectl delete pods test-cinder-568c454cf-x4j87
  pod "test-cinder-568c454cf-x4j87" deleted
  $ kubectl get pods
  NAME                          READY     STATUS              RESTARTS   AGE
  test-cinder-568c454cf-sqxp9   0/1       ContainerCreating   0          1s
  test-cinder-568c454cf-x4j87   1/1       Terminating         0          3h

On Kubernetes 1.9.X newly created pod would have been scheduled on the same
node where the volume is attached. But it would not get out of the state
``ContainerCreating``.

As a work around one could have changed the deployment update strategy to:

.. code:: yaml

   strategy:
     type: Recreate

In this case the deployment would first completely tear down the container
and then restart the pod with the container attaching to the correct volume.

This however will not work in the case of a node failure, because a Cinder
volume is attached to a node. In the case of node shutdown or crashing,
the volume would not be released, and what so ever update startegy is
applied a new pod would not start.
Exmaining a pod with ``kubectl describe pod test-cinder-xxx`` would show:

.. code:: yaml

   QoS Class:       BestEffort
   Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
   Tolerations:     <none>
   Events:
     Type     Reason                 Age              From                     Message
     ----     ------                 ----             ----                     -------
     Normal   Scheduled              1m               default-scheduler        Successfully assigned test-cinder-56bdb546dd-9vdsj to node-3-nude
     Normal   SuccessfulMountVolume  1m               kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
     Warning  FailedMount            1m (x3 over 1m)  attachdetach-controller  AttachVolume.Attach failed for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" : disk 4e41d530-cb5f-49a9-9c6f-a591abdb6f11 is attached to a different instance (9454752c-f0e2-4447-9b7f-16434c49f7ac)


Manual intervention is now needed to detach the volume from the host::

   openstack server remove volume 9454752c-f0e2-4447-9b7f-16434c49f7ac 4e41d530-cb5f-49a9-9c6f-a591abdb6f11


Failure and detaching in Kubernetes 1.10.x
------------------------------------------

Version 1.10 fixed this issue and can now detach volumes from active hosts
as well as terminated host. ``RollingUpdate`` as well as ``Recrate`` can
be applied for stateful deployments.

First, verify the strategy type::

   echo `kubectl get deployment  -o=jsonpath='{.items[].spec.strategy.type}'`

Then, test that you can delete the application pods, and the it can restart
without interruption::

   $ kubectl get pods -o wide
   NAME                          READY     STATUS    RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-sqxp9   1/1       Running   0          17m       10.233.74.4   node-3-nude
   $ kubectl delete pod test-cinder-568c454cf-sqxp9
   pod "test-cinder-568c454cf-sqxp9" deleted
   $ kubectl get pods -o wide
   NAME                          READY     STATUS              RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-sqxp9   1/1       Terminating         0          17m       10.233.74.4   node-3-nude
   test-cinder-568c454cf-v5qtc   0/1       ContainerCreating   0          1s        <none>        node-3-nude
   $ kubectl get pods -o wide
   NAME                          READY     STATUS              RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-sqxp9   1/1       Terminating         0          17m       10.233.74.4   node-3-nude
   test-cinder-568c454cf-v5qtc   0/1       ContainerCreating   0          9s        <none>        node-3-nude
   $ kubectl get pods -o wide
   NAME                          READY     STATUS              RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-sqxp9   1/1       Terminating         0          18m       10.233.74.4   node-3-nude
   test-cinder-568c454cf-v5qtc   0/1       ContainerCreating   0          13s       <none>        node-3-nude
   $ kubectl get pods -o wide
   NAME                          READY     STATUS        RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-sqxp9   1/1       Terminating   0          18m       10.233.74.4   node-3-nude
   test-cinder-568c454cf-v5qtc   1/1       Running       0          16s       10.233.74.5   node-3-nude

This demonstrates the the original container is destroyed and started with a new IP address.
The whole time you can reach the application via the Web UI, which will show something like::

   foo|foo@examle.com
   My pod name: test-cinder-568c454cf-v5qtc
   My node name node-3-nude

In some cases Kubernetes will schedule the pod to start on a new node::

   $ kubectl get pods -o wide
   NAME                          READY     STATUS    RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-v5qtc   1/1       Running   0          1h        10.233.74.5   node-3-nude
   $ kubectl delete pods test-cinder-568c454cf-v5qtc
   pod "test-cinder-568c454cf-v5qtc" deleted

   $ kubectl get pods -o wide
   NAME                          READY     STATUS              RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-s8qfm   0/1       ContainerCreating   0          1s        <none>        node-4-nude
   test-cinder-568c454cf-v5qtc   1/1       Terminating         0          1h        10.233.74.5   node-3-nude
   $ kubectl get pods -o wide
   NAME                          READY     STATUS              RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-s8qfm   0/1       ContainerCreating   0          9s        <none>        node-4-nude
   test-cinder-568c454cf-v5qtc   1/1       Terminating         0          1h        10.233.74.5   node-3-nude

In such case you can clearly see the Pod receiving an error, and detaching the volume from one node to another::

   $ kubectl describe pod test-cinder-568c454cf-s8qfm
   ...
   Events:
     Type     Reason                  Age   From                     Message
     ----     ------                  ----  ----                     -------
     Normal   Scheduled               9m    default-scheduler        Successfully assigned test-cinder-568c454cf-s8qfm to node-4-nude
     Warning  FailedAttachVolume      9m    attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already used by pod(s) test-cinder-568c454cf-v5qtc
     Normal   SuccessfulMountVolume   9m    kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
     Normal   SuccessfulAttachVolume  9m    attachdetach-controller  AttachVolume.Attach succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
     Normal   SuccessfulMountVolume   8m    kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
     Normal   Pulling                 8m    kubelet, node-4-nude     pulling image "oz123/cinder-test"
     Normal   Pulled                  8m    kubelet, node-4-nude     Successfully pulled image "oz123/cinder-test"
     Normal   Created                 8m    kubelet, node-4-nude     Created container
     Normal   Started                 8m    kubelet, node-4-nude     Started container

Failure of a node
-----------------

Here we demonstrate what happens when we shut a node down::

   $ kubectl get pods -o wide
   NAME                          READY     STATUS    RESTARTS   AGE       IP            NODE
   test-cinder-568c454cf-s8qfm   1/1       Running   0          15m       10.233.68.2   node-4-nude

   $ ssh node-4-nude sudo shutdown -h now
   Connection to node-4-nude closed by remote host.

Now node 4 is not availabe anymore::

   $ kubectl get nodes
   NAME            STATUS    ROLES     AGE       VERSION
   master-1-nude   Ready     master    8d        v1.10.2+coreos.0
   master-2-nude   Ready     master    8d        v1.10.2+coreos.0
   node-1-nude     Ready     node      8d        v1.10.2+coreos.0
   node-2-nude     Ready     node      8d        v1.10.2+coreos.0
   node-3-nude     Ready     node      4m        v1.10.2+coreos.0

The pod will error trying to mount the volume, but after about 2 minutes it will
start::

   $ kubectl get pods
   NAME                          READY     STATUS              RESTARTS   AGE
   test-cinder-568c454cf-v5qtc   0/1       ContainerCreating   0          13s       <none>        node-3-nude

   kubectl describe test-cinder-568c454cf-v5qtc
   ...
   Events:
    Type     Reason                  Age   From                     Message
    ----     ------                  ----  ----                     -------
    Normal   Scheduled               3m    default-scheduler        Successfully assigned test-cinder-568c454cf-qh4ph to node-3-nude
    Warning  FailedAttachVolume      3m    attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already exclusively attached to one node and can't be attached to another
    Normal   SuccessfulMountVolume   3m    kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
    Warning  FailedMount             1m    kubelet, node-3-nude     Unable to mount volumes for pod "test-cinder-568c454cf-qh4ph_default(b9cc0d18-59d9-11e8-ae02-fa163ed08711)": timeout expired waiting for volumes to attach or mount for pod "default"/"test-cinder-568c454cf-qh4ph". list of unmounted volumes=[database]. list of unattached volumes=[database default-token-hj8cc]
    Normal   SuccessfulAttachVolume  32s   attachdetach-controller  AttachVolume.Attach succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
    Normal   SuccessfulMountVolume   29s   kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
    Normal   Pulling                 18s   kubelet, node-3-nude     pulling image "oz123/cinder-test"
    Normal   Pulled                  15s   kubelet, node-3-nude     Successfully pulled image "oz123/cinder-test"
    Normal   Created                 14s   kubelet, node-3-nude     Created container
    Normal   Started                 14s   kubelet, node-3-nude     Started container

