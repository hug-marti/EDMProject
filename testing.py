from tkinter import *

root = Tk()
root.title("Using Frames")
root.geometry("400x600")

frame = LabelFrame(root, text="pages",
                   padx=5, pady=5)
frame.pack(padx=10, pady=10)


def create_window():
    window1 = Toplevel()
    btn = Button(window1, text="destroy main page", command=root.withdraw)
    btn.pack()
    btn2 = Button(window1, text="open main page", command=root.deiconify)
    btn2.pack()
    window1.mainloop()


b1 = Button(frame, text="create window 2", command=create_window)
b1.pack()
root.mainloop()