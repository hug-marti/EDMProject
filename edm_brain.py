class EdmBrain:
    has_next_question: bool

    def __init__(self,q_list, f_dict):
        self.current_question = None
        self.question_number = 0
        self.has_next_question = True
        self.question_list = q_list
        self.function_list = f_dict
        self.current_function = None

    def still_has_questions(self):
        return self.has_next_question

    def next_question(self, q_nbr, has_next_q, funct):
        self.question_number = q_nbr
        self.has_next_question = has_next_q
        self.current_question = self.function_list[funct]

