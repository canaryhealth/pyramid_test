# -*- coding: utf-8 -*-
import string
import unittest

import morph
from six.moves.urllib import parse
import sqlalchemy as sa

from .runner import settings, test_dbs

#------------------------------------------------------------------------------
class DbTestCase(unittest.TestCase):
  '''
  Creates database using alembic migrations. Each test database has an unique
  name based on the name of the test case.

  Attributes
  ----------
  masterdb_name : string
    name of the master db used as a template for all test databases
  masterdb_url : string
    dburl of the master db
  testdb_name : string
    name of the test db created for this test case
  testdb_url : string
    dburl of the test db created for this test case
  settings : dict
    dict containing pyramid current test settings/config
  '''
  maxDiff = None  # to display diff for nosetests

  #----------------------------------------------------------------------------
  # todo: create masterdb if it doesn't exist

  #----------------------------------------------------------------------------
  def setUp(self):
    '''
    Creates test_db for current testcase by copying the master_db.
    '''
    super(DbTestCase, self).setUp()

    # get master db url and name
    self.masterdb_url = settings.get('sqlalchemy.url')
    # index 2 is the path and trim leading slash
    self.masterdb_name = parse.urlparse(self.masterdb_url)[2][1:]

    # postgres has 63 char limit for db names. if exceed, use the rightmost 63
    self.testdb_name = self.masterdb_name + ':' \
      + self.id()[- ( 63 - 1 - len(self.masterdb_name) ):]

    if not self.masterdb_url.startswith('postgresql://'):
      raise ValueError('DbTestCase currently only supports postgres')

    # copy master db to test db (using test name as test db name)
    try:
      conn, engine = None, None
      engine = sa.create_engine(self.masterdb_url)
      conn = engine.connect()
      conn.execute('COMMIT')  # close the transaction opened by engine.connect()
      conn.execute('DROP DATABASE IF EXISTS "%s"' % (self.testdb_name,))
      conn.execute('COMMIT')
      # note: statement is postgres dependent!!
      conn.execute('CREATE DATABASE "%s" WITH TEMPLATE "%s"' %
                   (self.testdb_name, self.masterdb_name))
      test_dbs.append(self.testdb_name)
    finally:
      if conn:
        conn.close()
      if engine:
        engine.dispose()

    # update configs to use testdb_url
    self.testdb_url = string.replace(
      self.masterdb_url, self.masterdb_name, self.testdb_name)
    self.settings = dict(settings)
    self.settings['dburl'] = self.testdb_url
    self.settings['sqlalchemy.url'] = self.testdb_url
    # todo: the scheduler references the dburl as well

  #----------------------------------------------------------------------------
  def uni2str(self, obj):
    '''
    Converts unicode to string such that unittest's diff won't display them as
    different. The unittest comparision actually doesn't differentiate between
    unicode and string.
    '''
    if morph.isstr(obj):
      return str(obj)
    if morph.isseq(obj):
      if isinstance(obj, tuple):
        return tuple(self.uni2str(el) for el in obj)
      return [self.uni2str(el) for el in obj]
    if morph.isdict(obj):
      return {self.uni2str(k): self.uni2str(v) for k, v in obj.items()}
    return obj

  #----------------------------------------------------------------------------
  def assertEqual(self, a, b, *args, **kw):
    '''
    Overrides `assertEqual` to use `uni2str`.
    '''
    try:
      return super(DbTestCase, self).assertEqual(a, b, *args, **kw)
    except AssertionError:
      if not self.uni2str:
        raise
      a = self.uni2str(a)
      b = self.uni2str(b)
      return super(DbTestCase, self).assertEqual(a, b, *args, **kw)
