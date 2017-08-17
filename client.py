from tkinter import *
import requests
import json

master = Tk()
main = Frame(master)
main.grid(row=0)
main.columnconfigure(0, minsize=400)
main.rowconfigure(1, minsize=600)
title_frame = Frame(main)
title_frame.grid(row=0, column=0, sticky=N)
title_frame.columnconfigure(0, minsize=350)
vocabulary_frame = Frame(main)
flash_button = Button(title_frame, text='刷新', command=lambda: flash(vocabulary_frame))
flash_button.grid(row=0, column=0, sticky=E)
label_title = Label(title_frame, text='Vocabulary Book', pady=20)
label_title.grid(row=1, column=0)


def flash(frame):
    response = requests.get('http://127.0.0.1:5000/words')
    words = json.loads(response.content)
    frame.grid_remove()
    del frame
    frame = Frame(main)
    frame.grid(row=1, column=0, sticky=N)
    frame.columnconfigure(0, minsize=300)
    draw(frame, words)


def draw(frame, words):
    labels = [Label(frame, text=' ') for i in range(20)]
    for index, word in enumerate(words['words']):
        labels[index]['text'] = '{index}. {word}'.format(index=index + 1, word=word)
    for index, label in enumerate(labels):
        label.grid(row=index, column=0, sticky=W)
    for i in range(len(words['words'])):
        Button(frame, text='记住了').grid(row=i, column=1)

flash(vocabulary_frame)

master.mainloop()
