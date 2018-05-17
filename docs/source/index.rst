.. Cinder Test documentation master file, created by
   sphinx-quickstart on Wed May 16 13:02:07 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cinder Test
===========

About this document:
--------------------

These docs describe how we evaluted Cinder as a dynamic storage backend
for Kubernetes on OpenStack.

The Test setup
~~~~~~~~~~~~~~

A Kubernetes cluster build with `Kubespray_` on top of Ubuntu 16.04 Virtual
Machines in ``noris.cloud``.


.. _Kubespray: https://github.com/kubernetes-incubator/kubespray

Table of Contents
~~~~~~~~~~~~~~~~~
.. toctree::
   :maxdepth: 2

   Building the test cluster <building>
   The test application <application>
   Testing a machine failure <test>

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
