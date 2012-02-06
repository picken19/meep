import unittest
import meep_example_app

class TestApp(unittest.TestCase):
    def setUp(self):
        meep_example_app.initialize()
        app = meep_example_app.MeepExampleApp()
        self.app = app

    def test_index(self):
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)

        assert 'Login' in data[0]
        assert 'here' in data[0]

    def test_message_list(self):
        self.app.username = 'test' # force login
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
        #environ['wsgi.input'] = ''

        def fake_start_response(status, headers):
            assert status == '302 Found'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Username:' in data
        assert 'Password:' in data

    def test_add_thread(self):
        self.app.username = 'test' # force login
        environ = {}                    # make a fake dict
        environ['PATH_INFO'] = '/m/add_thread'

        def fake_start_response(status, headers):
            assert status == '200 OK'
            assert ('Content-type', 'text/html') in headers

        data = self.app(environ, fake_start_response)
        assert 'Title:' in data
        assert "Message: " in data

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
