import unittest
import meep_example_app

class TestApp(unittest.TestCase):
	def setUp(self):
		meep_example_app.initialize()
		app = meep_example_app.MeepExampleApp()
		self.app = app

	def test_index(self):
		environ = {}					# make a fake dict
		environ['PATH_INFO'] = '/'

		def fake_start_response(status, headers):
			assert status == '200 OK'
			assert ('Content-type', 'text/html') in headers

		data = self.app(environ, fake_start_response)
		assert 'Add a message' in data[0]
		assert 'Show messages' in data[0]

	def tearDown(self):
		pass

	def test_list(self):
		environ = {}					# make a fake dict
		environ['PATH_INFO'] = '/m/list'
		
		def fake_start_response(status, headers):
#			for x in environ:
#				print environ[x]
			assert status == '200 OK'
			assert ('Content-type', 'text/html') in headers

		data = self.app(environ, fake_start_response)
		#print data[0]
		assert 'index' in data[0]

	def test_login(self):
		environ = {}					# make a fake dict
		environ['PATH_INFO'] = '/login'

		def fake_start_response(status, headers):
#			for x in environ:
#				print environ[x]
#			print environ['PATH_INFO']
			assert status == '200 OK'
			assert ('Content-type', 'text/html') in headers

		data = self.app(environ, fake_start_response) 
		print 'hello'
		print data[0]
		print '2'
		assert 'Username:' in data[0]
		assert 'Password:' in data[0]

	def test_logout(self):
		environ = {}					# make a fake dict
		environ['PATH_INFO'] = '/logout'

		def fake_start_response(status, headers):
			assert status == '200 OK'
			assert ('Content-type', 'text/html') in headers

		data = self.app(environ, fake_start_response)
		print data[0]
		print 'hi'
		assert 'user: .' in data[0]

if __name__ == '__main__':
	unittest.main()
