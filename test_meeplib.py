import unittest
import meeplib

# note:
#
# functions start within test_ are discovered and run
#		between setUp and tearDown;
# setUp and tearDown are run *once* for *each* test_ function.

class TestMeepLib(unittest.TestCase):
	#will be run prior to every test
	def setUp(self):
		u = meeplib.User('foo', 'bar')
		print "\n add m"
		m = meeplib.Message('the title', 'the content', u, -1, {})
		print len(meeplib.get_all_messages())

	def test_for_message_existence(self):
		print "test for message existence"
		messages = meeplib.get_all_messages()
		for m in messages:
			print m.post
		print len(messages)
		assert len(messages) == 1
		assert messages[0].title == 'the title'
		assert messages[0].post == 'the content'
		meeplib._reset()

	def test_message_ownership(self):
		users = meeplib.get_all_users()
		for u in users:
			print u.username
		assert len(users) == 1 #two hardcoded and one added above
		u = users[0]
		messages = meeplib.get_all_messages()
		assert len(messages) == 1
		m = messages[0]
		assert m.author == u
		meeplib._reset()

	def test_get_next_user(self):
		id = meeplib._get_next_user_id()
		assert id != None
		meeplib._reset()

	def test_tearDown(self):
		print "test teardown"
		users = meeplib.get_all_users()
		for user in users:
			meeplib.delete_user(user)
			print meeplib._user_ids
		messages = meeplib.get_all_messages()
		for m in messages:
			meeplib.delete_message(m)
		print len(meeplib._user_ids)
		assert len(meeplib._messages) == 0
		assert len(meeplib._users) == 0
		assert len(meeplib._user_ids) == 0
		meeplib._reset()

	def testAddUser_newportt(self):
		print "test add user"
		meeplib.User("cait","test")
		meeplib.User('new', 'test')
		for user in meeplib.get_all_users():
			print user.username
		assert len(meeplib._users) == 3
		meeplib._reset()
		
if __name__ == '__main__':
	unittest.main()
