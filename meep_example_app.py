import meeplib
import traceback
import cgi
from wsgiref import util
import os
import pickle
import sys
import cPickle
import meepcookie
import Cookie

	# create a default user
	u = meeplib.User('test', 'foo')
	meeplib.User('new', 'test')

	path = '/Users/caitlynpickens/Documents/meep/pickle/'
	listing = os.listdir(path)
	for infile in listing:
		try:
			# load data
			print infile
			fp = open('/Users/caitlynpickens/Documents/meep/pickle/'+infile)
			print "unpickle"
			try:
				obj = pickle.load(fp)
			except:
				err = sys.exc_info()
				for x in err:
					print x
			meeplib.unpickle_message(obj)
		except IOError:	 # file does not exist/cannot be opened
			# create a single message
			err = sys.exc_info()
			for x in err:
				print x
			print "error"

	# create a thread
#	 t = meeplib.Thread('Test Thread')
	# create a single message
#	 m = meeplib.Message('This is my message!', u)
	# save the message in the thread
#	 t.add_post(m)


	meeplib.Message('Greetings Earthlings', 'The meep message board is open.', u, -1, [])
	# done.




class MeepExampleApp(object):
	"""
	WSGI app object.
	"""
	global username
	username = ''

		WSGI app object.
		
		def __init__(self):
			meeplib._threads, meeplib._user_ids, meeplib._users = meeplib.load_state()

		def index(self, environ, start_response):
			start_response("200 OK", [('Content-type', 'text/html')])
			# get cookie if there is one
			try:
				cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
				username = cookie["username"].value
				print "Username = %s" % username
			except:
				print "session cookie not set! defaulting username"
				username = ''

			user = meeplib.get_user(username)
			print "User = %s" % user
			if user is None:
				s = ["""<h1>Welcome!</h1><h2>Please Login or create an account.</h2>
	<form action='login' method='POST'>
	Username: <input type='text' name='username'><br>
	Password:<input type='text' name='password'><br>
	<input type='submit' value='Login'></form>

	<p>Don't have an account? Create a user <a href='/create_user'>here</a>"""]
			elif user is not None:
				s =	 ["""%s logged in!<p><a href='/m/add_thread'>New Thread</a><p><a href='/create_user'>Create User</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (username,)]
			return s

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
			except KeyError:
				username = None
			try:
				password = form['password'].value
			except KeyError:
				password = None

			print username
			print password
			# Test whether variable is defined to be None
			if username is None:
				returnStatement = "username was not set. User could not be created"
			if password is None:
				returnStatement = "password was not set. User could not be created"
			else:
				new_user = meeplib.User(username, password)
				meeplib.save_state()

			headers = [('Content-type', 'text/html')]
			headers.append(('Location', '/'))
			start_response("302 Found", headers)

			return [returnStatement]

		def login(self, environ, start_response):
			try:
				cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
				username = cookie["username"].value
				#print "Username = %s" % username
			except:
				#print "session cookie not set! defaulting username"
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
					 returnStatement = """<p>password was not set. User could not be created</p>"""
			else:
				returnStatement = """<p>username was not set. User could not be created</p>"""

			print """isValidafter: %s """ %(meeplib.check_user(username, password),)


			headers.append((k, v))
			start_response('302 Found', headers)

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

		def add_thread(self, environ, start_response):
			headers = [('Content-type', 'text/html')]

			start_response("200 OK", headers)

			return """<form action='add_thread_action' method='POST'>Title: <input type='text' name='title'><br>Message: <input type='text' name='message'><br><input type='submit'></form>"""

		def add_thread_action(self, environ, start_response):
			print environ['wsgi.input']
			form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

			title = form['title'].value
			message = form['message'].value

			cookie = Cookie.SimpleCookie(environ["HTTP_COOKIE"])
			username = cookie["username"].value
			user = meeplib.get_user(username)

			new_message = meeplib.Message(message, user)
			t = meeplib.Thread(title)
			t.add_post(new_message)

			meeplib.save_state()

			headers = [('Content-type', 'text/html')]
			headers.append(('Location', '/m/list'))
			start_response("302 Found", headers)
			return ["thread added"]

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
				#print the children (replies)
#				print "HELLO"
				s.append("""<form action='reply' method='POST'><input type='hidden' value='%d' name='msg_id'><input type='submit' value="Reply" name="reply_button"></form>""" % (m.id))
#				print len(m.child)
				for c in m.child:
					s.append('<hr >')
					n = meeplib.get_message(c)
					#print "HERE"
					s.append('id: %d<p>' % (n.id))
					s.append('Reply to: %s<p>' % (m.title))
					s.append('message: %s<p>' % (n.post))
					s.append('author: %s<px>' % (n.author.username))
#					s.append('<form action="delete_message" method="POST"><input type="hidden" name="id" value="%d"><input type="submit" value="Delete Message" name="delete_button"></form>' % (m.id))
				#print m.id
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
		headers = [('Content-type', 'text/html')]
		global username
		if username == '':
			#Send to error page if no user is logged in
			headers.append(('Location', '/m/no_user'))
			start_response("302 found", headers)
			return "no such content"
		else:
			start_response("200 OK", headers)
			return """<form action='add_action' method='POST'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='submit' name='add_button'></form>"""

	#add a single message action
	def add_message_action(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

		title = form['title'].value
		message = form['message'].value
		
		user = meeplib.get_user(username)
		
		new_message = meeplib.Message(title, message, user, -1, [])

		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		return ["message added"]

	#how do we pass in the parent id?
	def reply(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		form = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ)
		print form['msg_id'].value
		s = """<form action='reply_action' method='POST'>Message:<input type='text' name='message'><br><input type='hidden' name='msg_id' value='%d'><br><input type='submit' value='Submit' name='add_button'></form>""" % (int(form['msg_id'].value))
		print s
		return s															  

	def reply_action(self, environ, start_response):
		print environ['wsgi.input']
		form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
		parent_msg = meeplib.get_message(int(form['msg_id'].value))
		title = 'user replied to message ' + parent_msg.title
		message = form['message'].value
		parent = int(form['msg_id'].value)
		username = 'test' 
		user = meeplib.get_user(username)
		new_message = meeplib.Message(title, message, user, parent, -1)
		
		print "need to update parent!"
		meeplib.Message.update_children(parent_msg, new_message.id)		
		
		headers = [('Content-type', 'text/html')]
		headers.append(('Location', '/m/list'))
		start_response("302 Found", headers)
		return ["reply added"]

	def no_user(self, environ, start_response):
		headers = [('Content-type', 'text/html')]
		start_response("200 OK", headers)
		return """You can't submit a message if you aren't logged in!<p>
			<a href='/login'>Log in</a><p>
			<a href='../../'>Back to Home</a>"""
	
	def __call__(self, environ, start_response):
		# store url/function matches in call_dict
		call_dict = { '/': self.index,
					  '/create_user': self.create_user,
					  '/add_new_user':self.add_new_user,
					  '/login': self.login,
					  '/logout': self.logout,
					  '/m/list': self.list_messages,
					  '/m/add_thread': self.add_thread,
					  '/m/add_thread_action': self.add_thread_action,
					  '/m/add': self.add_message,
					  '/m/add_action': self.add_message_action,
					  '/m/delete_all': self.delete_all_messages_action,
					  '/delete_all_messages_action': self.delete_all_messages_action,
					  '/m/delete_one': self.delete_one_message,
					  '/m/delete_one_action': self.delete_one_message_action,
					  '/m/reply': self.reply,
					  '/m/reply_action': self.reply_action,
			  '/m/delete_message': self.delete_message,
			  '/m/no_user': self.no_user
					  }

		# see if the URL is in 'call_dict'; if it is, call that function.
		url = environ['PATH_INFO']
		fn = call_dict.get(url)

		if fn is None:
			start_response("404 Not Found", [('Content-type', 'text/html')])
			return ["Page not found."]

		try:
			return fn(environ, start_response)
		except:
			tb = traceback.format_exc()
			x = "<h1>Error!</h1><pre>%s</pre>" % (tb,)

			status = '500 Internal Server Error'
			start_response(status, [('Content-type', 'text/html')])
			return [x]