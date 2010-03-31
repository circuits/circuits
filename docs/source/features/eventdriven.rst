Event Driven
============

circuits is **Event Driven**.

This means that everything you do in a circuits-based application or system
is the reaction to or exposure of some kind of "Event". Components communicate
with one another by passing back and forth events on various channels. Each
Component itself also defines it's own channel (*sub channel*) which allows
two or more components with similar events to co-exist without interfering
with each other.
