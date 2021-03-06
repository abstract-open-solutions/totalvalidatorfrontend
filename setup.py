import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid_who',
    'redis',
    'pyramid_celery',
    'SQLAlchemy == 0.8.3',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'colander',
    'deform',
    'webhelpers',
    'abstract.totalvalidator',
    'psycopg2'
]

setup(name='totalvalidatorfrontend',
      version='0.0',
      description='totalvalidatorfrontend',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      test_suite='totalvalidatorfrontend',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = totalvalidatorfrontend:main
      [console_scripts]
      initialize_db = totalvalidatorfrontend.scripts.initializedb:main
      """,
      )
