# -*- coding: utf-8 -*-
# Spinner based on https://gist.github.com/cevaris/79700649f0543584009e
from __future__ import print_function

import itertools
import sys
import time
import threading


class Spinner(object):
    spinner_cycle = itertools.cycle(['⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽'])

    def __init__(self, message='', remove_message=True):
        self.stop_running = threading.Event()
        self.spin_thread = threading.Thread(target=self.init_spin)
        self.message = message
        self.remove_message = remove_message

    def start(self):
        self.spin_thread.start()

    def stop(self):
        self.stop_running.set()
        if self.message and self.remove_message:
            sys.stderr.write('\b' * len(self.message))
        self.spin_thread.join()

    def init_spin(self):
        while not self.stop_running.is_set():
            sys.stderr.write(next(self.spinner_cycle))
            sys.stderr.flush()
            time.sleep(0.35)
            sys.stderr.write('\b')

    def __enter__(self):
        if self.message:
            sys.stderr.write(self.message)
        self.start()

    def __exit__(self, *args):
        self.stop()
