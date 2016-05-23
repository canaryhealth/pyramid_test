============
pyramid_test
============

A collection of test helper functions to make testing easy!


Components
==========

Test runner
  Cleans up databases and temporary files/directories. When running nosetests, set `KEEP=1` to keep these temporary files after the tests complete.

DbTestCase
  Creates database using alembic migrations. Each test database has an unique name based on the name of the test case.

ApiTestMixin
  Provides assert statements for API OK or Error. See TBD Section.

ServerTestCase
  Creates a test database and launches a test server with an unique port using `pserve`. Its main intended use is for web browser automation tests. This differs from ApiTestCase since the server is accessible externally via the URL.


Usage/Examples
==============

For now, we need to create local classes to utilize `pyramid_test` for our test cases to extend.

.. code:: python

  # myapp/tests/test_helper.py
  import os
  appdir = os.path.dirname(os.path.dirname(__file__))
  os.environ['appdir'] = testdir  # must set before importing pyramid_test

  from pyramid_test import DbTestCase, ApiTestMixin
  from myapp import model, main

  class ModelTestCase(DbTestCase):
    def setUp(self):
      super(ModelTestCase, self).setUp()
      engine = sa.engine_from_config(self.settings, 'sqlalchemy.')
      model.DBSession.configure(bind=engine)

    def tearDown(self):
      super(ModelTestCase, self).tearDown()
      model.DBSession.remove()


  class ApiTestCase(ModelTestCase, ApiTestMixin):
    def setUp(self):
      super(ApiTestCase, self).setUp()
      # note: we cannot use pyramid.paster.getapp here b/c we changed the 
      #       dburl in self.settings, which is not reflected in config_uri
      self.router = main({}, **self.settings)
      self.testapp = TestApp(self.router)


  # myapp/tests/test_me.py
  from myapp.tests.test_helper import ModelTestCase

  class TestMe(ModelTestCase):
    def test_me(self):
      # the test db is created and ready to go!


Limitations
===========

* We can only run tests sequentially in a single process. This is due to:
  * To speed up the creation of an unique test database for each test case, we copy it from a primary test database instead of creating one from scratch. The primary test database must not have any opened connections when the copy occurs.
  * We use a singleton to generate unique port numbers for `BrowserTestCase`. May need to make this thread-safe.

* Only PostgreSQL is supported. We are using database-specific SQL statement to copy the primary test database.


TBD/TODO
========

- implement hooks for fixtures
- implement hooks for model and testapp to eliminate the need for local classes
