The following describes the steps how to test cinder.

THIS IS STILL NOT PROOF read, and I probably still forgot shit load of stuff
I did in the way.


ubuntu@work-oz:~$ kubectl get pods
NAME                                             READY     STATUS              RESTARTS   AGE
test-cinder-56bdb546dd-szgmd                     0/1       ContainerCreating   0          7m
zeroed-cheetah-sonatype-nexus-6bc778b649-m574p   1/1       Running             0          7h


Tolerations:     <none>
Events:
  Type     Reason                 Age   From                     Message
  ----     ------                 ----  ----                     -------
  Normal   Scheduled              2m    default-scheduler        Successfully assigned test-cinder-56bdb546dd-szgmd to node-4-nude
  Warning  FailedAttachVolume     2m    attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already exclusively attached to one node and can't be attached to another
  Normal   SuccessfulMountVolume  2m    kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"


Shut down both nodes on AZ-1a
```
ubuntu@master-1-nude:~$ kubectl get nodes
NAME            STATUS    ROLES     AGE       VERSION
master-1-nude   Ready     master    9h        v1.9.2+coreos.0
master-2-nude   Ready     master    9h        v1.9.2+coreos.0
node-1-nude     Ready     node      9h        v1.9.2+coreos.0
node-2-nude     Ready     node      9h        v1.9.2+coreos.0

```
The container now will be pending
```
ubuntu@master-1-nude:~$ kubectl get pods
NAME                                             READY     STATUS    RESTARTS   AGE
test-cinder-56bdb546dd-gw5tv                     0/1       Pending   0          1m
zeroed-cheetah-sonatype-nexus-6bc778b649-lmxz2   0/1       Pending   0          1m
```

That is becuase k8s won't be able to schedule it:

```
Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason            Age               From               Message
  ----     ------            ----              ----               -------
  Warning  FailedScheduling  9s (x7 over 40s)  default-scheduler  0/4 nodes are available: 2 PodToleratesNodeTaints, 3 NoVolumeZoneConflict.

```
ubuntu@master-1-nude:~$ kubectl get nodes
NAME            STATUS    ROLES     AGE       VERSION
master-1-nude   Ready     master    9h        v1.9.2+coreos.0
master-2-nude   Ready     master    9h        v1.9.2+coreos.0
node-1-nude     Ready     node      9h        v1.9.2+coreos.0
node-2-nude     Ready     node      9h        v1.9.2+coreos.0
node-4-nude     Ready     node      4s        v1.9.2+coreos.0
ubuntu@master-1-nude:~$ kubectl get pods
NAME                                             READY     STATUS              RESTARTS   AGE
test-cinder-56bdb546dd-gw5tv                     0/1       ContainerCreating   0          2m
zeroed-cheetah-sonatype-nexus-6bc778b649-lmxz2   0/1       ContainerCreating   0          2m
ubuntu@master-1-nude:~$ 
```

Now it will fail again, because the volume is still marked as attached:

```
  Type     Reason                 Age               From                     Message
  ----     ------                 ----              ----                     -------
  Warning  FailedScheduling       2m (x11 over 4m)  default-scheduler        0/4 nodes are available: 2 PodToleratesNodeTaints, 3 NoVolumeZoneConflict.
  Normal   Scheduled              2m                default-scheduler        Successfully assigned test-cinder-56bdb546dd-gw5tv to node-4-nude
  Normal   SuccessfulMountVolume  2m                kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Warning  FailedMount            30s               kubelet, node-4-nude     Unable to mount volumes for pod "test-cinder-56bdb546dd-gw5tv_default(2f47dbcd-53c1-11e8-8b74-fa163e141d50)": timeout expired waiting for volumes to attach/mount for pod "default"/"test-cinder-56bdb546dd-gw5tv". list of unattached/unmounted volumes=[database]
  Warning  FailedMount            18s (x9 over 2m)  attachdetach-controller  AttachVolume.Attach failed for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" : disk 4e41d530-cb5f-49a9-9c6f-a591abdb6f11 is attached to a different instance (3901d974-751e-4ba7-acfa-9cd583c6729d)
