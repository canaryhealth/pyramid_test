# -*- coding: utf-8 -*-
import pyramid_iniherit.install  # NOTE: this must be first.

import atexit
import os
import shutil

import morph
from pyramid.paster import get_appsettings
import sqlalchemy as sa

#------------------------------------------------------------------------------
# TODO: decouple the settings logic. remove this copy and paste section
from caditlib.settings import evalEnv

def fixSettings(settings):

  ret = dict()

  # evaluates '${ENV:NAME[:-DEFAULT]}' sequences in the configurations
  # todo: this would be *much* better if it was somehow made a part of
  #       ConfigParser...
  for k, v in settings.items():
    ret[k] = evalEnv(v, v)

  # todo: this is an ugly hack. basically, ``[DEFAULT]`` section
  #       configs (such as `envmod` and `env`) are not being
  #       made available in `settings`... ugh. so transferring here...
  for k, v in ret.items():
    if k.startswith('_') and k[1:] not in ret:
      ret[k[1:]] = v

  return ret

#------------------------------------------------------------------------------
appdir = os.getenv('appdir')
if not os.getenv('inifile'):
  os.environ['inifile'] = os.path.join(appdir, 'test.ini')  # default value
else:
  os.environ['inifile'] = os.path.join(os.getcwd(), os.getenv('inifile'))
config_uri = os.getenv('inifile')
settings = fixSettings(get_appsettings(os.getenv('inifile')))

#------------------------------------------------------------------------------
test_dirs = []
test_files = []
test_dbs = []

if morph.tobool(os.environ.get('KEEP', '0')):
  # todo: keep automatically on failed tests
  def cleanUpTests():
    # tmp dbs
    print '\n' + '='*65
    print '======= DID NOT DROPPED THE FOLLOWING UNIT TEST DATABASES ======='
    print '='*65 + '\n'
    for db in test_dbs:
      print 'DROP DATABASE "%s";' % db
    print '\n' + '='*65 + '\n'

    # tmp dirs
    print '\n' + '='*65
    print '==== NOT CLEANING UP THE FOLLOWING UNIT TEST TEMPORARY DIRS ====='
    print '='*65 + '\n'
    for tdir in test_dirs:
      print '  *', tdir
    print '\n' + '='*65 + '\n'

    # tmp files
    print '\n' + '='*65
    print '==== NOT CLEANING UP THE FOLLOWING UNIT TEST TEMPORARY FILES ===='
    print '='*65 + '\n'
    for fname in test_files:
      print '  *', fname
    print '\n' + '='*65 + '\n'
else:
  def cleanUpTests():
    # tmp dbs
    try:
      conn, engine = None, None
      engine = sa.create_engine(settings.get('sqlalchemy.url'))
      conn = engine.connect()
      for db in test_dbs:
        conn.execute('COMMIT')  # close the transaction block
        # note: statement is postgres dependent!!
        # close all other active connection
        # (http://stackoverflow.com/questions/5408156)
        try:
          conn.execute(
            '''
            SELECT pg_terminate_backend(pg_stat_activity.pid)
              FROM pg_stat_activity
              WHERE pg_stat_activity.datname = '%s'
                AND pid <> pg_backend_pid()
            ''' % (db,))
          conn.execute('COMMIT')
        except: pass
        conn.execute('DROP DATABASE "%s"' % (db,))
    finally:
      if conn:
        conn.close()
      if engine:
        engine.dispose()

    # tmp dirs
    for tdir in test_dirs:
      shutil.rmtree(tdir)

    # tmp files
    for fname in test_files:
      os.unlink(fname)

atexit.register(cleanUpTests)
