import meeplib
import traceback
import cgi
import meepcookie
import cPickle
from Cookie import SimpleCookie
from jinja2 import Environment, FileSystemLoader
from file_server import FileServer

##in meep##

def initialize():
	print "enter initialize"
	meeplib.load_state()
	u = meeplib.User('test', 'foo')
	t = meeplib.Thread('Greetings Earthlings')
	m = meeplib.Message('The meep message board is open.', u)
	t.add_post(m)

env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
	print "enter render page"
	template = env.get_template(filename)
	s = template.render(**variables)
	print "exit render page"
	return str(s)

def check_cookie(environ):
	print "enter check cookie"
	try:
		cookie = SimpleCookie()
		cookie.load(environ.get('HTTP_COOKIE'))
		username = cookie['username'].value
		print "check cookie username: %s" % username
		print "exit check cookie"
		return username
	except:
		print "check cookie exception"
		print "exit check cookie"
		return ''

class MeepExampleApp(object):
	"""
	WSGI app object.
	"""
	
	def index(self, environ, start_response):
		print "enter index"
		start_response("200 OK", [('Content-type', 'text/html')])
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		if user is None:
			print "exit index"
			return [ render_page('login.html') ]
		elif user is not None:
			print "exit index"
			return [ render_page('index.html', username=username) ]

	def create_user(self, environ, start_response):
		print "enter create user"
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		if user is not None:
			headers = [('Content-type', 'text/html')]
			headers.append(('Location', '/'))
			start_response("302 Found", headers)
			return ["log out to use that feature"]
		headers = [('Content-type', 'text/html')]
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		try:
			username = form['username'].value
		except KeyError:
			username = ''
		try:
			password = form['password'].value
		except KeyError:
			password = ''
			
		s=[]

		##if we have username and password
		if username != '':
			user = meeplib.get_user(username)
			## user already exists
			if user is not None:
				s.append('''user already exists; <br>
				please use a different username.<p>''')
			## user doesn't exist but they messed up the passwords
			elif password == '':
				s.append('''enter a password <br/>''')
			else:
				u = meeplib.User(username, password)
				meeplib.save_state()
				## send back a redirect to '/'
				k = 'Location'
				v = '/'
				headers.append((k, v))
				cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',username)
				headers.append((cookie_name, cookie_val))

		start_response('302 Found', headers)

		s.append(render_page("create_user.html", username=username))
		print "exit create user"
		return [''.join(s)]

	def login(self, environ, start_response):
		print "enter login"
		username = check_cookie(environ)
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		returnStatement = "logged in"
		try:
			username = form['username'].value
		except KeyError:
			username = None
		try:
			password = form['password'].value
		except KeyError:
			password = None
		k = 'Location'
		v = '/'
		headers = [('Content-type', 'text/html')]
		if username is not None:
			 if password is not None:
				 if meeplib.check_user(username, password) is True:
					 new_user = meeplib.User(username, password)
					 meeplib.set_curr_user(username)
					 # set the cookie to the username string
					 cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',username)
					 headers.append((cookie_name, cookie_val))
				 else:
					 returnStatement = """<p>invalid user,	please try again.</p>"""
			 else:		
				 returnStatement = """<p>password was not set; user was not created</p>"""
		else:
			returnStatement = """<p>username was not set; user was not created</p>"""
		print """isValidafter: %s """ %(meeplib.check_user(username, password),)
		headers.append((k, v))
		start_response('302 Found', headers)

		print returnStatement
		print "exit login"
		return "no such content"	

	def logout(self, environ, start_response):
		print "enter logout"
		headers = [('Content-type', 'text/html')]
		k = 'Location'
		v = '/'
		headers.append((k, v))
		cookie_name, cookie_val = meepcookie.make_set_cookie_header('username','')
		headers.append((cookie_name, cookie_val))
		start_response('302 Found', headers)
		print "exit logout"
		return "no such content"

	#return a list of all messages
	def list_messages(self, environ, start_response):
		print "enter list messages"
		messages = meeplib.get_all_threads()
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		s = []
		if messages:
			s.append(render_page("list_messages.html", messages=messages, user=user))
		else:
			s.append("no threads exist<p>")
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		print "exit list messages"
		return ["".join(s)]

	#delete all messages action
	def delete_all_messages_action(self, environ, start_response):
		print "enter delete all messages action"
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		username = check_cookie(environ)
		threads = meeplib.get_all_threads()
		for t in threads:
			meeplib.delete_thread(t)

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
	
		meeplib.save_state()
		print "exit delete all messages action"
		return ["all threads deleted"]

	def delete_message_action(self, environ, start_response):
		print "enter delete message action"
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		thread_id = int(form['msg_id'].value)
		post_id = int(form['post_id'].value)
		t = meeplib.get_thread(thread_id)
		p = t.get_post(post_id)
		t.delete_post(p)
		meeplib.save_state()
		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		print "exit delete message action"
		return["post deleted"]

	def add_thread(self, environ, start_response):
		print "enter add thread"
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		if user is None:
			headers = [('Content-type', 'text/html')]
			headers.append(('Location', '/'))
			start_response("302 Found", headers)
			return ["log in in to use that feature"]
		headers = [('Content-type', 'text/html')]
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		try:
			title = form['title'].value
		except KeyError:
			title = ''
		try:
			message = form ['message'].value
		except KeyError:
			message = ''
		s = []
		if title == '' and message == '':
			pass
		elif title == '' and message != '':
			s.append('''''title' cannot be empty<p>''')
		elif title != '' and message == '':
			s.append('''''message' cannot be empty<p>''')
		elif title != '' and message != '':
			new_message = meeplib.Message(message, user)
			t = meeplib.Thread(title)
			t.add_post(new_message)
			meeplib.save_state()
			headers.append(('Location','/m/list'))
		start_response("302 Found", headers)
		s.append(render_page("add_message.html", title=title, message=message))
		print "exit add thread"
		return ["".join(s)]

	#how do we pass in the parent id?
	def reply(self, environ, start_response):
		print "enter reply"
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		if user is None:
			headers = [('Content-type', 'text/html')]
			headers.append(('Location', '/'))
			start_response("302 Found", headers)
			return ["log in to use that feature"]
		headers = [('Content-type', 'text/html')]
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		thread_id = int(form['thread_id'].value)
		t = meeplib.get_thread(thread_id)
		s = []
		try:
			post = form['post'].value
		except KeyError:
			post = ''
		if post != '':
			new_message = meeplib.Message(post, user)
			t.add_post(new_message)
			meeplib.save_state()
			headers.append(('Location','/m/list'))
		start_response("302 Found", headers)
		s.append(render_page("reply.html", thread=t))
		print "exit reply"
		return ["".join(s)]

	def __call__(self, environ, start_response):
		print "enter call"
		# store url/function matches in call_dict
		call_dict = { '/': self.index,
				'/create_user': self.create_user,
				'/login': self.login,
				'/logout': self.logout,
				'/m/list': self.list_messages,
				'/m/add_thread': self.add_thread,
				'/delete_all_messages_action': self.delete_all_messages_action,
				'/m/delete_message_action': self.delete_message_action,
				'/m/reply': self.reply,
				'/style': FileServer('templates/style.css'),
			  	'/style2': FileServer('templates/style2.css')
			}

		# see if the URL is in 'call_dict'; if it is, call that function.
		url = environ['PATH_INFO']
		fn = call_dict.get(url)

		if fn is None:
			start_response("404 Not Found", [('Content-type', 'text/html')])
			return ["Page not found."]

		try:
			print "exit call"
			return fn(environ, start_response)
		except:
			tb = traceback.format_exc()
			x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)
			status = '500 Internal Server Error'
			start_response(status, [('Content-type', 'text/html')])
			print "exit call"
			return [x]