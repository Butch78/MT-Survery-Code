import json
import os
import sys
import uuid
import random
from collections import Counter
from datetime import datetime

from flask import Flask, render_template, request, make_response, redirect, \
    url_for

from parserModule import Parser

print(sys.executable)

# set the project root directory as the templates folder, you can set others.
app = Flask(__name__)

# All experiments are saved in the source folder 'resources/experiments'.
experiments_path = os.path.join("resources", "experiments")

# The list experiments contains all the files in the experiment directory
(_, _, experiments) = next(os.walk(experiments_path))

# Counters of how many experiments have started
# All start with 0 counts
# ITC = Short Checklist; NTC = Long Checklist; ETC = No Checklist
experiments_started = Counter()
experiments_started['ETC'] = 0
experiments_started['ITC'] = 0
experiments_started['NTC'] = 0
# experiments_started['NF'] = 0

# Counters of how many experiments have concluded
# All start with 0 counts
# ITC = Short Checklist; NTC = Long Checklist; ETC = No Checklist
experiments_concluded = Counter()
experiments_concluded['ETC'] = 0
experiments_concluded['ITC'] = 0
experiments_concluded['NTC'] = 0
# experiments_concluded['NF'] = 0

# Creation of log file based on id name
html_tags = ["<li", "<ul", "<a"]

p = Parser()


# Loading of the main page --> Entry Point
@app.route('/')
def index():
    """
    Start of the application. It returns the file "templates/index.html" and
    create the unique identifier "userid", if not already found.
    """
    resp = make_response(render_template('index.html', title="Intro"))
    user_id = request.cookies.get('experiment-userid', None)

    print("experiments_started: ", experiments_started)
    print("experiments_concluded: ", experiments_concluded)

    if user_id is None:
        user_id = uuid.uuid4()
        resp.set_cookie('experiment-userid', str(user_id))
        print(f'Userid was None, now is {user_id}')
    return resp


@app.route("/experiment_intro", methods=['GET', 'POST'])
def experiment_intro():
    print('neyz run exp intro')
    """
    Starts the intro of the experiment.
    It reads the files from "resources/experiments" and populates the page.
    """

    # Default is "user not found"
    user_id = request.cookies.get('experiment-userid', 'userNotFound')

    # data: is an annotation for the variable data (used just for information and to iETCrease code readability)
    # to note that it is of type dict. Has no effect on the runtime
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)
    log_data(str(user_id), "start fibo", "fibonacci")

    # Choosing experiment
    # choose_experiment() returns 3 variables
    cr_file, is_cr_primed, pe_type, group = choose_experiment()
    if request.cookies.get('time-constraint-type') == "ETC":
        group = "ETC"
    elif request.cookies.get('time-constraint-type') == "ITC":
        group = "ITC"
    elif request.cookies.get('time-constraint-type') == "NTC":
        group = "NTC"
    # elif request.cookies.get('time-constraint-type') == "NF":
    #     group = "NF"

    print(f'intro - Group was None, now is {group}')
    log_data(str(user_id), "timeConstraintType fibo", group)
    log_data(str(user_id), "setexperimentCRtype fibo", cr_file)
    # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))

    exp_is_done = request.cookies.get('experimentCR', 'not_done')

    if exp_is_done != 'experimentCR-done':
        experiment_snippets, experiment_body = read_experiment('files_fibonacci')
        codes = build_experiments(experiment_snippets)
        print("neyz body1: ", experiment_body)

        comment_line_number = 0
        comment = ''

        resp = make_response(render_template("experiment_intro.html",
                                             title='Code Review Experiment intro',
                                             codes=codes,
                                             # checklist=checklist,
                                             # is_primed=is_cr_primed,
                                             comment_line_number=comment_line_number,
                                             comment=comment,
                                             md_body=experiment_body,
                                             group=group))
        resp.set_cookie('experiment-init-questions', 'init-questions-done')
        resp.set_cookie('experiment-experimentCRtype', cr_file)
        resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
        # print(group)
        resp.set_cookie('time-constraint-type', str(group))
        resp.set_cookie('assignmentDone', 'done')
        # print("CHECK")
        # print(request.cookies.get('time-constraint-type'))

        return resp
    else:
        return redirect(url_for('already_done'))


