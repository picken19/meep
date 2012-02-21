import meeplib
import traceback
import cgi
import meepcookie
import cPickle
from Cookie import SimpleCookie
from jinja2 import Environment, FileSystemLoader

##in meep##

def initialize():
	u = meeplib.User('test', 'foo')
	m = meeplib.Message('Greetings Earthlings', 'The meep message board is open.', u, -1, [])

env = Environment(loader=FileSystemLoader('templates'))

def render_page(filename, **variables):
	template = env.get_template(filename)
	s = template.render(**variables)
	return str(s)

def check_cookie(environ):
	print "check cookie"
	try:
		cookie = SimpleCookie()
		cookie.load(environ.get('HTTP_COOKIE'))
		username = cookie['username'].value
		print "check cookie username: %s" % username
		return username
	except:
		print "check cookie exception"
		return ''
	
class MeepExampleApp(object):
	"""
	WSGI app object.
	"""
	
	def __init__(self):
		meeplib._messages, meeplib._user_ids, meeplib._users = meeplib.load_state()

	def index(self, environ, start_response):
		start_response("200 OK", [('Content-type', 'text/html')])

		username = check_cookie(environ)
		print "index a"
		user = meeplib.get_user(username)
		print "User: %s" % user

		if user is None:
			print "index b"
			return [ render_page('login.html') ]

		elif user is not None:
			print "index c"
			return [ render_page('index.html', username=username) ]

	def create_user(self, environ, start_response):
		headers = [('Content-type', 'text/html')]

		start_response("302 Found", headers)
		return """<form action='add_new_user' method='POST'>
		Username: <input type='text' name='username'><br>
		Password:<input type='text' name='password'><br>
		<input type='submit' value='Create User'></form>"""

	def add_new_user(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

		returnStatement = "user added"
		try:
			username = form['username'].value
			print "username accepted"
		except KeyError:
			username = None
		try:
			password = form['password'].value
			print "password accepted"
		except KeyError:
			password = None

		print "Username: %s" % username
		print "Password: %s" % password

		# Test whether variable is defined to be None
		if username is None:
			returnStatement = "username was not set. User could not be created"
		if password is None:
			returnStatement = "password was not set. User could not be created"
		else:
			new_user = meeplib.User(username, password)
			meeplib.save_state()
			print meeplib.get_user(username)

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/'))
		start_response("302 Found", headers)

		return [returnStatement]

	def login(self, environ, start_response):
		try:
			cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
			username = cookie["username"].value
			print "Username = %s" % username
		except:
			print "session cookie not set! defaulting username"
			username = ''

		print environ['wsgi.input']
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

		# set content-type
		headers = [('Content-type', 'text/html')]

		# Test whether variable is defined to be None
		if username is not None:
			 if password is not None:
				 if meeplib.check_user(username, password) is True:
					 new_user = meeplib.User(username, password)
					 meeplib.set_curr_user(username)
					 # set the cookie to the username string
					 cookie_name, cookie_val = meepcookie.make_set_cookie_header('username',username)
					 headers.append((cookie_name, cookie_val))
				 else:
					 returnStatement = """<p>Invalid user.	Please try again.</p>"""

			 else:		
				 returnStatement = """<p>Password was not set. User could not be created</p>"""
		else:
			returnStatement = """<p>Username was not set. User could not be created</p>"""

		print """isValidafter: %s """ %(meeplib.check_user(username, password),)


		headers.append((k, v))
		start_response('302 Found', headers)

		print returnStatement
		return "no such content"	

	def logout(self, environ, start_response):
		# does nothing
		headers = [('Content-type', 'text/html')]

		# send back a redirect to '/'
		k = 'Location'
		v = '/'
		headers.append((k, v))

		cookie_name, cookie_val = meepcookie.make_set_cookie_header('username','')
		headers.append((cookie_name, cookie_val))

		start_response('302 Found', headers)

		return "no such content"

	#return a list of all messages
	def list_messages(self, environ, start_response):
		messages = meeplib.get_all_messages()
		s = []
		print "num of messages"
		print len(messages)
		for m in messages:
			if m.parent == -1:
				s.append('id: %d<p>' % (m.id))
				s.append('title: %s<p>' % (m.title))
				s.append('message: %s<p>' % (m.post))
				s.append('author: %s<px>' % (m.author.username))
				s.append("""<form action='reply' method='POST'><input type='hidden' value='%d' name='msg_id'><input type='submit' value="Reply" name="reply_button"></form>""" % (m.id))
				for c in m.child:
					s.append('<hr >')
					n = meeplib.get_message(c)
					s.append('id: %d<p>' % (n.id))
					s.append('Reply to: %s<p>' % (m.title))
					s.append('message: %s<p>' % (n.post))
					s.append('author: %s<px>' % (n.author.username))
				s.append('<hr />')
				s.append('<hr />')	
		s.append("<a href='../../'>index</a>")
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		return ["".join(s)]

	#call the method to delete all messages
	def delete_all_messages(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		
		start_response("200 OK", headers)

		return """<form action='delete_all_action' method='POST'></form>"""

	#delete all messages action
	def delete_all_messages_action(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

		username = 'test'
		user = meeplib.get_user(username)

		messages = meeplib.get_all_messages()
		for msg in messages:
			meeplib.delete_message(msg)

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		
		meeplib.save_state()
		return ["all messages deleted"]

	#call the method to delete one message
	def delete_one_message(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		
		start_response("200 OK", headers)

		return """<form action='delete_one_action' method='POST'>Message ID: <input type='text' name='msgID'><br><input type='submit' value='Delete'></form>"""

	#delete one message action
	def delete_one_message_action(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

		ID = form['msgID'].value

		username = 'test'
		user = meeplib.get_user(username)

		msg = meeplib.get_message(int(ID))
		meeplib.delete_message(msg)

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		return ["message deleted"]

	#call the method to add a single message
	def add_message(self, environ, start_response):
		print "add message 1"
		headers = [('Content-type', 'text/html')]
		username = check_cookie(environ)
		print "add message 2"
		print username
		if username == '':
			print "add message 3"
			print "no user logged in"
			#Send to error page if no user is logged in
			headers.append(('Location', '/m/no_user'))
			start_response("302 found", headers)
			return "you must be logged in to post to meep"

		print "add message 4"
		start_response("200 OK", headers)
		return render_page('add_message.html')


	#add a single message action
	def add_message_action(self, environ, start_response):
		print "add message action 1"
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

		title = form['title'].value
		message = form['message'].value
		
		print "add messaage action 2"
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		
		print "add message action 3"
		new_message = meeplib.Message(title, message, user, -1, [])

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		meeplib.save_state()
		print "add message action 4"
		return ["message added"]

	#how do we pass in the parent id?
	def reply(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		form = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ)
		print form['msg_id'].value
		s = """<form action='reply_action' method='POST'>Message:<input type='text' name='message'><br><input type='hidden' name='msg_id' value='%d'><br><input type='submit' value='Submit' name='add_button'></form>""" % (int(form['msg_id'].value))
		return s

	def reply_action(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		parent_msg = meeplib.get_message(int(form['msg_id'].value))
		title = 'user replied to message ' + parent_msg.title
		message = form['message'].value
		parent = int(form['msg_id'].value)
		username = check_cookie(environ)
		user = meeplib.get_user(username)
		new_message = meeplib.Message(title, message, user, parent, -1)
		
		print "need to update parent!"
		meeplib.Message.update_children(parent_msg, new_message.id)		
		
		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		meeplib.save_state()
		return ["reply added"]

	def no_user(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		return """You can't submit a message if you aren't logged in!<p>
			<a href='/login'>Log in</a><p>
			<a href='../../'>Back to Home</a>"""
	
	def __call__(self, environ, start_response):
		# store url/function matches in call_dict
		print "enter call dict"
		call_dict = { '/': self.index,
					  '/create_user': self.create_user,
					  '/add_new_user':self.add_new_user,
					  '/login': self.login,
					  '/logout': self.logout,
					  '/m/list': self.list_messages,
					  '/m/add_message': self.add_message,
					  '/m/add_message_action': self.add_message_action,
					  '/m/delete_all': self.delete_all_messages_action,
					  '/delete_all_messages_action': self.delete_all_messages_action,
					  '/m/delete_one': self.delete_one_message,
					  '/m/delete_one_action': self.delete_one_message_action,
					  '/m/reply': self.reply,
					  '/m/reply_action': self.reply_action,
			  '/m/no_user': self.no_user
			}

		# see if the URL is in 'call_dict'; if it is, call that function.
		url = environ['PATH_INFO']
		fn = call_dict.get(url)

		if fn is None:
			print "call 1"
			start_response("404 Not Found", [('Content-type', 'text/html')])
			return ["Page not found."]

		try:
			print "call 2"
			return fn(environ, start_response)
		except:
			print "call 3"
			tb = traceback.format_exc()
			x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

			status = '500 Internal Server Error'
			start_response(status, [('Content-type', 'text/html')])
			return [x]