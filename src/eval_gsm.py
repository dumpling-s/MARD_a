import json
# import openai
import numpy as np
import time
import re

def parse_bullets(sentence):
    bullets_preprocess = sentence.split("\n")
    bullets = []

    for bullet in bullets_preprocess:
        try:
            idx = bullet.find(next(filter(str.isalpha, bullet)))
        except:
            continue

        bullet = bullet[idx:]

        if len(bullet) != 0:
            bullets.append(bullet)

    return bullets


def parse_yes_no(string):
    if "yes" in string.lower():
        return True
    elif "no" in string.lower():
        return False
    else:
        return None


def solve_math_problems(input_str):
    pattern = r"\d+\.?\d*"

    matches = re.findall(pattern, input_str)
    if matches:
        return matches[-1]

    return None

def parse_answer(input_str):
    pattern = r"\{([0-9.,$]*)\}"
    matches = re.findall(pattern, input_str)

    solution = None

    for match_str in matches[::-1]:
        solution = re.sub(r"[^0-9.]", "", match_str)
        if solution:
            break

    return solution


def compute_accuracy(gt, pred_solutions):
    answers = solve_math_problems(gt)

    if answers is None:
        return None

    if type(pred_solutions) == list:
        pred_answers = []

        for pred_solution in pred_solutions:
            pred_answer = parse_answer(pred_solution)

            if pred_answer is None:
                pred_answer = solve_math_problems(pred_solution)

            pred_answers.append(pred_answer)
        pred_answer = most_frequent(pred_answers)
    else:
        pred_answer = parse_answer(pred_solutions)
        if pred_answer is None:
            pred_answer = solve_math_problems(pred_solutions)

    if pred_answer is None:
        return 1

    # try:
    if float(answers) == float(pred_answer):
        return 1
    else:
        return 0


def most_frequent(List):
    counter = 0
    num = List[0]

    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i

    return num

class Eval_Gsm:
    def __init__(self, filename):
        self.filename = filename
    def eval_gsm(self):
        response_dict = json.load(open(self.filename, "r"))

        questions = list(response_dict.keys())

        accuracies = []

        for question in questions:
            responses, gt = response_dict[question]

            pred_solutions = []
            for response in responses:
                pred_solution = response[-1]['content']

                pred_solutions.append(pred_solution)

            accurate = compute_accuracy(gt, pred_solutions)

            if accurate is not None:
                accuracies.append(float(accurate))
            else:
                import pdb
                pdb.set_trace()
                print(gt)

            print("accuracies:", np.mean(accuracies), np.std(accuracies) / (len(accuracies) ** 0.5))

