# Welcome to the contributing guide for circuits!

## Team members

- James Mills [@prologic](https://github.com/prologic) (*Project Author and Maintainer*)
- [@Osso](https://github.com/Osso)
- [@treemo](https://github.com/treemo)
- [@spaceone](https://github.com/spaceone)
- [@y0no](https://github.com/y0no)

## Learn & listen

* Mailing list: [circuits-dev](https://groups.google.com/forum/#!forum/circuits-dev)
* IRC channel: [#circuits](http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4)
	           on the [FreeNode IRC Network](http://freenode.net/) (``irc.freenode.net``).\
* Blog: [James Mills circuits Blog](http://shortcircuit.net.au/~prologic/blog/tag/circuits/)

## Adding new features

Got a great new feature you'd like to add? Great! First let's discuss it either on
the [#circuits](http://webchat.freenode.net/?randomnick=1&channels=circuits&uio=d4) IRC Channel
or create a new [Discussion Issue](https://github.com/circuits/circuits/issues/new).

Once we're all on the same page and we've nutted down the design and requirements together
let's get you hacking and take ownership of the new feature!

* [Fork circuits](https://github.com/circuits/circuits/issues/14#fork-destination-box)
* Clone your newly created fork:

```bash
$ git clone git@github.com:myuser/circuits.git
```

* Create a new feature branch:

```bash
$ git checkout -b my-feature master
```

* Hack on your feature with your favorite editor or IDE!
* Commit and Push your changes up:

```bash
$ git add -A
$ git commit -m "my fancy new feature. Closes #xx"
$ git push -u origin my-feature
```

* Create a new [Pull Request](https://github.com/circuits/circuits/compare/)

That's it! Six easy steps to contributing a new feature!

Generally we'll respond pretty quickly to new issues, pull requests and general
discussions on IRC. So come and join us!

# Reporting Bugs

Found a bug? Great! We wants to help fix it!

* File a new [Bug Report](https://github.com/circuits/circuits/issues/new)
* Label it as a "Bug"

When describing your bug report; please be concise and as detailed as you can
so we can easily work out what the problem is. It's also very helpful if you
are able to provide a test case that repeatedly demonstrates the bug at hand:

Example:

```python
from circuits import Event, Component


class test(Event):
    """test Event"""


class App(Component):

	message = None

    def started(self):
		self.message = "Hello World!"
		self.stop()


def test():
	App().run()

	assert app.message == "Hello World!"
```

Obviously this test *would pass* but this is ideally what we'd like to see bug reports in the
form of; a reliable, repeatable way of demonstrating the bug.

If you don't feel comfortable writing a test case; a good description is enough!
(*We'll take care of the hard work of ensuring the bug never occurs again!*)

# Documentation

Please help us with [Documentation](http://circuits.readthedocs.org/)

Our documentation is written in [reStructuredText](http://en.wikipedia.org/wiki/ReStructuredText)
using the [Sphinx](http://sphinx-doc.org/) documentation toolkit.

See: [Documentation Sources](https://github.com/circuits/circuits/tree/master/docs)

You can contribute in these easy steps:

1. Navigate our [Documentation Sources](https://github.com/circuits/circuits/tree/master/docs)
2. Find a document you wish to improve.
3. Click on the Pen (*Edit this file*) button.
4. Make your changes and submit a new Pull Request using the Github editor

See: [Editing files in another user's repository](https://help.github.com/articles/editing-files-in-another-user-s-repository/)

# Community 
This section includes ideas on how non-developers can help with the project. Here's a few examples:

* You can help us answer questions our users have here: [StackOverflow circuits-framework](http://stackoverflow.com/questions/tagged/circuits-framework)
* You can help build and design our website here: [circuitsframework.com](https://github.com/circuits/circuitsframework.com)
* You can help write blog posts about the project by: sharing them with the [Community](http://circuitsframework.com/Community)
* You can tweet about your use of circuits and tag [@pythoncircuits](https://twitter.com/pythoncircuits)

* Create an example of the project in real world by building something or showing what others have built. 
* Write about other people’s projects based on this project. Show how it’s used in daily life. Take screenshots and make videos!

----

If you have further questions, contact: [James Mills](mailto:prologic+circuits@shortcircuit.net.au) ([@therealprologic](https://twitter.com/therealprologic)
