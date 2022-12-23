from question_model import Question
from data import question_dict
from ui import Quiz

# get the data from the question_data file
question_bank = []
for question in question_dict:
    q_nbr = question['question_nbr']
    q_text = question['question']
    q_answer = question['answers']
    q_next = question['next_question']
    q_next_nbr = question['next_question_nbr']
    a_text = question['additional_text']
    new_question = Question(q_nbr, q_text, q_answer,
                            q_next, q_next_nbr, a_text)
    question_bank.append(new_question)

# create an object of the Quiz Class.
quiz = Quiz(question_bank)
