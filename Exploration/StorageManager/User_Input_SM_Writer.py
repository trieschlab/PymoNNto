import threading
import sys
import time

def start_SM_Listener(storage_manager):

    def get_input():
        while True:
            data = input()
            print(data)

    global exit_flag
    exit_flag=False
    global input_thread
    input_thread = threading.Thread(target=get_input, args=(lambda : exit_flag, ))
    input_thread.start()

def terminate_listener():
    global exit_flag
    exit_flag=True

start_SM_Listener(None)

time.sleep(10)

terminate_listener()

