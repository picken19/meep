import meeplib
import traceback
import cgi
from wsgiref import util
import os

def initialize():
    # create a default user
    u = meeplib.User('test', 'foo')

    # create a single message
    meeplib.Message('Greetings Earthlings', 'The meep message board is open.', u, -1, {})

    # done.

class MeepExampleApp(object):
    """
    WSGI app object.
    """
    def index(self, environ, start_response):
        start_response("200 OK", [('Content-type', 'text/html')])

        username = 'test'

        return ["""you are logged in as user: %s.<p><a href='/m/add'>Add a message</a><p><a href='m/delete_one'>Delete a message</a><p><a href='/m/delete_all'>Delete all messages</a><p><a href='/login'>Log in</a><p><a href='/logout'>Log out</a><p><a href='/m/list'>Show messages</a>""" % (username,)]

    def login(self, environ, start_response):
        # hard code the username for now; this should come from Web input!
        username = 'test'

        # retrieve user
        user = meeplib.get_user(username)

        # set content-type
        headers = [('Content-type', 'text/html')]
        
        # send back a redirect to '/'
        k = 'Location'
        v = '/'
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
        start_response('302 Found', headers)
        
        return "no such content"

    #return a list of all messages
    def list_messages(self, environ, start_response):
        messages = meeplib.get_all_messages()

        s = []
        for m in messages:
            s.append('id: %d<p>' % (m.id,))
            s.append('title: %s<p>' % (m.title))
            s.append('message: %s<p>' % (m.post))
            s.append('author: %s<px>' % (m.author.username))
            s.append(
                """<form action='reply' method='POST'><input type='hidden' value='%d' name='msg_id'><input type='submit' value="Reply"></form>""" % (m.id))

            print m.id
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
        
        start_response("200 OK", headers)

        return """<form action='add_action' method='POST'>Title: <input type='text' name='title'><br>Message:<input type='text' name='message'><br><input type='submit'></form>"""

    #add a single message action
    def add_message_action(self, environ, start_response):
        print environ['wsgi.input']
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

        title = form['title'].value
        message = form['message'].value
        
        username = 'test'
        user = meeplib.get_user(username)
        
        new_message = meeplib.Message(title, message, user)

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

    def __call__(self, environ, start_response):
        # store url/function matches in call_dict
        call_dict = { '/': self.index,
                      '/login': self.login,
                      '/logout': self.logout,
                      '/m/list': self.list_messages,
                      '/m/add': self.add_message,
                      '/m/add_action': self.add_message_action,
                      '/m/delete_all': self.delete_all_messages_action,
                      '/m/delete_all_action': self.delete_all_messages_action,
                      '/m/delete_one': self.delete_one_message,
                      '/m/delete_one_action': self.delete_one_message_action,
                      '/m/reply': self.reply,
                      '/m/reply_action': self.reply_action
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