```

remove the deployment with `kubectl delete deploy test-cinder` will still not mark it as free:

ubuntu@master-1-nude:~$ kubectl get pvc
NAME                            STATUS    VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS         AGE
test-cinder-volume              Bound     pvc-12ff0316-53bd-11e8-8b74-fa163e141d50   3Gi        RWO            default-de-nbg6-1a   36m
zeroed-cheetah-sonatype-nexus   Bound     pvc-8f92feb1-537d-11e8-8b74-fa163e141d50   8Gi        RWO            default-de-nbg6-1a   8h


kubectl describe pod test-cinder-56bdb546dd-xz8px
```
Volumes:
  database:
    Type:       PersistentVolumeClaim (a reference to a PersistentVolumeClaim in the same namespace)
    ClaimName:  test-cinder-volume
    ReadOnly:   false
  default-token-hj8cc:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-hj8cc
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason                 Age   From                     Message
  ----     ------                 ----  ----                     -------
  Normal   Scheduled              1m    default-scheduler        Successfully assigned test-cinder-56bdb546dd-xz8px to node-4-nude
  Normal   SuccessfulMountVolume  1m    kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Warning  FailedMount            1m    attachdetach-controller  AttachVolume.Attach failed for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" : disk 4e41d530-cb5f-49a9-9c6f-a591abdb6f11 is attached to a different instance (3901d974-751e-4ba7-acfa-9cd583c6729d)
```

If you now detach the volume in openstack, and reapply the deployment you will see the container comming back to life with
the correct volume mounted.

TODO: check if this is possible to do automatic failover with StatefulSet

With the correct startegy you can do automatic restart without deleting the deployment:

You should see :


```
Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason                 Age   From                     Message
  ----     ------                 ----  ----                     -------
  Normal   Scheduled              1m    default-scheduler        Successfully assigned test-cinder-56bdb546dd-b9t6x to node-4-nude
  Warning  FailedAttachVolume     1m    attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already exclusively attached to one node and can't be attached to another
  Normal   SuccessfulMountVolume  1m    kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Normal   SuccessfulMountVolume  23s   kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
  Normal   Pulling                12s   kubelet, node-4-nude     pulling image "oz123/cinder-test"
  Normal   Pulled                 11s   kubelet, node-4-nude     Successfully pulled image "oz123/cinder-test"
  Normal   Created                11s   kubelet, node-4-nude     Created container
  Normal   Started                11s   kubelet, node-4-nude     Started container

```

If a nodes is shutdown, the cinder volume is still attached to it. Hence, kubernetes can't start the pods on a
new node, you should see the following error:

```
QoS Class:       BestEffort
Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason                 Age              From                     Message
  ----     ------                 ----             ----                     -------
  Normal   Scheduled              1m               default-scheduler        Successfully assigned test-cinder-56bdb546dd-9vdsj to node-3-nude
  Normal   SuccessfulMountVolume  1m               kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Warning  FailedMount            1m (x3 over 1m)  attachdetach-controller  AttachVolume.Attach failed for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" : disk 4e41d530-cb5f-49a9-9c6f-a591abdb6f11 is attached to a different instance (9454752c-f0e2-4447-9b7f-16434c49f7ac)

```

You need to intervine here and tell openstack to detach the volume:

```
openstack server remove volume 9454752c-f0e2-4447-9b7f-16434c49f7ac 4e41d530-cb5f-49a9-9c6f-a591abdb6f11
```

Now you should remove the failed pods, a new one will be created using the correct volume:

```
ubuntu@work-oz:~$ kubectl get pods
NAME                           READY     STATUS              RESTARTS   AGE
test-cinder-56bdb546dd-9vdsj   0/1       ContainerCreating   0          10m
ubuntu@work-oz:~$ kubectl delete pods test-cinder-56bdb546dd-9vdsj
pod "test-cinder-56bdb546dd-9vdsj" deleted

```

Now the pod will be properly launched.

The manual intervention is a know issue, and is describe in many cases also for EBS (AWS Storage) [1].

According to the release notes this issue is fixed in  k8s 1.10

https://kubernetes.io/docs/imported/release/notes/#openstack-1


With kubelet v1.10:

 volumes.kubernetes.io/controller-managed-attach-detach=true


You should now be able see failover happening automatically:

```

Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason                  Age              From                     Message
  ----     ------                  ----             ----                     -------
  Normal   Scheduled               7m               default-scheduler        Successfully assigned test-cinder-56bdb546dd-56mct to node-4-nude
  Warning  FailedAttachVolume      7m               attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already exclusively attached to one node and can't be attached to another
  Normal   SuccessfulMountVolume   7m               kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Warning  FailedMount             3m (x2 over 5m)  kubelet, node-4-nude     Unable to mount volumes for pod "test-cinder-56bdb546dd-56mct_default(4f51f4ab-5783-11e8-b805-fa163e141d50)": timeout expired waiting for volumes to attach or mount for pod "default"/"test-cinder-56bdb546dd-56mct". list of unmounted volumes=[database]. list of unattached volumes=[database default-token-hj8cc]
  Normal   SuccessfulAttachVolume  1m               attachdetach-controller  AttachVolume.Attach succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
  Normal   SuccessfulMountVolume   1m               kubelet, node-4-nude     MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
  Normal   Pulling                 1m               kubelet, node-4-nude     pulling image "oz123/cinder-test"
  Normal   Pulled                  1m               kubelet, node-4-nude     Successfully pulled image "oz123/cinder-test"
  Normal   Created                 1m               kubelet, node-4-nude     Created container
  Normal   Started                 1m               kubelet, node-4-nude     Started container
