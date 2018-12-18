
# lwm2mclient

A customizable LWM2M client written in Python 3.

# Installation

* Prerequisite: Download and install [Python 3.5+](https://www.python.org/downloads/).
* run ``python3 setup.py install`` (for system-wide installation) or
* ``python3 setup.py install --user`` (for user-local installation).

# Usage

## Running The Client

Use ``python3 leshan_client.py`` command to connect to Leshan public LWM2M server
(Make sure to create a secure client with PSK here first [Leshan](https://leshan.eclipse.org/#/security)
also edit leshan_client.py to match your configured client. Remember PSK is in ASCII, but Leshan uses hex!).

## Client Data Model

The data for LWM2M objects hold by the client is represented in the file ``data.json``. The data model
for well-defined LWM2M objects (e.g. Device object) must match the object data definition
specified in ``lwm2m-object-definitions.json``. For custom objects, both files must be adjusted.

## Execute Operations

Resources which provide an execute operation, are specified via string in ``data.json``. The
string name is evaluated to a method name, which should be contained in ``handlers.py``.
The signature for such a handler is  
  
  ```
      def method_name(*args, **kwargs):
         ...
  ```
  
The positional ``args`` arguments are not used. Provided arguments such as ``model``, ``path``, 
``payload`` and ``content_format`` are contained in the ``kwargs`` dictionary. See existing
handlers for example.

## Observe Operations

Resources which support Observe operations, must also be defined in ``handlers.py``. 
The signature of a handler for observe on object/instance/resource follows a convention:  

```
def observe_{object_id}_{instance_id}_{resource_id}(*args, **kwargs):
   ...
```
  
The positional ``args`` arguments are not used. Provided arguments such as ``notifier``, ``cancel``, 
``model``, ``path``,  ``payload`` and ``content_format`` are contained in the ``kwargs`` dictionary.  
A ``notifier`` argument is a function, which triggers a client-initiated notification and may be, e.g. called
periodically.  
A ``cancel`` argument can be used in order to cancel an existing observation.
See ``observe_3_0_13()`` example in ``handlers.py`` on how to trigger a periodic observation.  

Please observe that Leshan uses Passive Observe Cancel, which is currently not supported by aiocoap/this client.
See more information here: https://tools.ietf.org/html/rfc7641#section-3.6

# License

This project is licensed under the terms of [MIT License](LICENSE).

# ToDo

* [x] implement TLV encoding
* [x] implement Execute (via handlers)
* [x] implement Observe (via handlers)
* [x] implement Write 
* [ ] implement Cancel Observation (when [this issue](https://github.com/chrysn/aiocoap/issues/30) is resolved)
* [ ] improve data definition validation
* [ ] extend with REST API (for instrumenting it using 3rd party software)
* [ ] provide Dockerfile
* [x] add DTLS support
* [ ] tests, docs & stuff
* [ ] fulfill SCRs from OMA (s. Tech Spec)
