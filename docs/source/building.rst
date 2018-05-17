Building the test environment
=============================

Creating a kubernetes cluster on OpenStack
------------------------------------------

Install kolt_ and ansible_ on your host.

Follow the instructions in the `kolt`_ repository on how to setup a Kubernetes
cluster. You need at least 2 worker nodes in each availability zone.

Use the file ``k8s/cinder-test-cluster.yml`` as an example:

.. code:: shell

   $ kolt -i cinder-test-cluster.ini k8s/cinder-test-cluster.yml

Use the created inventory to deploy a Kubernetes cluster on your hosts using
ansible:

.. code:: shell

  $ git clone -b 'v2.4.0' --single-branch --depth 1 git@github.com:kubernetes-incubator/kubespray.git

  $ cp cinder-test-cluster.ini kubespray/inventory/

Edit the following entries in ``kubespray/inventory/inventory/group_vars/all.yml``:

.. code:: yaml

   bootstrap_os: ubuntu
   cloud_provider: openstack

in ``kubespray/inventory/group_vars/k8s-cluster.yml``:

.. code:: yaml

   kube_version: v1.10.2

Finally, run ansible:

.. code:: shell

   $ cd kubespray
   $ ansible-playbook -i  inventory/mycluster.ini cluster.yml \
     --ssh-extra-args="-o StrictHostKeyChecking=no" -u ubuntu \
     -e ansible_python_interpreter="/usr/bin/python3" -b --flush-cache


For a list of known problems see the ``README`` in `kolt`_.

.. _kolt: https://gitlab.noris.net/PI/kolt
.. _ansible: https://www.ansible.com/


Preparing your kubernetes cluster
---------------------------------

After you kubernetes cluster is bootstrap you should be able to
execute ``kubectl`` on any of your masters.

You should see at least two nodes in each availability zone by running:


.. code:: shell

   $ ubuntu@master-1-nude:~$ kubectl get nodes --show-labels

You should now create a StorageClass_ for each availability zone.
On the master machine still:

.. code:: shell

   $ git clone https://gitlab.noris.net/PI/cinder-test
   $ kubectl apply -f cinder-test/k8s/storageClasses/default-storageClass-de-nbg6-1a.yml
   $ kubectl apply -f cinder-test/k8s/storageClasses/default-storageClass-de-nbg6-1b.yml

.. _StorageClass: https://kubernetes.io/docs/concepts/storage/storage-classes/
