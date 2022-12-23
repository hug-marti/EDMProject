class EdmBrain:
    has_next_question: bool

    def __init__(self, q_list):
        self.has_another_question = True
        self.question_number = 0
        self.question_list = q_list

    def still_has_questions(self):
        while self.has_another_question:
            self.next_question()

    def next_question(self):
        current_question = self.question_list[self.question_number]

        print(f"{current_question.question}")
        for i in current_question.answers:
            print(f"{i}")
        user_answer = int(input("Select one: "))

        print(f"{current_question.additional_text[user_answer]}")
        self.has_another_question = current_question.next_question[user_answer]
        self.question_number = current_question.next_question_nbr[user_answer]

