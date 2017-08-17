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
        self.main = Frame(root, height=680, width=800)
        self.main.grid(row=0, padx=10, pady=10)
        self.main.grid_propagate(0)
        self.control_frame = Frame(self.main)
        self.control_frame.grid(row=0)
        self.control_frame.columnconfigure([i for i in range(8)], minsize=100)
        self.control_refresh = Button(self.control_frame, text='刷新', command=lambda: self.refresh(1))
        self.control_refresh.grid(column=7)
        self.view_frame = None
        self.view_title = None
        self.view_paging_frame = None
        self.refresh(1)

    def refresh(self, current_index):
        # response = requests.get('http://139.196.77.131:5000/words')
        response = requests.get('http://127.0.0.1:5000/words')
        words = json.loads(response.content)\

        # 如果view_frame已存在，移除当前view_frame并重新绘制
        if hasattr(self, 'view_frame'):
            self.view_frame.grid_remove()
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
        requests.put('http://127.0.0.1:5000/word/{}'.format(word_id))
        # 开发环境
        # requests.put('http://139.196.77.131:5000/word/{}'.format(word_id))
        # 线上环境
        button['state'] = 'disable'
        self.root.update()


master = Tk()
vocabulary = Vocabulary(master)
master.mainloop()
