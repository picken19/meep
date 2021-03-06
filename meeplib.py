"""
meeplib - A simple message board back-end implementation.

Functions and classes:

 * u = User(username, password) - creates & saves a User object.  u.id
	 is a guaranteed unique integer reference.

 * m = Message(title, post, author) - creates & saves a Message object.
	 'author' must be a User object.  'm.id' guaranteed unique integer.

 * get_all_messages() - returns a list of all Message objects.

 * get_all_users() - returns a list of all User objects.

 * delete_message(m) - deletes Message object 'm' from internal lists.

 * delete_user(u) - deletes User object 'u' from internal lists.

 * get_user(username) - retrieves User object for user 'username'.

 * get_message(msg_id) - retrieves Message object for message with id msg_id.

"""

import cPickle
from Cookie import SimpleCookie


__all__ = ['Message', 'get_all_messages', 'get_message', 'delete_message',
		   'User', 'get_user', 'get_all_users', 'delete_user']

###
# internal data structures & functions; please don't access these
# directly from outside the module.	 Note, I'm not responsible for
# what happens to you if you do access them directly.  CTB


# a string, stores the current user that is logged on
_curr_user = []

# a dictionary, storing all messages by a (unique, int) ID -> Message object.
_messages = {}

def _get_next_message_id():
	if _messages:
		return max(_messages.keys()) + 1
	return len(_messages)

# a dictionary, storing all users by a (unique, int) ID -> User object.
_user_ids = {}

# a dictionary, storing all users by username
_users = {}

def _get_next_user_id():
	if _users:
		return max(_user_ids.keys()) + 1
	return 0

def _reset():
	"""
	Clean out all persistent data structures, for testing purposes.
	"""
	global _messages, _users, _user_ids, _curr_user
	_messages = {}
	_users = {}
	_user_ids = {}
	_curr_user = []

def save_state():
	filename = "save.pickle"
	fp = open(filename, 'w')
	objects = (_messages, _user_ids, _users)
	cPickle.dump(objects, fp)
	print "saving"
	print _messages
	fp.close()

def load_state():
	try:
		filename = "save.pickle"
		fp = open(filename, 'r')
		objects = cPickle.load(fp)
		(_messages, _user_ids, _users) = objects
		print "successfully loaded"
		print _messages, _user_ids, _users
		return _messages, _user_ids, _users
	except IOError:
		print "meeplib.load_state() IOError"
		return {}, {}, {}

###
#modify to include parent and children ids
class Message(object):
	"""
	Simple "Message" object, containing title/post/author.
	'author' must be an object of type 'User'.
	'child' must be an object of type 'array'	
	"""

	def __init__(self, title, post, author, parent, child):
		self.title = title
		self.post = post
		self.parent = parent
		self.child = child

		assert isinstance(author, User)
		self.author = author

		self._save_message()

	def _save_message(self):
		self.id = _get_next_message_id()
		
		# register this new message with the messages list:
		_messages[self.id] = self
		
	def update_children(parent_msg, child_id):
		parent_msg.child.append(child_id)
	
def get_all_messages(sort_by='id'):
	return _messages.values()

def get_message(id):
	return _messages[id]

def delete_message(msg):
	assert isinstance(msg, Message)
	del _messages[msg.id]

###

class User(object):
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self._save_user()

	def _save_user(self):
		self.id = _get_next_user_id()
		# register new user ID with the users list:
		_user_ids[self.id] = self
		_users[self.username] = self

def set_curr_user(username):
	_curr_user.insert(0, username)

def get_curr_user():
	return _curr_user[0]

def delete_curr_user(username):
	_curr_user.remove(_curr_user.index(0))

def get_user(username):
	return _users.get(username)			# return None if no such user

def get_all_users():
	return _users.values()

def delete_user(user):
	del _users[user.username]
	del _user_ids[user.id]

def check_user(username, password):
	try:
		aUser = get_user(username)
	except NameError:
		aUser = None
	try:
		password
	except NameError:
		password = None

	if aUser is not None:
			if aUser.password is not None:
				if aUser.password == password:
					return True
	else:
		return False
