
# easy_py_messaging - version 1.0.0
A simple to use python wrapper around ZeroMQ for distributed systems to use for messaging and logging. Especially targeted to Raspberry Pi systems.

## Welcome

The Easy Py Messaging system provides lightweight messaging in a library
which implements a ZeroMQ based messaging to privde logging facilities for
distributed systems.  This robust library uses the excellent ZeroMQ messaging
system to allow easy interfacing with distributed systems.  While
specifically developed for distributed Raspberry Pis and similar systems, it
is easily installed in almost any Linux system. Additionaly, this code works
seamlessly when all processes exist on the same node.

This code contains a synchronous messaging API, a log collector to receive
and store logs, a log filter application to receive, store and filter logs.
Additional support utilities enhance and support this product.

The library contains easy-to-use python classes for interfacing with the lower
level ZeroMQ messaging system. Users will enjoy the simplicity of interfacing
these classes with their own applications. 

The logging system can easily collect logs from remote systems and store
them. Now consolidated log messages eases the problems associated with
monitoring and debugging problems with distributed systems.


## Building and installation

Installation consists of the normal:
``` bash
git clone https://github.com/TrailingDots/easy_py_messaging.git
python setup.py install
```
"sudo" may or may not be required depending upon your particular
system configuration.

### Dependencies

Your system may or may not require additional dependencies.
The project has been careful to provide clean code as determined
by pyflakes, unit test, python lint, etc.

#### Python pip and setup tools

You might need these tools. Mos python developers have these
already installed. See <a href="https://packaging.python.org/install_requirements_linux/">Installing pip/setuptools/wheel with Linux Package Managers</a>.
Windows and OSX are on sister pages.

#### Pyflakes - The passive checker of Python programs

Pyflakes is a code analysis tool for Python. Pyflakes
does not execute code, but rather analyzes the code.
See <a href="https://launchpad.net/pyflakes">pyflakes</a> or
<a href="https://www.blog.pythonlibrary.org/2012/06/13/pyflakes-the-passive-checker-of-python-programs/">pyflakes</a> and follow the
installation instructions.

#### Lizard - for cyclomatic complexity

Cyclomatic complexity determines the complexity of Python
code. Reducing the complexity allows code to usually be
more readable, testable and maintainable.

This may be ignored by commenting out the lizard
command in runTests.sh.

To install lizard, see <a href="https://github.com/terryyin/lizard">lizard</a>.

#### pep8 - Style Guile for Python Coding

pep8 checks Python code against the recommended style conventions.
See <a href="https://pypi.python.org/pypi/pep8">pep8 - Python style guide checker</a>.

If desired, comment out the line in runTest.sh to ignore this.

#### Python bindings for ZeroMQ

The Python bindings for Zero MQ are <b>required</b> since the
intent of the package drives an easy Zero MQ interface.


## Documentation and Utilities

The distribution provides extensive documentation. Refer to
[Easy Py Messaging](./easy_py_messaging/docs/easy_py_messaging.html).


## Tutorial
A tutorial: [Easy Py Messaging Tutorial](./easy_py_messaging/docs/easyMessagingTutorial.html).


## License

The project license is specified in COPYING and COPYING.LESSER.

Easy Py Messaging is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License (LGPL) as published by
the Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

As a special exception, the Contributors give you permission to link
this library with independent modules to produce an executable,
regardless of the license terms of these independent modules, and to
copy and distribute the resulting executable under terms of your choice,
provided that you also meet, for each linked independent module, the
terms and conditions of the license of that module. An independent
module is a module which is not derived from or based on this library.
If you modify this library, you must extend this exception to your
version of the library.

Easy Py Messaging is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
more details.

