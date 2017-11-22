import unittest
import coursework
import os

TEST_DB = '/static/foundation.db/'
class TestingTest(unittest.TestCase):
  def test_root(self):
    self.app = coursework.app.test_client()
    out = self.app.get('/')
    assert '200 OK' in out.status
    assert 'charset=utf-8' in out.content_type
    assert 'text/html' in out.content_type

#def login(self, user, pw):
 # self.app = coursework.app.test_client()
  #return self.app.get('/login/')

def logout(self):
  return self.app.get('/logout/', follow_redirects=True)



if __name__ == "__main__":
  unittest.main()

