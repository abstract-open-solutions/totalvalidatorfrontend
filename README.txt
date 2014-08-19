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
