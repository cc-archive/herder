Herder Events
=============

Herder uses a simple event dispatch model to reduce coupling and allow
for simple extensibility.  The Herder event dispatch model uses
``zope.event`` and ``zope.component``.


Events
------

Herder defines the following events:

* MessageUpdateEvent

Handler Registration
--------------------

Event handlers are declared as adapters for the specific event type.
The event model is class based so declaring an adapter for
``HerderEvent`` (the base of all built-in Herder events) will catch
all events that are ``HerderEvent`` sub-classes as well.

For example::

  @zope.component.handler(HerderEvent)
  def handler(event):
      """Process the event, which is guaranteed to be an instance of
      HerderEvent or a sub-class."""

To complete the registration you need to let the component system 
know about the handler::

  zope.component.provideHandler(handler)

Start-up Registration
---------------------

Herder uses an entry point to streamline registration.  At start up
all entry points in the ``herder.register_handlers`` group are 
enumerated and called with no arguments.  See Herder's ``setup.py`` 
for an example of declaring a registration function.
