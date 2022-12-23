import textwrap
from tkinter import *


# class to define the popup text window of the GUI
class TextWindow:
    def __init__(self, root, add_text):
        top = self.top = Toplevel(root)
        top.geometry("1100x500")

        self.text = textwrap.dedent(add_text)
        self.scroll_widget = Scrollbar(top, orient="vertical")
        self.text_widget = Text(top, wrap=WORD, yscrollcommand=self.scroll_widget.set,
                                height=27, width=130)
        self.top_button = Button(top, text="Continue", command=self.cleanup,
                                 width=10, bg="black", fg="white", font=("ariel", 16, " bold"))

        top.title("Read Before Moving On")
        self.scroll_widget.pack(side=RIGHT, fill=Y)
        self.scroll_widget.config(command=self.text_widget.yview)

        self.text_widget.pack()
        self.text_widget.insert(END, add_text)
        self.top_button.pack()
        self.top_button.place(x=450, y=450)

    # destroys the top level GUI
    def cleanup(self):
        self.top.destroy()
