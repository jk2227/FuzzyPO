from Tkinter import *
import tkFont
from JRecInterface import JRecInterface

def iter(interface, textbox, res):
    interface.response(res)
    req = interface.request()
    article = interface.request().article
    stats = interface.recommender.color_stats()
    textbox.delete('1.0', END)
    textbox.insert(END, "Round: " + str(req.num) + "\n"
                   + "Doc ID: " + req.id + "\n"
                   + "Algo: " + req.info + "\n"
                   + "Colored Yes: " + str(stats[1]) + "  No: " + str(stats[0]) + "\n\n"
                   +  article.text.replace(' ', '\n'))

def ExampleUI():
    tk = Tk()
    tk.title('SimpleUI       NHK_easy     Sona Tithew')
    tk.resizable(0, 0)
    textbox = Text(tk, font=tkFont.Font(size=12))
    interface = JRecInterface()
    req = interface.request()
    article = interface.request().article
    stats = interface.recommender.color_stats()
    textbox.insert(END, "Round: " + str(req.num) + "\n"
                   + "Doc ID: " + req.id + "\n"
                   + "Algo: " + req.info + "\n"
                   + "Colored Yes: " + str(stats[1]) + "  No: " + str(stats[0]) + "\n\n"
                   +  article.text.replace(' ', '\n'))
    textbox.grid(row=0, column=0, columnspan=5)
    m = IntVar()
    m.set(2)
    #Radiobutton(tk, text='0%', variable=m, value=4).grid(row=1, column=0, sticky=N + S + E + W)
    #Radiobutton(tk, text='25%', variable=m, value=3).grid(row=1, column=1, sticky=N + S + E + W)
    #Radiobutton(tk, text='50%', variable=m, value=2).grid(row=1, column=2, sticky=N + S + E + W)
    #Radiobutton(tk, text='75%', variable=m, value=1).grid(row=1, column=3, sticky=N + S + E + W)
    #Radiobutton(tk, text='100%', variable=m, value=0).grid(row=1, column=4, sticky=N + S + E + W)
    #e = IntVar()
    #e.set(1)
    # Radiobutton(tk, text='I prefer easier articles.', variable=e, value=0).grid(row=2, column=1, sticky=N + S + E + W)
    # Radiobutton(tk, text='I enjoy this article!', variable=e, value=1).grid(row=2, column=2, sticky=N + S + E + W)
    # Radiobutton(tk, text='I prefer harder articles.', variable=e, value=2).grid(row=2, column=3, sticky=N + S + E + W)
    # Button(tk, text='Submit', height=1, width=12, font=tkFont.Font(size=24), command = lambda: self.kb_iter(textbox, m.get(), e.get())).grid(row=3, column=1, columnspan=3)
    Button(tk, text='Yes', height=1, width=22, font=tkFont.Font(size=10),
           command=lambda: iter(interface, textbox, True)).grid(row=1, column=1, sticky=N + S + E + W)
    Button(tk, text='No', height=1, width=22, font=tkFont.Font(size=10),
           command=lambda: iter(interface, textbox, False)).grid(row=1, column=2, sticky=N + S + E + W)
    tk.mainloop()

ExampleUI()