# -*- coding: utf-8 -*-
import unittest

from aadict import aadict
import morph

#------------------------------------------------------------------------------
class ApiTestMixin(unittest.TestCase):

  #----------------------------------------------------------------------------
  def assertApiOk(self, response, expected=None,
                  contentType='application/json', location=None,
                  root=None, sideload=None,
                  pick=None, pluck=None, omit=None, sort=None):
    if location is not None:
      self.assertEqual(response.status_code, 302)
      if morph.isstr(location):
        self.assertEqual(response.headers['location'], location)
      else:
        self.assertTrue(location(response.headers['location']))
      return response
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.content_type, contentType)
    if expected is None:
      return response
    if contentType == 'text/html':
      self.assertEqual(response.body, expected)
      return response
    result = response.json_body
    if root is not None:
      self.assertIn(root, result, 'root "%s" not found in response' % (root,))
      self.assertEqual(result.keys(), [root] if not sideload else [root] + sideload)
      result = result[root]
    if pick is not None:
      if morph.isdict(expected):
        result = morph.pick(result, *morph.tolist(pick))
      elif morph.isseq(expected):
        result = [morph.pick(item, *morph.tolist(pick)) for item in result]
    if pluck is not None:
      result = [item.get(pluck, None) for item in result]
    if omit is not None:
      if morph.isdict(expected):
        result   = morph.omit(result, *morph.tolist(omit))
        expected = morph.omit(expected, *morph.tolist(omit))
      elif morph.isseq(expected):
        result   = [morph.omit(item, *morph.tolist(omit)) for item in result]
        expected = [morph.omit(item, *morph.tolist(omit)) for item in expected]
    if sort:
      if sort is True:
        expected = sorted(expected)
        result   = sorted(result)
      else:
        expected = sort(expected)
        result   = sort(result)
    self.assertEqual(result, expected)
    return response

  #----------------------------------------------------------------------------
  def assertApiErr(self, response, code, expected=None, message=None):
    self.assertEqual(response.status_code, code)
    self.assertEqual(response.content_type, 'application/json')
    jdata = response.json
    self.assertEqual(jdata.get('code'), code)
    if expected is not None:
      self.assertEqual(aadict(jdata).omit('code', 'message'), expected)
    if message is not None:
      self.assertEqual(jdata.get('message'), message)
    return response