@app.route("/experiment_intro2", methods=['GET', 'POST'])
def experiment_intro2():
    global is_cr_primed
    print('neyz run exp intro2')

    # Default is "user not found"
    user_id = request.cookies.get('experiment-userid', 'userNotFound')

    # data: is an annotation for the variable data (used just for information and to iETCrease code readability)
    # to note that it is of type dict. Has no effect on the runtime
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)
    log_data(str(user_id), "start Intro 2", "start Intro 2")

    # Choosing experiment
    # choose_experiment() returns 3 variables
    # cr_file, is_cr_primed, pe_type, group = choose_experiment()
    try:
        # Code that may raise an error
        if request.cookies.get('time-constraint-type') == "ETC":
            group = "ETC"
        elif request.cookies.get('time-constraint-type') == "ITC":
            group = "ITC"
        elif request.cookies.get('time-constraint-type') == "NTC":
            group = "NTC"
        else:
            raise Exception("None of the time-constraint-type conditions were met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"Time-constraint-type - An error occurred by run experiment: {e}")

    try:
        # Code that may raise an error
        if request.cookies.get('experiment-experimentCRtype') == "files_experiment":
            cr_file = "files_experiment"
        else:
            raise Exception("experiment-experimentCRtype condition is not met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"Experiment-experimentCRtype - An error occurred by run experiment: {e}")

    try:
        # Code that may raise an error
        if request.cookies.get('experiment-experimentCRisprimed') == "False":
            is_cr_primed = False
        else:
            raise Exception("experiment-experimentCRisprimed condition is not met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"experiment-experimentCRisprimed - An error occurred by run experiment: {e}")

    print(f'intro 2 - Group was None, now is {group}')
    log_data(str(user_id), "timeConstraintType intro 2", group)
    log_data(str(user_id), "setexperimentCRtype intro 2", cr_file)
    # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))

    exp_is_done = request.cookies.get('experimentCR', 'not_done')

    if exp_is_done != 'experimentCR-done':
        experiment_snippets, experiment_body = read_experiment(cr_file)
        codes = build_experiments(experiment_snippets)

        comment_line_number = 0
        comment = ''

        resp = make_response(render_template("experiment_intro2.html",
                                             title='Code Review Experiment intro 2',
                                             codes=codes,
                                             is_primed=is_cr_primed,
                                             comment_line_number=comment_line_number,
                                             comment=comment,
                                             md_body=experiment_body,
                                             group=group))
        resp.set_cookie('experiment-init-questions', 'init-questions-done')
        resp.set_cookie('experiment-experimentCRtype', cr_file)
        resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
        # print(group)
        resp.set_cookie('time-constraint-type', str(group))
        resp.set_cookie('assignmentDone', 'done')
        # print("CHECK")
        # print(request.cookies.get('time-constraint-type'))

        return resp
    else:
        return redirect(url_for('already_done'))


@app.route("/experiment", methods=['GET', 'POST'])
def run_experiment():
    global cr_file
    print('neyz run exp')
    """
    Starts the first phase of the experiment.
    It reads the files from "resources/experiments" and populates the page.
    """

    # Default is "user not found"
    user_id = request.cookies.get('experiment-userid', 'userNotFound')

    # data: is an annotation for the variable data (used just for information and to iETCrease code readability)
    # to note that it is of type dict. Has no effect on the runtime
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)
    log_data(str(user_id), "start - experiment", "files_experiment")

    # Choosing experiment
    # choose_experiment() returns 3 variables
    # cr_file, is_cr_primed, pe_type, group = choose_experiment()
    try:
        # Code that may raise an error
        if request.cookies.get('time-constraint-type') == "ETC":
            group = "ETC"
        elif request.cookies.get('time-constraint-type') == "ITC":
            group = "ITC"
        elif request.cookies.get('time-constraint-type') == "NTC":
            group = "NTC"
        else:
            raise Exception("None of the time-constraint-type conditions were met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"Time-constraint-type - An error occurred by run experiment: {e}")

    try:
        # Code that may raise an error
        if request.cookies.get('experiment-experimentCRtype') == "files_experiment":
            cr_file = "files_experiment"
        else:
            raise Exception("experiment-experimentCRtype condition is not met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"Experiment-experimentCRtype - An error occurred by run experiment: {e}")

    print("neyz prime", request.cookies.get('experiment-experimentCRisprimed'))
    try:
        # Code that may raise an error
        if request.cookies.get('experiment-experimentCRisprimed') == "False":
            is_cr_primed = False
        else:
            raise Exception("experiment-experimentCRisprimed condition is not met")
    except Exception as e:
        # Handle the error and print the error message
        print(f"experiment-experimentCRisprimed - An error occurred by run experiment: {e}")

    print(f'Exp - Group was None, now is {group}')
    log_data(str(user_id), "timeConstraintType experiment", group)
    log_data(str(user_id), "setexperimentCRtype experiment", cr_file)
    # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))

    exp_is_done = request.cookies.get('experimentCR', 'not_done')

    if exp_is_done != 'experimentCR-done':
        experiment_snippets, experiment_body = read_experiment(cr_file)
        codes = build_experiments(experiment_snippets)

        print("neyz body2: ", experiment_body)
        comment_line_number = 0
        comment = ''

        resp = make_response(render_template("experiment.html",
                                             title='Code Review Experiment',
                                             codes=codes,
                                             # checklist=checklist,
                                             is_primed=is_cr_primed,
                                             comment_line_number=comment_line_number,
                                             comment=comment,
                                             md_body=experiment_body,
                                             group=group))
        resp.set_cookie('experiment-init-questions', 'init-questions-done')
        resp.set_cookie('experiment-experimentCRtype', cr_file)
        resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
        # print(group)
        resp.set_cookie('time-constraint-type', str(group))
        resp.set_cookie('assignmentDone', 'done')
        # print("CHECK")
        # print(request.cookies.get('time-constraint-type'))

        return resp
    else:
        return redirect(url_for('already_done'))


def choose_experiment():
    # checklist_type = []
    group = ""
    """
    Assign an experiment to a new user. We choose the type of experiment
    that has the least amount of concluded experiments.
    If we have more than one such case, we choose the one that has the
    least amount of started experiments.
    """

    # if request.cookies.get('assignmentDone') == "done":
    #     if request.cookies.get('time-constraint-type') == "ETC":
    #         # checklist_type = 0
    #         group = "ETC"
    #
    #     # assign to Long Checklist
    #     elif request.cookies.get('time-constraint-type') == "NTC":
    #         # checklist_type = import_checklist("resources/checklistLong.txt")
    #         group = "NTC"
    #
    #     # assign to No Checklist
    #     elif request.cookies.get('time-constraint-type') == "ITC":
    #         # checklist_type = import_checklist("resources/checklistShort.txt")
    #         group = "ITC"
    #
    # else:
    #     # most_common returns a dict with index 0 = Dict Key with most entries (So its a dict sorted from largest to
    #     # smallest.
    #     # we take the last element of this dict [-1], which is the element with the least counts
    #     # From this element, we take entry 1 (because entry 0 is the identifier and entry 1 the count number)
    #     # So min_val now is an int that represents the smallest number in the dict
    min_val = experiments_concluded.most_common()[-1][1]

    mins = []

    for k in experiments_concluded:
        if experiments_concluded[k] == min_val:
            mins.append(k)

    if len(mins) > 1:
        # more than 1 type has the same amount of concluded
        # experiments. Hence, we choose the one that has the least amount of
        # started ones
        min = sys.maxsize
        to_assing = ''
        for k in mins:
            if experiments_started[k] < min:
                min = experiments_started[k]
                to_assing = k
    else:
        to_assing = mins[0]


    # groupToken = random.randint(0, 2)
    # if groupToken == 0:
    #     to_assing = 'ETC'
    # elif groupToken == 1:
    #     to_assing = 'ITC'
    # elif groupToken == 2:
    #     to_assing = 'NTC'


    # Todo The experiment is assigned randomly
    # groupToken = random.randint(0, 4)
    # print(groupToken)
    # #if groupToken <= 1:
    # to_assing = 'NF'
    # #else:
    # #to_assing = 'NTC'
    # # elif groupToken == 2:
    #    # to_assing = 'ITC'

    experiments_started[to_assing] += 1
    group = to_assing
    # group = "ITC"

    primed = False
    cr = 'files_experiment'

    print("exp started line 396: ", experiments_started)
    print("exp concluded line 397: ", experiments_concluded)

    return cr, primed, "test", group


# Loading of General Survey.
@app.route("/survey", methods=['GET', 'POST'])
def start():
    """
    Loading of Survey. These questions can be found and
    changed in "templates/survey.html"
    """
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    first_time = request.cookies.get('experiment-survey', 'not-done')

    if first_time == 'not-done':
        log_data(str(user_id), "start - survey", "survey")
        resp = make_response(render_template('survey.html',
                                             title="Survey"))
        # Todo commented out
        #  resp.set_cookie('experimentCR', 'experimentCR-done')
        resp.set_cookie('experiment2nd', 'experiment2nd-done')

        return resp
    else:
        return redirect(url_for('already_done'))


# Loading of Personal Information Survey.
@app.route("/dem_questions", methods=['GET', 'POST'])
def load_questions():
    """
    Loading of Demographic Questions. These questions can be found and
    changed in "templates/dem_questions.html"
    """
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)
    first_time = request.cookies.get('experiment-dem-questions', 'experiment-dem-not_done')

    if first_time == 'experiment-dem-not_done':
        log_data(str(user_id), "start - dem", "dem_questions")
        resp = make_response(render_template('dem_questions.html',
                                             title="Demographics Questions"))
        resp.set_cookie('experiment-final', 'experiment-final-done')
        resp.set_cookie('experiment-survey', 'experiment-survey-done')
        return resp
    else:
        return redirect(url_for('already_done'))


# @app.route("/experiment_final_skip", methods=['GET', 'POST'])
# def run_experiment_final_skip():
#     user_id = request.cookies.get('experiment-userid', 'userNotFound')
#     # log_data(str(user_id), "experiment2nd-skipped", True)
#     user_id = request.cookies.get('experiment-userid', 'userNotFound')
#
#     if request.method == 'POST':
#         data: dict = request.form.to_dict()
#         log_received_data(user_id, data)
#     log_data(str(user_id), "start", "cr-experiment-final")
#
#     # Retrieving treatment information
#     cr_file = request.cookies.get('experiment-experimentCRtype')
#     is_cr_primed = request.cookies.get('experiment-experimentCRisprimed')
#     pe_type = "test"
#     log_data(str(user_id), "setexperimentCRtype", cr_file)
#     # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))
#
#     exp_is_done = request.cookies.get('experiment-final', 'experiment-final-not_done')
#
#     if exp_is_done != 'experiment-final-done':
#         experiment_snippets, experiment_body = read_experiment(cr_file)
#         codes = build_experiments(experiment_snippets)
#
#         comment_line_number = 0
#         comment = ''
#
#         # if it's in the test group, put the comment
#         # if cr_file == "files_experiment1" and is_cr_primed:
#         #    comment_line_number = 15
#         #    comment = "You should check if 'total' is null, otherwise the " \
#         #              "first line gives a null pointer exception"
#         # elif cr_file == "files_experiment" and is_cr_primed:
#         #    comment_line_number = 22
#         #    comment = "There is a corner case in which it doesn't work. " \
#         #              "The check should be >=, otherwise it fails in " \
#         #              "assigning the carry (e.g. 29 + 1)."
#
#         resp = make_response(render_template("experiment_final.html",
#                                              title='Code Review - Vulnerabilities',
#                                              codes=codes,
#                                              is_primed=is_cr_primed,
#                                              comment_line_number=comment_line_number,
#                                              treatment=cr_file,
#                                              comment=comment,
#                                              md_body=experiment_body))
#         # Todo removed the next line
#         # resp.set_cookie('experiment2nd', 'experiment2nd-done')
#         resp.set_cookie('experiment-experimentCRtype', cr_file)
#         resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
#         return resp
#
#     else:
#         return redirect(url_for('already_done'))


@app.route("/experiment_final_review", methods=['GET', 'POST'])
def run_experiment_final_review():
    print("This user is assigned to the Group: " + request.cookies.get("time-constraint-type", "na"))
    # checklist = request.cookies.get("time-constraint-type", "na")
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    # log_data(str(user_id), "experiment2nd-skipped", False)
    user_id = request.cookies.get('experiment-userid', 'userNotFound')

    if request.method == 'POST':
        data: dict = request.form.to_dict()
        print("DATA INCOMING: ")
        print(data)
        log_received_data(user_id, data)
    log_data(str(user_id), "start - experiment-final", "experiment-final")

    # Retrieving treatment information
    cr_file = request.cookies.get('experiment-experimentCRtype')
    is_cr_primed = request.cookies.get('experiment-experimentCRisprimed')
    pe_type = "test"
    log_data(str(user_id), "setexperimentCRtype - experiment-final", cr_file)
    # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))

    exp_is_done = request.cookies.get('experiment-final', 'experiment-final-not_done')

    if exp_is_done != 'experiment-final-done':
        experiment_snippets, experiment_body = read_experiment(cr_file)
        codes = build_experiments(experiment_snippets)

        comment_line_number = 0
        comment = ''

        # if it's in the test group, put the comment
        # if cr_file == "files_experiment1" and is_cr_primed:
        #    comment_line_number = 15
        #    comment = "You should check if 'total' is null, otherwise the " \
        #              "first line gives a null pointer exception"
        # elif cr_file == "files_experiment" and is_cr_primed:
        #    comment_line_number = 22
        #    comment = "There is a corner case in which it doesn't work. " \
        #              "The check should be >=, otherwise it fails in " \
        #              "assigning the carry (e.g. 29 + 1)."

        resp = make_response(render_template("experiment_final.html",
                                             title='Code Review - Time Constraint',
                                             codes=codes,
                                             is_primed=is_cr_primed,
                                             treatment=cr_file,
                                             comment_line_number=comment_line_number,
                                             comment=comment,
                                             # checklist=checklist,
                                             md_body=experiment_body))
        resp.set_cookie('experiment-experimentCRtype', cr_file)
        resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
        resp.set_cookie('experimentCR', 'experimentCR-done')
        return resp

    else:
        return redirect(url_for('already_done'))


# def run_experiment_final():
#     """
#     Loading of the final phase of the experiment showing the vulnerabilities.
#     It reads the files from "resources/experiments" and populates the page.
#     """
#
#     user_id = request.cookies.get('experiment-userid', 'userNotFound')
#
#     if request.method == 'POST':
#         data: dict = request.form.to_dict()
#         log_received_data(user_id, data)
#     log_data(str(user_id), "start", "cr-experiment-final")
#
#     # Choosing experiment
#     cr_file = request.cookies.get('experiment-experimentCRtype')
#     is_cr_primed = request.cookies.get('experiment-experimentCRisprimed')
#     pe_type = "test"
#     log_data(str(user_id), "setexperimentCRtype", cr_file)
#     # log_data(str(user_id), "setexperimentCRisprimed", str(is_cr_primed))
#
#     exp_is_done = request.cookies.get('experiment-final', 'experiment-final-not_done')
#
#
#     if exp_is_done != 'experiment-final-done':
#         experiment_snippets, experiment_body = read_experiment(cr_file)
#         codes = build_experiments(experiment_snippets)
#
#         comment_line_number = 0
#         comment = ''
#
#         # if it's in the test group, put the comment
#         # if cr_file == "files_experimentSB" and is_cr_primed:
#         #    comment_line_number = 15
#         #    comment = "You should check if 'total' is null, otherwise the " \
#         #              "first line gives a null pointer exception"
#         # elif cr_file == "files_experiment" and is_cr_primed:
#         #    comment_line_number = 22
#         #    comment = "There is a corner case in which it doesn't work. " \
#         #              "The check should be >=, otherwise it fails in " \
#         #              "assigning the carry (e.g. 29 + 1)."
#
#         resp = make_response(render_template("experiment_final.html",
#                                              title='Code Review - Vulnerabilities',
#                                              codes=codes,
#                                              is_primed=is_cr_primed,
#                                              treatment=cr_file,
#                                              comment_line_number=comment_line_number,
#                                              comment=comment,
#                                              md_body=experiment_body))
#         # todo removed the next line
#         # resp.set_cookie('experiment2nd', 'experiment2nd-done')
#         resp.set_cookie('experiment-experimentCRtype', cr_file)
#         resp.set_cookie('experiment-experimentCRisprimed', str(is_cr_primed))
#         return resp
#
#     else:
#         return redirect(url_for('already_done'))


# @app.route("/experiment_concluded", methods=['GET', 'POST'])
# def experiment_concluded():
#     """
#     After the experiment, we report to the participants all the bugs that
#     were present in the code, and ask their opinion on why they missed/caught
#     them.
#     """
#     user_id = request.cookies.get('experiment-userid', 'userNotFound')
#     exp_type = request.cookies.get('experiment-experimentCRtype')
#     exp_is_done = request.cookies.get('experiment-experimentCR', 'not_done')
#     exp_is_primed = request.cookies.get('experiment-experimentCRisprimed')
#     if request.method == 'POST':
#         data: dict = request.form.to_dict()
#         log_received_data(user_id, data)
#
#     log_data(str(user_id), "end", "cr_experiment")
#
#     if exp_is_done != 'DONE':
#         experiment_snippets, _ = read_experiment(exp_type)
#         code = experiment_snippets['0']['R']
#         if exp_type == 'files_experimentSB':
#             bugs = [{
#                 'comment': 'The check should be "small < total", otherwise it '
#                            'can return -1 in cases in which there are enough '
#                            'small boxes. For example, total = 20, big = 3, '
#                            'small = 5.',
#                 'line_number': 26,
#                 'bug_number': 'Bug B'
#             }, {
#                 'comment': 'small and big could be null too',
#                 'line_number': 18,
#                 'bug_number': 'Bug A'
#             }]
#             if exp_is_primed == 'False':
#                 bugs[0]['bug_number'] = 'Bug C'
#                 bugs[1]['bug_number'] = 'Bug B'
#                 bugs.append({
#                     'comment': 'total could be null. If this happen, '
#                                'the first line would give a '
#                                'NullPointerException.',
#                     'line_number': 14,
#                     'bug_number': 'Bug A'
#                 })
#         else:
#             bugs = [{
#                 'comment': 'If one of the 2 numbers is bigger than the other, '
#                            'the corresponding value will be null, raising a '
#                            'NPE.',
#                 'line_number': 17,
#                 'bug_number': 'Bug A'
#             }, {
#                 'comment': 'This check should be > (without the =). '
#                            'Otherwise when there is no carry the program '
#                            'will append a 0.',
#                 'line_number': 29,
#                 'bug_number': 'Bug B'
#             }]
#             if exp_is_primed == 'False':
#                 bugs[1]['bug_number'] = 'Bug C'
#                 bugs.append({
#                     'comment': 'The check should be >=, otherwise it fails '
#                                'in assigning the carry (e.g. 29 + 1).',
#                     'line_number': 22,
#                     'bug_number': 'Bug B'
#                 })
#         resp = make_response(
#             render_template("experiment_concluded.html",
#                             title="Experiment concluded",
#                             code=code,
#                             bugs=bugs,
#                             is_primed=exp_is_primed))
#
#         # Todo Set Cookie for Survey Lockout here
#         # resp.set_cookie('experiment-survey', 'experiment-survey-done')
#         return resp
#     else:
#         return redirect(url_for('already_done'))


@app.route("/feedback", methods=['GET', 'POST'])
def feedback():
    """
    As for the demographics, we ask the participants for feedback.
    Return the page "templates/feedback.html"
    """
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    resp = make_response(render_template("feedback.html", title='Feedback'))
    resp.set_cookie('experiment-dem-questions', 'experiment-dem-questions-done')
    return resp


@app.route('/data_policy', methods=['GET', 'POST'])
def data_policy():
    resp = make_response(render_template("data_policy.html", title='Data Policy'))
    resp.set_cookie('data_policy', 'open')
    return resp


@app.route("/conclusion", methods=['GET', 'POST'])
def conclusion():
    """
    Finally, thank the participant.
    Return "templates/conclusion.html"
    """
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    if request.method == 'POST':
        data: dict = request.form.to_dict()
        log_received_data(user_id, data)

    log_data(str(user_id), "end", "experiment_concluded")

    time_constraint_type = request.cookies.get('time-constraint-type')
    exp_type = request.cookies.get('experiment-experimentCRtype')
    exp_is_primed = request.cookies.get('experiment-experimentCRisprimed')

    print("time-constraint-type - line 740: ", time_constraint_type)
    print("exp-type - line 740: ", exp_type)
    print("exp_is_primed - line 741: ", exp_is_primed)

    if time_constraint_type == 'ETC':
        experiments_concluded['ETC'] += 1
    elif time_constraint_type == 'ITC':
        experiments_concluded['ITC'] += 1
    elif time_constraint_type == 'NTC':
        experiments_concluded['NTC'] += 1

    print("exp started line 759: ", experiments_started)
    print("exp concluded line 760: ", experiments_concluded)

    conclusion_text = read_files("conclusion.txt")
    return render_template("conclusion.html", title='conclusion',
                           conclusion=conclusion_text)


def build_experiments(experiment_snippets):
    # codes is used in experiment.html to loop over
    codes = []
    for num_experiment in experiment_snippets:
        experiment_snippet = experiment_snippets[num_experiment]
        codes.append({
            "id": num_experiment,
            "filename": experiment_snippet['filename'],
            "linecount": max(experiment_snippet['num_lines_L'],
                             experiment_snippet['num_lines_R']),
            "contextLineCount": 1,
            "left_line_number": 1,
            "left_content": experiment_snippet['L'],
            "right_line_number": 1,
            "right_content": experiment_snippet['R'],
            "prefix_line_count": 1,
            "prefix_escaped": 1,
            "suffix_escaped": 1,
        })
    return codes


@app.route("/already_done", methods=['GET', 'POST'])
def already_done():
    user_id = request.cookies.get('experiment-userid', 'userNotFound')
    log_data(str(user_id), "already_done", "already_done")
    conclusion_text = "Sorry but it seems you already tried to answer the " \
                      "survey. <br>This means that (1) you " \
                      "failed the first time, or (2) you already did the " \
                      "experiment. In both cases, you can't take the " \
                      "experiment a second time, sorry!"
    return render_template("conclusion.html", title='Already done',
                           conclusion=conclusion_text)


def log_received_data(user_id, data):
    print(data)
    for key in data.keys():
        if key == 'hidden_log':
            d = json.loads(data[key])
            for log in d['data']:
                splitted = log.strip().split(";")
                dt = splitted[0]
                action = splitted[1]
                info = ';'.join(splitted[2:])
                log_data(user_id, action, info, dt)
        else:
            log_data(user_id, key, data[key])


def read_files(filename):
    with open(os.path.join("resources", filename)) as f:
        return p.parse_md(f, has_code=False)


# FuETCtion creates or opens a file f and writes user data into it
# with open 'a' means open for writing and create if not existing
# datetime.timestamp creates the current time stamp which can be converted into time using
# datetime.fromtimestamp(timeStamp)
def log_data(user_id: str, key: str, data: str, dt: datetime = None):
    data = data.replace("\r\n", " ")

    with open(f'{user_id}.log', 'a') as f:
        log_dt = dt if dt is not None else datetime.timestamp(datetime.now())
        f.write(f'{log_dt};'
                f'{key};'
                f'{data}\n')


# This function read the experiment content from experiments/ folder. Each
# file follow the same composition rule of the experiments.
def read_experiment(file_name):
    with open(os.path.join(experiments_path, file_name)) as file_content:
        snippets = p.parse_md(file_content, has_code=True)

    questions_experiment = file_name.replace('files', 'questions')
    body = ''
    if os.path.exists(os.path.join(experiments_path, questions_experiment)):
        with open(os.path.join(experiments_path, questions_experiment)) as \
                file_content:
            body = p.parse_md(file_content, has_code=False)
    return snippets, body

# def contains_html_tags(string_to_check):
#     return any(tag in string_to_check for tag in html_tags)


# def import_checklist(path):
#     uid = 1
#     checklistArray = []
#     data_path = path
#     with open(data_path,'r') as file:
#         for line in file.readlines():
#             temp = {
#                 "type": line[0],
#                 "id": uid,
#                 "text": line[2:-1],
#                 "checked": False
#             }
#             checklistArray.append(temp)
#             uid += 1
#
#     #print(checklistArray)
#     return checklistArray
