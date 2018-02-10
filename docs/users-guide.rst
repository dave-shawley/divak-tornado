.. :py:currentmodule:: divak.api
.. _users_guide:

============
User's Guide
============

Application Requirements
========================
.. index:: divak_request_id, Recorder, Application

Your application needs to inherit from :class:`.Recorder` to use divák.
The :class:`.Recorder` class provides methods to inject observers into the
request processing pipeline.  The only notable functionality that it provides
is to ensure that every request has a ``divak_request_id`` attribute that is
set to :data:`None` by default.  Beyond that, it is a strictly *opt-in*
interface in that you must explicitly add observers to enable functionality.

.. include:: tracing.rst
