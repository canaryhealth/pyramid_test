# -*- coding: utf-8 -*-
import subprocess
import tempfile

from .db import DbTestCase
from .runner import appdir, config_uri, test_dirs, test_files

#------------------------------------------------------------------------------
class ServerSolo(object):
  '''
  Singleton to generate unique port numbers for server test case.
  '''
  __instance = None
  port = 20150  # party like it's 2015

  # create tmp dir for screenshots
  tmpdir = tempfile.mkdtemp()
  test_dirs.append(tmpdir)


  def __new__(cls):
    if ServerSolo.__instance is None:
      ServerSolo.__instance = object.__new__(cls)
    return ServerSolo.__instance

  def get_port(self):
    self.port = self.port + 1
    return self.port


#------------------------------------------------------------------------------
class ServerTestCase(DbTestCase):
  '''
  Creates a test database and launches a test server with an unique port using 
  `pserve`. Its main intended use is for web browser automation tests. This
  differs from ApiTestCase since the server is accessible externally via the
  URL.

  Attributes
  ----------
  tmpdir : dir
    name of tmp for test output/screenshots
  config : string
    name of temp config file used to run pserve
  pserve : subprocess
    reference to the subprocess that is running pserve/test server
  '''
  #----------------------------------------------------------------------------
  def setUp(self):
    super(ServerTestCase, self).setUp()

    # write dburl and port to temp ini file
    prefix = 'test-'
    suffix = '.ini.LOCAL'
    port = ServerSolo().get_port()
    fp = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False)
    config = '''\
[DEFAULT]
%%inherit                        = %(inherit)s
dburl                           = %(dburl)s
here                            = %(here)s
[server:main]
host                            = %%(env)s.canary.md
port                            = %(port)d
'''
    # set here = appdir
    fp.write(config % dict(inherit=config_uri, 
                           dburl=self.testdb_url,
                           here=appdir,
                           port=port))
    test_files.append(fp.name)
    fp.close()

    # fire webserver up
    self.config = fp.name
    self.pserve = subprocess.Popen(['i-pserve', self.config],
                                   close_fds=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)


  def tearDown(self):
    super(ServerTestCase, self).tearDown()
    self.pserve.kill()
