#! /usr/bin/env python
import sys
import os
import socket
import unittest


class TestApp(unittest.TestCase):
    def setUp(self):
        pass

    def test_serve2(self):
        print 'Make sure you are running your server on localhost:5123 before this test'
        interface = 'localhost'
        port = '5123'
        message = 'GET /m/list'

        port = int(port)

        sock = socket.socket()

        print 'connecting to', interface, port
        sock.connect((interface, port))

        message = str(len(message)) + ':' + message

        print 'sending %s' % message[0:len(message)-4]
        sock.sendall(message[0:len(message)-4])
        print 'now sending %s' %  message[len(message)-4:len(message)]
        sock.sendall(message[len(message)-4:len(message)])

        x = sock.recv(4096)
        assert 'List Messages' in x

if __name__ == '__main__':
    unittest.main()
