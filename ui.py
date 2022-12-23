# Simple Quiz using Tkinter
from tkinter import *
from text_window import TextWindow


class Quiz:
    def __init__(self, q_list):
        # Create a GUI Window
        self.root = Tk()

        # set the size of the GUI Window
        self.root.geometry("856x450")

        # set the title of the Window
        self.root.title("Troubleshoot App")

        self.popWin = None
        self.question_list = q_list
        self.q_no = 0
        self.has_another_question = True

        # assigns ques to the display_question function to update later.
        self.display_title()
        self.display_question()

        # opt_selected holds an integer value which is used for
        # selected option in a question.
        self.opt_selected = IntVar()

        # displaying radio button for the current question and used to
        # display options for the current question
        self.opts = self.radio_buttons()

        # display options for the current question
        self.display_options()

        # displays the button for next and exit.
        self.buttons()

        # display the additional text
        self.display_options()

        self.root.mainloop()

    # This method checks if there is another question for the chosen answer
    def has_next_question(self, u_input):
        current_question = self.question_list[self.q_no]
        # checks for if the selected option is correct
        if current_question.next_question[u_input]:
            # if the option is correct it return true
            return True

    # This method is used pull the next question if there is one,
    # by calling the has_next_question.
    # if the question is correct it will check if there is another question
    # and pull in the additional text, next question, and question number. 
    # If it is last question then it will destroy itself, otherwise 
    # it shows next question.
    def next_btn(self):
        current_question = self.question_list[self.q_no]

        # Check if the answer is correct
        if self.has_next_question(self.opt_selected.get() - 1):

            # shows the next question
            self.popup(current_question.additional_text[self.opt_selected.get() - 1])

            self.q_no = current_question.next_question_nbr[self.opt_selected.get() - 1]
            self.display_question()
            self.display_options()
        else:
            # destroys the GUI
            self.popup(current_question.additional_text[self.opt_selected.get() - 1])
            self.root.destroy()

    # This method shows the two buttons on the screen.
    # The first one is the next_button which moves to next question
    # It has properties like what text it shows the functionality,
    # size, color, and property of text displayed on button. Then it
    # mentions where to place the button on the screen. The second
    # button is the exit button which is used to close the GUI without
    # completing the quiz.
    def buttons(self):

        # The first button is the Next button to move to the
        # next Question
        next_button = Button(self.root, text="Next", command=self.next_btn,
                             width=10, bg="blue", fg="white", font=("ariel", 16, "bold"))

        # placing the button on the screen
        next_button.place(x=200, y=325)

        # This is the second button which is used to Quit the GUI
        quit_button = Button(self.root, text="Quit", command=self.root.destroy,
                             width=10, bg="black", fg="white", font=("ariel", 16, " bold"))

        # placing the Quit button on the screen
        quit_button.place(x=450, y=325)

        # class to define the components of the GUI

    def display_title(self):

        # The title to be shown
        title = Label(self.root, text="Troubleshooting Decision Tree",
                      width=50, bg="green", fg="white", font=("ariel", 20, "bold"))

        # place of the title
        title.place(x=0, y=2)

    # This method deselect the radio button on the screen
    # Then it is used to display the options available for the current
    # question which we obtain through the question number and Updates
    # each of the options for the current question of the radio button.
    def display_options(self):
        val = 0

        # deselecting the options
        self.opt_selected.set(0)

        current_question = self.question_list[self.q_no]

        # looping over the options to be displayed for the
        # text of the radio buttons.
        for option in current_question.answers:
            self.opts[val]['text'] = option
            val += 1

    # This method shows the current Question on the screen
    def display_question(self):
        current_question = self.question_list[self.q_no]

        # setting the Question properties
        q_no = Label(self.root, text=current_question.question, width=600,
                     font=('ariel', 16, 'bold'), anchor='w')

        # placing the option on the screen
        q_no.place(x=180, y=100)

    # This method is used to Display Title

    # This method shows the radio buttons to select the Question
    # on the screen at the specified position. It also returns a
    # list of radio button which are later used to add the options to
    # them.
    def radio_buttons(self):

        current_question = self.question_list[self.q_no]
        # initialize the list with an empty list of options
        q_list = []

        # position of the first option
        y_pos = 150

        # adding the options to the list
        while len(q_list) < len(current_question.answers):
            # setting the radio button properties

            radio_btn = Radiobutton(self.root, text=" ", variable=self.opt_selected,
                                    value=len(q_list) + 1, font=("ariel", 14))

            # adding the button to the list
            q_list.append(radio_btn)

            # placing the button
            radio_btn.place(x=180, y=y_pos)

            # incrementing the y-axis position by 40
            y_pos += 40

        # return the radio buttons
        return q_list

    # This method shows the top level GUI window showing the additional 
    # text needed for the next question
    def popup(self, add_t):
        self.popWin = TextWindow(self.root, add_t)
        self.root.wait_window(self.popWin.top)

# END OF THE PROGRAM
