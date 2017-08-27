from tkinter import *
import os
import pickle
from new_client.frames import ViewFrame, LoginFrame, RegisterFrame
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(name)20s: %(levelname)5s: %(message)s'))
logger.addHandler(handler)


class Vocabulary:
    def __init__(self, root):
        """初始化Vocabulary

        :param root: 根页面
        :type root: Tk
        """
        self.root = root
        self.main = Frame(root, height=680, width=800)
        self.main.grid(row=0, padx=10, pady=10)
        self.main.grid_propagate(0)
        self.time_remember = {'hour': 0, 'minute': 0, 'second': 0}
        logger.debug('time_remember = {} {} {}'.format(
            self.time_remember['hour'],
            self.time_remember['minute'],
            self.time_remember['second']
        ))
        self.token = None
        self.time_count = None
        self.view_frame = ViewFrame(self, self.main, padx=30)
        self.login_frame = LoginFrame(self, self.main, padx=30, height=600, width=800)
        self.register_frame = RegisterFrame(self, self.main, padx=30, height=600, width=800)

        # self.url = 'http://139.196.77.131:5000'
        self.url = 'http://127.0.0.1:5000'

    def start(self):
        """开始初始化页面"""
        try:
            with open('time_count', 'rb') as f:
                self.time_count = pickle.load(f)
                logger.debug('time_count = {}'.format(self.time_count))
        except FileNotFoundError:
            self.time_count = 0

        try:
            with open('token') as f:
                self.token = f.read()

        except FileNotFoundError:
            self.token = None

        if self.token:
            self.refresh(1)
        else:
            self.login_frame_init()

    def log_out(self):
        """登出操作"""
        try:
            os.remove('token')
        except FileNotFoundError:
            pass
        self.login_frame_init()

    def login_frame_init(self):
        self.login_frame.init()

    def register_frame_init(self):
        self.register_frame.init()

    def refresh(self, current_index):
        self.view_frame.refresh(current_index)


master = Tk()
vocabulary = Vocabulary(master)
vocabulary.start()

master.mainloop()
