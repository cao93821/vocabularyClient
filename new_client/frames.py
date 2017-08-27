from tkinter import *
from .tools import Proxy, Timer, frame_init
import requests
import json
from threading import Thread
import pickle
import time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(name)20s: %(levelname)5s: %(message)s'))
logger.addHandler(handler)


class ViewFrame(Frame):
    def __init__(self, upper_frame, *args, **kwargs):
        """构造函数，初始化view_frame

        :param upper_frame: master
        :param args: Frame构造函数所接受的参数
        :param kwargs: Frame构造函数所接受的参数
        """
        super().__init__(*args, **kwargs)

        self.columnconfigure([i for i in range(6)], weight=1)
        self.rowconfigure([i for i in range(23)], minsize=28)
        self.upper_frame = upper_frame
        self._time_flag = 1
        self.is_deleted = True
        logger.info('ViewFrame.is_deleted = {}'.format(self.is_deleted))
        self.view_title = None
        self.view__paging_frame = None
        self._control_frame = None

    def delete(self):
        """移除本Frame及其上的所有widget"""
        self.grid_remove()
        for widget in self.grid_slaves():
            widget.grid_remove()

        self.is_deleted = True

    @frame_init
    def refresh(self, current_index):
        """根据提供的页数渲染view_frame

        :param current_index: 单词本的页数
        :type current_index: int
        :return: 如果数据请求失败则停止渲染进入到登录页面
        """
        token_json = json.dumps({'token': self.upper_frame.token})
        response = requests.get(self.upper_frame.url + '/words', json=token_json)
        logger.debug('view_frame response code = {}'.format(response.status_code))

        if response.status_code == 404:
            return self.upper_frame.login_frame_init()
        words = json.loads(response.content)
        logger.debug('view_frame json = {}'.format(response.json()))

        self.grid(row=0, sticky=W + E + N + S)
        self.is_deleted = False

        self.vocabulary_control_init()

        self.view_title = Label(self, text='猪猪单词本')
        self.view_title.grid(row=1, column=0, columnspan=6)

        # 显示单词及其释义
        word_id_list = [word_id for word_id in words.keys()]
        current_word_id_list = word_id_list[(current_index - 1) * 20:current_index * 20]

        for index, word_id in enumerate(current_word_id_list):
            Label(self, text='{index}. {word}'.format(
                index=index + 1,
                word=words[word_id]['word'])).grid(row=index + 2, column=0, sticky=W)

            word_explain = words[word_id]['word_explain']
            if word_explain is not None and len(word_explain) >= 35:
                word_explain = word_explain[0:35] + '...'
            Label(self, text='{}'.format(word_explain)).grid(row=index + 2, column=1, sticky=W, columnspan=4)

            button = Button(self, text='记住了')
            button['command'] = Proxy(self._keep_in_mind, button, word_id)
            button.grid(row=index + 2, column=5, sticky=E)

        # 绘制分页
        self._paging(len(words), current_index)

    def _paging(self, words_count, current_index):
        """绘制分页

        :param words_count: 单词总数
        :type words_count: int
        :param current_index: 当前页数
        :type current_index: int
        """
        self.view__paging_frame = Frame(self)
        self.view__paging_frame.grid(row=22, column=0, columnspan=6, sticky=W + E + N + S)
        self.view__paging_frame.columnconfigure([i for i in range(30)], weight=1)

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
            button = Button(self.view__paging_frame, text='{}'.format(i), padx=10, command=Proxy(self.refresh, i))
            button.grid(row=0, column=29 + start_index - end_index + n)
            n += 1

    def _keep_in_mind(self, button, word_id):
        """记住单词，使之下次不会再出现

        :param button: 点击记住单词的按钮
        :type button: tkinter.Button
        :param word_id: 单词的id
        """
        response = requests.put(self.upper_frame.upper_frame.url + '/word/{}'.format(word_id))
        button['state'] = 'disable'
        logger.debug('keep_in_mind response code = {}'.format(response.status_code))
        self.upper_frame.root.update()

    def vocabulary_control_init(self):
        """渲染view_frame的控制栏"""
        self._control_frame = Frame(self)
        self._control_frame.grid(row=0, column=0, columnspan=6)
        self._control_frame.columnconfigure([i for i in range(8)], minsize=90)

        control_refresh = Button(self._control_frame, text='刷新', command=lambda: self.refresh(1))
        control_refresh.grid(column=7, row=0)

        control_logout = Button(self._control_frame, text='退出登录', command=self.upper_frame.log_out)
        control_logout.grid(column=5, row=0)

        self.suspend_text = StringVar()
        self.suspend_text.set('暂停计时')

        control_suspend = Button(self._control_frame, textvariable=self.suspend_text, command=lambda: self._switch())
        control_suspend.grid(column=6, row=0)

        self.total_time = StringVar()
        control_timer = Label(self._control_frame, textvariable=self.total_time)
        control_timer.grid(column=0, row=0, columnspan=2, sticky=W + N)

        thread = Thread(target=self._timer_start)
        thread.start()

    def _timer_start(self):
        """开始计时"""
        timer = Timer(
            self.upper_frame.time_remember['hour'],
            self.upper_frame.time_remember['minute'],
            self.upper_frame.time_remember['second']
            )
        while self._time_flag:
            time.sleep(1)
            timer.add_time()
            self.total_time.set('复习时间 ' + timer.display())
            self.upper_frame.time_remember['hour'] = timer.hour
            self.upper_frame.time_remember['minute'] = timer.minute
            self.upper_frame.time_remember['second'] = timer.second

            if timer.second == 0:
                self.upper_frame.time_count += 60
                # 每隔60s将已复习时间持久化存储至本地
                with open('time_count', 'wb') as f:
                    pickle.dump(self.upper_frame.time_count, f)

    def _switch(self):
        """开始计时按钮显示的变化"""
        if self._time_flag == 1:
            self._time_flag = 0
            self.suspend_text.set('开始计时')
        else:
            self._time_flag = 1
            thread = Thread(target=self._timer_start)
            thread.start()
            self.suspend_text.set('暂停计时')


