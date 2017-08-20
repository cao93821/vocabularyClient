from tkinter import *
import requests
import json
from threading import Thread
import time
from tkinter.font import Font
from functools import partial, wraps


class Timer:
    def __init__(self, hour=0, minute=0, second=0):
        self.hour = hour
        self.minute = minute
        self.second = second

    def add_time(self):
        if self.second < 59:
            self.second += 1
        elif self.minute < 59:
            self.second = 0
            self.minute += 1
        else:
            self.hour = 0

    def display(self):
        # 使用神奇的format字符串填充解决时间显示的问题
        return '{:0>2}: {:0>2}: {:0>2}'.format(self.hour, self.minute, self.second)


class Proxy:
    def __init__(self, method, *args):
        self.method = method
        self.args = args

    def __call__(self):
        self.method(*self.args)


def frame_init(method):
    """ 任何切换页面的行为都要进行页面初始化 """
    @wraps(method)
    def decorate(self, *args, **kwargs):
        if self.register_frame:
            self.register_frame.grid_remove()
            self.register_frame = None
        if self.login_frame:
            self.login_frame.grid_remove()
            self.login_frame = None
        if self.view_frame:
            self.view_frame.grid_remove()
            self.view_frame = None
        return method(self, *args, **kwargs)
    return decorate


