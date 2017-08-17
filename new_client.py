from tkinter import *
import requests
import json


class Proxy:
    def __init__(self, method, *args):
        self.method = method
        self.args = args

    def __call__(self):
        self.method(*self.args)


class Vocabulary:
    def __init__(self, root):
        self.root = root
        self.main = Frame(root)
        self.main.grid(row=0, padx=10, pady=10)
        self.main.columnconfigure(0, minsize=800)
        self.main.rowconfigure(1, minsize=600)
        self.main.rowconfigure(0, minsize=30)
        self.control_frame = Frame(self.main)
        self.control_frame.grid(row=0)
        self.control_frame.columnconfigure([i for i in range(8)], minsize=100)
        self.control_refresh = Button(self.control_frame, text='刷新', command=self.refresh)
        self.control_refresh.grid(column=7)
        self.view_frame = Frame(self.main)
        self.refresh()

    def refresh(self):
        response = requests.get('http://139.196.77.131:5000/words')
        words = json.loads(response.content)
        self.view_frame.grid_remove()
        self.view_frame = Frame(self.main)
        self.view_frame.grid(row=1)
        self.view_frame.columnconfigure([i for i in range(5)], minsize=120)
        self.view_frame.rowconfigure([i for i in range(21)], minsize=30)
        view_title = Label(self.view_frame, text='猪猪单词本')
        view_title.grid(row=0, column=0, columnspan=6)
        for index, word_id in enumerate(words):
            Label(self.view_frame,
                  text='{index}. {word}'.format(index=index + 1,
                                                word=words[word_id]['word'])).grid(row=index + 2, column=0, sticky=W)
            word_explain = words[word_id]['word_explain']
            if len(word_explain) >= 40:
                word_explain = word_explain[0:40] + '...'
            Label(self.view_frame, text='{}'.format(word_explain)).grid(row=index + 2, column=1, sticky=W, columnspan=4)
            button = Button(self.view_frame, text='记住了')
            button['command'] = Proxy(self.keep_in_mind, button, word_id)
            button.grid(row=index + 2, column=5)

    def keep_in_mind(self, button, word_id):
        # requests.put('http://127.0.0.1:5000/word/{}'.format(word_id))
        # 开发环境
        requests.put('http://139.196.77.131:5000/word/{}'.format(word_id))
        # 线上环境
        button['state'] = 'disable'
        self.root.update()


master = Tk()
vocabulary = Vocabulary(master)
master.mainloop()
