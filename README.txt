totalvalidatorfrontend README
==================

Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/python setup.py develop

- $VENV/bin/initialize_totalvalidatorfrontend_db development.ini

- $VENV/bin/pserve development.ini



Start services
--------------

CELERY::

    ./bin/pceleryd etc/development.ini

REDIS::

    ./parts/redis/bin/redis-server parts/redis/redis.conf



Translations
============

extract messages and create .pot file::

    >>> ./bin/pot-create -o src/totalvalidatorfrontend/locale/totalvalidatorfrontend.pot src


init catalog::

    >>> ./bin/py setup.py init_catalog -l <language code>


update catalogs::

    >>> ./bin/py setup.py update_catalog


compile catalogs::

    >>> ./bin/py setup.py compile_catalog
