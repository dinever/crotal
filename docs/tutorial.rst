Tutorial
========

After installation of the Crotal, ``crotal`` command will be available
in your terminal window.

Creating a new site
-------------------

Go to the folder in which you want to put your site, simply use the
following command to create a new site named ``new``.

.. code:: bash

    $ crotal init new

Basic Structure
---------------

A basic Crotal site is like this:

.. code:: text

    ▾ source/
        ▸ pages/
        ▸ posts/
    ▸ static/
    ▾ themes/
        ▸ default/
      _config.yml
      db.json

Your posts and pages content, which is the core data of your site, will
be stored at ``source/posts`` and ``source/pages``. The static files you
may want to add to your site is under ``static/``. The config file
``_config.yml`` is used to config your site, it contains the information
like the site name, the author, the site description, etc.

Adding a post
-------------

Post is the very basic data format for your site. You can add a post
using the following command:

::

    $ crotal new_post 'hello-world-this-is-a-new-post'

However, you can still create a post mannually. Just create a new
``.md`` file under ``source/posts/``.

Adding a page
-------------

If you want to add a standalone webpage to your site, it is smart to add
a page in your site.

To create a crotal page, simple type the following command:

::

    $ crotal new_page

The instruction will guide you for creating the page. However, if you
want to mannually create a page, it will be simple, just add a ``.md``
file with proper format to the folder ``source/pages``.

Generating the site
-------------------

.. code:: bash

    $ crotal generate

After generating the site, your site files will be located at the
``preview`` folder.

Previewing the site
-------------------

.. code:: bash

    $ crotal server

Now you can browse the site at http://localhost:1124, if the port 1124
is already in use, please indicate a new port like this:

.. code:: bash

    $ crotal server -p 8088