ubuntu@work-oz:~$
```

Here is what happens when node-4 is turned off:

```
Node-Selectors:  failure-domain.beta.kubernetes.io/region=de-nbg6-1
Tolerations:     <none>
Events:
  Type     Reason                  Age              From                     Message
  ----     ------                  ----             ----                     -------
  Normal   Scheduled               6m               default-scheduler        Successfully assigned test-cinder-56bdb546dd-gthct to node-3-nude
  Warning  FailedAttachVolume      6m               attachdetach-controller  Multi-Attach error for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50" Volume is already exclusively attached to one node and can't be attached to another
  Normal   SuccessfulMountVolume   6m               kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "default-token-hj8cc"
  Warning  FailedMount             2m (x2 over 4m)  kubelet, node-3-nude     Unable to mount volumes for pod "test-cinder-56bdb546dd-gthct_default(5c6eba2e-5785-11e8-b805-fa163e141d50)": timeout expired waiting for volumes to attach or mount for pod "default"/"test-cinder-56bdb546dd-gthct". list of unmounted volumes=[database]. list of unattached volumes=[database default-token-hj8cc]
  Normal   SuccessfulAttachVolume  45s              attachdetach-controller  AttachVolume.Attach succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
  Normal   SuccessfulMountVolume   41s              kubelet, node-3-nude     MountVolume.SetUp succeeded for volume "pvc-12ff0316-53bd-11e8-8b74-fa163e141d50"
  Normal   Pulling                 31s              kubelet, node-3-nude     pulling image "oz123/cinder-test"
  Normal   Pulled                  29s              kubelet, node-3-nude     Successfully pulled image "oz123/cinder-test"
  Normal   Created                 29s              kubelet, node-3-nude     Created container
  Normal   Started                 29s              kubelet, node-3-nude     Started container

```

The output should be like this when following the podes:

```
ubuntu@work-oz:~/cinder-test/demoApplication/src$ kubectl get pods -o wide
NAME                          READY     STATUS              RESTARTS   AGE       IP        NODE
test-cinder-568c454cf-dkwp8   0/1       Terminating         0          3m        <none>    node-4-nude
test-cinder-568c454cf-rfzd6   0/1       ContainerCreating   0          32s       <none>    node-3-nude
```

```
ubuntu@work-oz:~$ kubectl get pods -o wide -w
NAME                           READY     STATUS    RESTARTS   AGE       IP            NODE
test-cinder-56bdb546dd-56mct   1/1       Running   0          14m       10.233.69.2   node-4-nude
test-cinder-56bdb546dd-56mct   1/1       Running   0         14m       10.233.69.2   node-4-nude
test-cinder-56bdb546dd-56mct   1/1       Terminating   0         14m       10.233.69.2   node-4-nude
test-cinder-56bdb546dd-gthct   0/1       Pending   0         0s        <none>    <none>
test-cinder-56bdb546dd-56mct   1/1       Terminating   0         14m       10.233.69.2   node-4-nude
test-cinder-56bdb546dd-gthct   0/1       Pending   0         0s        <none>    node-3-nude
test-cinder-56bdb546dd-gthct   0/1       ContainerCreating   0         0s        <none>    node-3-nude
test-cinder-56bdb546dd-gthct   1/1       Running   0         6m        10.233.70.2   node-3-nude
```

Conclusion: Failover works in Cinder + Kubespray (v2.4.0) on top of OpenStack with Kubernetes 1.10


### caveats

It seems unmount the volume tend to crash the hosts! Both node-3 where the volume is mounted and the node-4
where the volume should be mounted  ...

While forcing the volume to detach and attach to another machine, this only happens within 1 availability zone.
Users of Cinder volumes must manualy taking care of backup to a volume in another AZ in case of the active AZ
is down.
In case of a Database server one could create a stand-by replica in a second AZ, and a mathching application
deployment which is alreay reading from the Replica. In case of an event, the service is then configured
to expose the stand-by deployment.


[1]: https://dzone.com/articles/fixing-kubernetes-failedattachvolume-and-failed-mo
