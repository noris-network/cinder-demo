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
