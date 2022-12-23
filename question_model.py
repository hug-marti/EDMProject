class Question:

    def __init__(self, q_nbr, q_question, ans, nex_quest, nex_quest_nbr, a_text):
        self.question_nbr = q_nbr
        self.question = q_question
        self.answers = ans
        self.next_question = nex_quest
        self.next_question_nbr = nex_quest_nbr
        self.additional_text = a_text
