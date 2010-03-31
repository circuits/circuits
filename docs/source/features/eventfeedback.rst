Event Feedback
==============

Within the core of circuits is a feature called **Event Feedback**. This is a
mechanism that ties into any **Event** object allowing feedback to be given
for a number of criteria:
 * **success**: An optional channel to use for Event Handler success
 * **failure**: An optional channel to use for Event Handler failure
 * **filter**: An optional channel to use if an Event is filtered
 * **start**: An optional channel to use before an Event starts
 * **end**: An optional channel to use when an Event ends

These criterion are specified on the **Event** class as class or instance
attributes and used to trigger an event on the channel specified in the form
of a 2-item tuple: (channel, target)