class Vocabulary:
    def __init__(self, root):
        self.root = root
        self.main = Frame(root, height=680, width=800)
        self.main.grid(row=0, padx=10, pady=10)
        self.main.grid_propagate(0)
        self.time_remember = {'hour': 0, 'minute': 0, 'second': 0}
        self.time_flag = 1
        self.control_frame = Frame(self.main)
        self.control_frame.grid(row=0)
        self.control_frame.columnconfigure([i for i in range(8)], minsize=100)

        self.control_refresh = Button(self.control_frame, text='刷新', command=lambda: self.refresh(1))
        self.control_refresh.grid(column=7)

        self.suspend_text = StringVar()
        self.suspend_text.set('暂停计时')
        self.control_suspend = Button(self.control_frame, textvariable=self.suspend_text, command=lambda: self.switch())
        self.control_suspend.grid(column=6, row=0)

        self.control_register = Button(self.control_frame, text='注册', command=self.register_frame_init)
        self.control_register.grid(column=5, row=0)

        self.control_timer = None
        self.view_frame = None
        self.view_title = None
        self.view_paging_frame = None
        self.total_time = StringVar()
        self.control_timer = Label(self.control_frame, textvariable=self.total_time)
        self.control_timer.grid(column=0, row=0, columnspan=2, sticky=W + N)

        # self.url = 'http://127.0.0.1:5000'
        self.url = 'http://139.196.77.131:5000'

        self.login_frame = None
        self.register_frame = None
        self.login_alert = None

        thread = Thread(target=self.timer_start)
        thread.start()
        self.login_frame_init()

        # self.refresh(1)

    @frame_init
    def login_frame_init(self):
        self.login_frame = Frame(self.main, padx=30, height=600)
        self.login_frame.rowconfigure([i for i in range(15)], weight=1)  # weight必须结合父widget固定大小才能使用，否则无效

        # 我之前对于weight的用法一直都是有误解的，一组index使用weight不能改变他们所占的比例
        self.login_frame.columnconfigure(0, weight=1)
        self.login_frame.columnconfigure(1, weight=1)

        self.login_frame.grid(row=1, sticky=W + E)  # 对于frame需要进行这样的设置，或者固定frame的大小
        self.login_frame.grid_propagate(0)
        self.login_lable = Label(self.login_frame, text='欢迎来到猪猪单词本')
        self.login_lable.grid(row=5, column=0, columnspan=2)
        self.login_username_label = Label(self.login_frame, text='账号')
        self.login_username_label.grid(row=6, column=0, sticky=E)
        self.login_username = Entry(self.login_frame)
        self.login_username.grid(row=6, column=1, sticky=W)
        self.login_password_label = Label(self.login_frame, text='密码')
        self.login_password_label.grid(row=7, column=0, sticky=E)
        self.login_password = Entry(self.login_frame, show='*')
        self.login_password.grid(row=7, column=1, sticky=W)

        # 这个button中的参数需要及时取用，所以不需要对参数进行保存
        self.login_button = Button(self.login_frame,
                                   text='登录', width=19,
                                   command=lambda: self.login(self.login_username.get(), self.login_password.get())
                                   )  # mac无法设置button的高度，太蛋疼了
        self.login_button.grid(row=8,
                               column=0,
                               columnspan=2)

    @frame_init
    def register_frame_init(self):
        self.register_frame = Frame(self.main, padx=30, height=600)
        self.register_frame.rowconfigure([i for i in range(15)], weight=1)  # weight必须结合父widget固定大小才能使用，否则无效

        # 我之前对于weight的用法一直都是有误解的，一组index使用weight不能改变他们所占的比例
        self.register_frame.columnconfigure(0, weight=1)
        self.register_frame.columnconfigure(1, weight=1)

        self.register_frame.grid(row=1, sticky=W + E)  # 对于frame需要进行这样的设置，或者固定frame的大小
        self.register_frame.grid_propagate(0)
        self.register_lable = Label(self.register_frame, text='欢迎来到猪猪单词本')
        self.register_lable.grid(row=5, column=0, columnspan=2)
        self.register_username_label = Label(self.register_frame, text='账号')
        self.register_username_label.grid(row=6, column=0, sticky=E)
        self.register_username = Entry(self.register_frame)
        self.register_username.grid(row=6, column=1, sticky=W)
        self.register_password_label = Label(self.register_frame, text='密码')
        self.register_password_label.grid(row=7, column=0, sticky=E)
        self.register_password = Entry(self.register_frame, show='*')
        self.register_password.grid(row=7, column=1, sticky=W)
        self.register_button = Button(self.register_frame,
                                      text='注册', width=19,
                                      command=lambda: self.register(self.register_username.get(), self.register_password.get())
                                      )  # mac无法设置button的高度，太蛋疼了
        self.register_button.grid(row=8,
                               column=0,
                               columnspan=2)

    def login(self, username, password):
        login_json = json.dumps({'username': username, 'password': password})
        response = requests.post(self.url + '/login', json=login_json)
        if response.status_code == 404:
            if self.login_alert:
                self.login_alert.grid_remove()
            self.login_alert = Label(self.login_frame, text='账户不存在')
            self.login_alert.grid(row=9, column=0, columnspan=2)
        if response.status_code == 403:
            if self.login_alert:
                self.login_alert.grid_remove()
            self.login_alert = Label(self.login_frame, text='密码错误')
            self.login_alert.grid(row=9, column=0, columnspan=2)
        if response.status_code == 200:
            self.token = response.json()['token']
            self.refresh(1)

    def register(self, username, password):
        register_json = json.dumps({'username': username, 'password': password})
        response = requests.post(self.url + '/register', json=register_json)
        if response.status_code == 200:
            self.token = response.json()['token']
            self.refresh(1)

    def switch(self):
        if self.time_flag == 1:
            self.time_flag = 0
            self.suspend_text.set('开始计时')
        else:
            self.time_flag = 1
            thread = Thread(target=self.timer_start)
            thread.start()
            self.suspend_text.set('暂停计时')

    def timer_start(self):
        timer = Timer(self.time_remember['hour'], self.time_remember['minute'], self.time_remember['second'])
        while self.time_flag:
            time.sleep(1)
            timer.add_time()
            self.total_time.set('复习时间 ' + timer.display())
            self.time_remember['hour'] = timer.hour
            self.time_remember['minute'] = timer.minute
            self.time_remember['second'] = timer.second

    @frame_init
    def refresh(self, current_index):
        response = requests.get(self.url + '/words')
        words = json.loads(response.content)

        # 如果view_frame已存在，移除当前view_frame并重新绘制
        # if hasattr(self, 'view_frame'):

        self.view_frame = Frame(self.main, padx=30)
        self.view_frame.columnconfigure([i for i in range(6)], weight=1)
        self.view_frame.rowconfigure([i for i in range(23)], minsize=28)
        self.view_frame.grid(row=1, sticky=W + E + N + S)

        # 在view_frame当中增加view_title显示标题
        self.view_title = Label(self.view_frame, text='猪猪单词本')
        self.view_title.grid(row=0, column=0, columnspan=6)

        # 显示单词及其释义
        word_id_list = [word_id for word_id in words.keys()]
        current_word_id_list = word_id_list[(current_index - 1) * 20:current_index * 20]
        for index, word_id in enumerate(current_word_id_list):
            Label(self.view_frame,
                  text='{index}. {word}'.format(index=index + 1,
                                                word=words[word_id]['word'])).grid(row=index + 1, column=0, sticky=W)

            word_explain = words[word_id]['word_explain']
            if word_explain is not None and len(word_explain) >= 40:
                word_explain = word_explain[0:40] + '...'
            Label(self.view_frame, text='{}'.format(word_explain)).grid(row=index + 1, column=1, sticky=W, columnspan=4)

            button = Button(self.view_frame, text='记住了')
            button['command'] = Proxy(self.keep_in_mind, button, word_id)
            button.grid(row=index + 1, column=5, sticky=E)

        # 绘制分页
        self.paging(len(words), current_index)

    def paging(self, words_count, current_index):
        self.view_paging_frame = Frame(self.view_frame)
        self.view_paging_frame.grid(row=22, column=0, columnspan=6, sticky=W + E + N + S)
        self.view_paging_frame.columnconfigure([i for i in range(30)], weight=1)
        if words_count % 20 == 0:
            total_index = words_count // 20
        else:
            total_index = words_count // 20 + 1
        if total_index <= 7:
            start_index = 1
            end_index = total_index
        elif current_index <= 4:
            start_index = 1
            end_index = 7
        elif current_index + 3 <= total_index:
            start_index = current_index - 3
            end_index = total_index
        else:
            start_index = current_index - 3
            end_index = current_index + 3
        n = 0
        for i in range(start_index, end_index + 1):
            button = Button(self.view_paging_frame, text='{}'.format(i), padx=10, command=Proxy(self.refresh, i))
            button.grid(row=0, column=29 + start_index - end_index + n)
            n += 1

    def keep_in_mind(self, button, word_id):
        # requests.put('http://127.0.0.1:5000/word/{}'.format(word_id))
        # 开发环境
        requests.put(self.url + '/word/{}'.format(word_id))
        # 线上环境
        button['state'] = 'disable'
        self.root.update()


master = Tk()
vocabulary = Vocabulary(master)
master.mainloop()
