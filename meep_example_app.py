import meeplib
import traceback
import cgi
from wsgiref import util
import os

def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')
    meeplib.User('new', 'test')

    # create a single message

    meeplib.Message('Greetings Earthlings', 'The meep message board is open.', u, -1, {})

    # done.

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    global username
    username = ''
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])
	
	global username

        return ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='m/delete_one'>Delete a message</a><p><a href='/m/delete_all'>Delete all messages</a><p><a href='/login'>Log in</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (username,)]

    def login(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        
        start_response("200 OK", headers)

        return """<form action='login_action' method='POST'>Username: <input type='text' name='username' value=''><br>Password: <input type='password' name='password' value=''><br><input type='submit'></form>"""

    def login_action(self, environ, start_response):
	print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

	global username
	if "username" not in form or "password" not in form:
	    #If either field is left blank on login, redirect to error page.
	    headers = [('Content-type', 'text/html')] 
            headers.append(('Location', '/invalid_login'))
            start_response('302 Found', headers)
            return "no such content"

	tryuser = form['username'].value
	trypass = form['password'].value
	login_success = False

	users = meeplib.get_all_users()
	for u in users:
	    if u.username == tryuser:
		if u.password == trypass:
		    username = tryuser
		    login_success = True
	if login_success:
	    #login successful, redirect to index
	    k = 'Location'
	    v = '/'
	else:
            #login failed, redirect to error page
	    k = 'Location'
	    v = '/invalid_login'
	    
        # set content-type
        headers = [('Content-type', 'text/html')]
        
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    def invalid_login(self, environ, start_response):
        headers = [('Content-type', 'text/html')]
        start_response("200 OK", headers)
	return """Invalid username or password<p>
		<a href='/login'>Retry Login?</a><p>
		<a href='../../'>Back to Home</a>"""

    def logout(self, environ, start_response):
        #Resets username back to '' instead of current user
	global username
	username = ''
        headers = [('Content-type', 'text/html')]

        # send back a redirect to '/'
        k = 'Location'
        v = '/'
        headers.append((k, v))
        start_response('302 Found', headers)
        
        return "no such content"

    #return a list of all messages
    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()

        s = []
        for m in messages:
            s.append('id: %d<p>' % (m.id))
            s.append('title: %s<p>' % (m.title))
            s.append('message: %s<p>' % (m.post))
            s.append('author: %s<px>' % (m.author.username))
            s.append(
                """<form action='reply' method='POST'><input type='hidden' value='%d' name='msg_id'><input type='submit' value="Reply"></form>""" % (m.id))

            print m.id

	    s.append('<form action="delete_message" method="POST"><input type="hidden" name="id" value="%d"><input type="submit" value="Delete Message"></form>' % (m.id))

            s.append('<hr>')
#
#            if len(m.child):
#                s.append('----------------------')
#                for c in m.child:
#                    s.append('child id: %s<p>' % c)
#            else:
#                s.append("<a href='.../reply/'>reply</a>")
#            s.append('<hr>')

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
            return """<form action='add_action' method='POST'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='submit'></form>"""

    #add a single message action
    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        
        user = meeplib.get_user(username)
        
        new_message = meeplib.Message(title, message, user, -1, {})

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
        s = """<form action='reply_action' method='POST'>Message:<input type='text' name='message'><br><input type='hidden' name='msg_id' value='%d'><br><input type='submit' value='Submit'></form>""" % (int(form['msg_id'].value))
        print s
        return s                                                              

    def reply_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
        print 'reply_action a'
        parent_msg = meeplib.get_message(int(form['msg_id'].value))
        title = 'user replied to message ' + parent_msg.title
        print 'reply_action b'
        print title
        message = form['message'].value
        parent = int(form['msg_id'].value)
        username = 'test' 
        user = meeplib.get_user(username)
        new_message = meeplib.Message(title, message, user, parent, -1)
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

    def delete_message(self, environ, start_response):
	print environ['wsgi.input']
	form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

	# Get the message id from form, convert to int
	id = int(form['id'].value)
	
	# Get message using built in function, delete the message
	message = meeplib.get_message(id)
	meeplib.delete_message(message)

	headers = [('Content-type', 'text/html')]
	headers.append(('Location', '/m/list'))
	start_response("302 Found", headers)
	return ["message deleted"]
    
    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
		      '/login_action': self.login_action,
		      '/invalid_login': self.invalid_login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/delete_all': self.delete_all_messages_action,
                      '/m/delete_all_action': self.delete_all_messages_action,
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

