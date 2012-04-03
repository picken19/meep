import twill

twill.execute_file("twill_tests/add_message.twill", initial_url="http://localhost:8000")
twill.execute_file("/twill_tests/add_user.twill", initial_url="http://localhost:8000")
twill.execute_file("twill_tests/delete_message.twill", initial_url="http://localhost:8000")
twill.execute_file("/twill_tests/msg_reply.twill", initial_url="http://localhost:8000")
