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
        m = meeplib.Message( 'the content', u)
        t = meeplib.Thread('TestingPage')
        t.add_post(m)

    def test_for_message_existence(self):
        x = meeplib.get_all_threads()
        y = x[0].get_all_posts()
        assert len(y) == 1
        assert x[0].title == 'TestingPage'
        assert y[0].post == 'the content'

    def test_message_ownership(self):
        x = meeplib.get_all_users()
        assert len(x) == 1
        u = x[0]

        threads = meeplib.get_all_threads()
        for thread in threads:
            messages = thread.get_all_posts()
            for message in messages:
                print message.author
                assert message.author == u

    def test_get_next_user(self):
        x = meeplib._get_next_user_id()
        assert x != None

    def tearDown(self):
        m = meeplib.get_all_threads()
        p = m[0].get_all_posts('id')
        m[0].delete_post(p[0])

        u = meeplib.get_all_users()[0]
        meeplib.delete_user(u)

        assert len(meeplib._messages) == 0
        assert len(meeplib._users) == 0
        assert len(meeplib._user_ids) == 0

if __name__ == '__main__':
    unittest.main()
