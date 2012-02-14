import unittest
import meep_example_app
import urllib
import sys
import os.path
cwd = os.path.dirname(__file__)
importdir = os.path.abspath(os.path.join(cwd, '../'))
if importdir not in sys.path:
    sys.path.append(importdir)
import meep_example_app

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_index_no_auth(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Login' in data[0]
        assert 'here' in data[0]

    def test_index_with_auth(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'
        environ['HTTP_COOKIE'] = "username=george"

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        assert 'New Thread' in data[0]
        assert 'Show messages' in data[0]

    def test_thread_list(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/list'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Back to Main Page' in data[0]

    def test_create_user(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/create_user'
        environ['wsgi.input'] = ''

        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Username: ' in data
        assert 'Password:' in data

    def test_create_user_action(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/create_user'
        environ['wsgi.input'] = ''

        form_dict = {}
        form_dict['username'] = "bob"
        form_dict['password'] = "pass"
        environ['QUERY_STRING'] = urllib.urlencode(form_dict)

        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'
        environ['wsgi.input'] = ''
        environ['HTTP_COOKIE'] = "username=bob"

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        print "data: %s" %(data[0],)

        assert "bob " in data[0]

    def test_create_thread(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/add_thread'
        environ['wsgi.input'] = ''
        environ['HTTP_COOKIE'] = "username=george"

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Title: ' in data
        assert 'Message: ' in data

    def test_create_thread_action(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/add_thread_action'
        environ['wsgi.input'] = ''
        environ['HTTP_COOKIE'] = "username=george"

        form_dict = {}
        form_dict['title'] = "title"
        form_dict['message'] = "message"
        environ['QUERY_STRING'] = urllib.urlencode(form_dict)

        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/list'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        print "data: %s" %(data,)

        assert 'Back to Main Page' in data[0]
        assert "title" in data[0]
        assert "message" in data[0]

    def test_reply(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/reply'
        environ['wsgi.input'] = ''
        environ['HTTP_COOKIE'] = "username=george"

        form_dict = {}
        form_dict['thread_id'] = 1
        environ['QUERY_STRING'] = urllib.urlencode(form_dict)

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert "Message:" in data[0]

    def test_reply_action(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/reply'
        environ['wsgi.input'] = ''
        environ['HTTP_COOKIE'] = "username=test"

        form_dict = {}
        form_dict['thread_id'] = 1
        form_dict['post'] = "replytest"
        environ['QUERY_STRING'] = urllib.urlencode(form_dict)

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/list'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        assert 'Back to Main Page' in data[0]
        assert "first post" in data[0]

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