class LoginFrame(Frame):
    def __init__(self, upper_frame, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rowconfigure([i for i in range(15)], weight=1)  # weight必须结合父widget固定大小才能使用，否则无效
        self.upper_frame = upper_frame
        self.is_deleted = True
        self._login_alert = None
        self._control_frame = None

    def delete(self):
        self.grid_remove()
        self.is_deleted = True

    @frame_init
    def init(self):
        self._control_frame = Frame(self)
        self._control_frame.grid(row=0, column=0, columnspan=2)
        self._control_frame.columnconfigure([i for i in range(8)], minsize=90)

        control_register = Button(self._control_frame, text='注册', command=self.upper_frame.register_frame_init)
        control_register.grid(column=7, row=0)

        self.upper_frame.token = None

        # 我之前对于weight的用法一直都是有误解的，一组index使用weight不能改变他们所占的比例
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.grid(row=0, sticky=W + E + S + N)  # 对于frame需要进行这样的设置，或者固定frame的大小
        self.grid_propagate(0)
        self.is_deleted = False

        login_label = Label(self, text='欢迎来到猪猪单词本')
        login_label.grid(row=5, column=0, columnspan=2)

        login_username_label = Label(self, text='账号')
        login_username_label.grid(row=6, column=0, sticky=E)

        login_username = Entry(self)
        login_username.grid(row=6, column=1, sticky=W)

        login_password_label = Label(self, text='密码')
        login_password_label.grid(row=7, column=0, sticky=E)

        login_password = Entry(self, show='*')
        login_password.grid(row=7, column=1, sticky=W)

        # 这个button中的参数需要及时取用，所以不需要对参数进行保存
        self.login_button = Button(self,
                                   text='登录', width=19,
                                   command=lambda: self._login(login_username.get(), login_password.get())
                                   )  # mac无法设置button的高度，太蛋疼了
        self.login_button.grid(row=8,
                               column=0,
                               columnspan=2)

    def _login(self, username, password):
        login_json = json.dumps({'username': username, 'password': password})
        response = requests.post(self.upper_frame.url + '/login', json=login_json)
        logger.debug('login response code = {}'.format(response.status_code))

        if response.status_code == 404:
            if self._login_alert:
                self._login_alert.grid_remove()
            _login_alert = Label(self, text='账户不存在')
            _login_alert.grid(row=9, column=0, columnspan=2)

        if response.status_code == 403:
            if self._login_alert:
                self._login_alert.grid_remove()
            self._login_alert = Label(self, text='密码错误')
            self._login_alert.grid(row=9, column=0, columnspan=2)

        if response.status_code == 200:
            self.upper_frame.token = response.json()['token']
            with open('token', 'w') as f:
                f.write(self.upper_frame.token)
            self.upper_frame.refresh(1)


class RegisterFrame(Frame):
    def __init__(self, upper_frame, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rowconfigure([i for i in range(15)], weight=1)  # weight必须结合父widget固定大小才能使用，否则无效
        self.upper_frame = upper_frame
        self.is_deleted = True
        self._control_frame = None

    def delete(self):
        self.grid_remove()
        self.is_deleted = True

    @frame_init
    def init(self):
        if self._control_frame:
            self._control_frame.grid_remove()

        self._control_frame = Frame(self)
        self._control_frame.grid(row=0, column=0, columnspan=2)
        self._control_frame.columnconfigure([i for i in range(9)], minsize=90)

        control_register = Button(
            self._control_frame,
            text='登录',
            command=self.upper_frame.login_frame_init)

        control_register.grid(column=8, row=0)

        self.rowconfigure([i for i in range(15)], weight=1)  # weight必须结合父widget固定大小才能使用，否则无效

        # 我之前对于weight的用法一直都是有误解的，一组index使用weight不能改变他们所占的比例
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.grid(row=1, sticky=W + E)  # 对于frame需要进行这样的设置，或者固定frame的大小
        self.grid_propagate(0)
        self.is_deleted = False

        register_label = Label(self, text='欢迎来到猪猪单词本')
        register_label.grid(row=5, column=0, columnspan=2)

        register_username_label = Label(self, text='账号')
        register_username_label.grid(row=6, column=0, sticky=E)

        register_username = Entry(self)
        register_username.grid(row=6, column=1, sticky=W)

        register_password_label = Label(self, text='密码')
        register_password_label.grid(row=7, column=0, sticky=E)

        register_password = Entry(self, show='*')
        register_password.grid(row=7, column=1, sticky=W)

        register_button = Button(
            self,
            text='注册',
            width=19,
            command=lambda: self.register(
                register_username.get(),
                register_password.get()
            )
        )  # mac无法设置button的高度，太蛋疼了
        register_button.grid(row=8,
                             column=0,
                             columnspan=2)

    def register(self, username, password):
        register_json = json.dumps({'username': username, 'password': password})
        response = requests.post(self.upper_frame.url + '/register', json=register_json)
        logger.debug('register response code = {}'.format(response.status_code))

        if response.status_code == 200:
            self.upper_frame.token = response.json()['token']
            with open('token', 'w') as f:
                f.write(self.upper_frame.token)
            self.upper_frame.refresh(1)

