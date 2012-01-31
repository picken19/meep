import unittest
import meeplib

# note:
#
# functions start within test_ are discovered and run
#       between setUp and tearDown;
# setUp and tearDown are run *once* for *each* test_ function.

class TestMeepLib(unittest.TestCase):
    def setUp(self):
        u = meeplib.User('foo', 'bar')
        m = meeplib.Message('the title', 'the content', u, -1, {})

    def test_for_message_existence(self):
        x = meeplib.get_all_messages()
        assert len(x) == 1
        assert x[0].title == 'the title'
        assert x[0].post == 'the content'

    def test_message_ownership(self):
        x = meeplib.get_all_users()
        assert len(x) == 1
        u = x[0]

        x = meeplib.get_all_messages()
        assert len(x) == 1
        m = x[0]

        assert m.author == u

    def tearDown(self):
        msg_list = meeplib.get_all_messages()

        for m in msg_list:
            meeplib.delete_message(m)

        usr_list = meeplib.get_all_users()

        for u in usr_list:
            meeplib.delete_user(u)

        assert len(meeplib._messages) == 0
        assert len(meeplib._users) == 0
        assert len(meeplib._user_ids) == 0

    def testAddUser_newportt(self):
        meeplib.User("cait","test")
        meeplib.User('new', 'test')
        
        assert len(meeplib._users) == 3 #two hardcoded users in main body of code, third user added here
        

if __name__ == '__main__':
    unittest.main()
