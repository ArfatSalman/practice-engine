from datetime import datetime, timedelta

from flask import render_template, flash, url_for
from flask import request, redirect, jsonify, current_app
from flask_login import current_user, login_required

from sqlalchemy.exc import SQLAlchemyError
from . import question
from .. import db
from ..models import (User,
                      Question, 
                      Option, 
                      Tag, 
                      SolvedQuestionsAssoc as SQ,
                      Solution,
                      ReportQuestionAssoc as RQ)
from .forms import (
                    PostQuestionForm, 
                    UserTagsForm, 
                    EditQuestionForm,
                    SolutionForm)
from ..utilities import add_to_db, bad_request, add_to_db_ajax, print_debug, dual_response


'''Helper Functions'''
def get_options(form):
    options = []
    is_all_false = True

    for fieldname, value in form.data.items():
        if fieldname.startswith('option'):
            if value:
                is_right = form.data.get('check_'+fieldname)
                option = Option(body=value)
                option.is_right = is_right
                
                if is_right:
                    is_all_false = False
                
                options.append(option)

    return None if is_all_false else options

def associate_tags(form):
    tags = []
    for tagname in form.tags.data:
        tag = Tag.query.filter_by(tagname=tagname).first()
        if not tag:
            tag = Tag(tagname=tagname)
        tags.append(tag)
        
    return None if tags == [] else tags


@question.route('/post-question', methods=['GET','POST'])
@login_required
def post_question():
    form = PostQuestionForm(request.form)

    if form.validate_on_submit():

        options = get_options(form)
        
        # options will be None if at least one option is not chosen
        if not options:
            flash('At least one option should be chosen as correct.', 'info')
            return redirect(url_for('.post_question'))

        tags = associate_tags(form)
        if len(tags) > 5:
            return dual_response('More than 5 tags are not allowed.')
        
        if not tags:
            flash('At least one tag is required.')
            return redirect(url_for('.post_question'))

        ques = Question(body=form.body.data,
                            description=form.description.data,
                            user=current_user,
                            options=options,
                            tags=associate_tags(form))
        try:
            db.session.add(ques)
            db.session.commit()
            flash('Question has been posted successfully.','success')
            return redirect(url_for('.questions', id=ques.id))
        except SQLAlchemyError:
            db.session.rollback()
            flash('There was a problem posting the question.', 'danger')
            return redirect(url_for('.post_question'))

    return render_template('question/post-question.html', form=form)


@question.route('/edit-question/<int:id>', methods=['GET','POST'])
@login_required
def edit_question(id):
    ques = Question.query.get_or_404(id)

    if current_user != ques.user:
        flash('You are not authorized to edit this question.', 'info')
        return redirect(url_for('.question', id=ques.id))

    form = EditQuestionForm()
    
    option_name = [
                    'option1',
                    'option2',
                    'option3',
                    'option4'
                    ]

    if form.validate_on_submit():
        
        ques.body = form.body.data
        ques.description = form.body.description
        ques.tags = associate_tags(form)

        is_all_false = True
        options = []
        for name in option_name:
            value = form.data.get(name)
            opt_id = form.data.get(name+'_id')
            is_right = form.data.get('check_'+name)
            option = Option.query.get(opt_id)

            if value:
                # Check to see whther there is atleast one right option
                if is_right:
                    is_all_false = False

                # If option is None, means a new option is being added
                if not option:
                    ques.options.append(Option(body=value,
                                               is_right=is_right)
                                            ) 
                    continue

                # A new value has been obtained. Edit the option.   
                # if the option is part of said question.
                if option in ques.options:
                    option.body = value
                    option.is_right = is_right
                else:
                    flash('Option being edited is not part of the question.','info')
                    return redirect(url_for('main.home'))

                options.append(option)

        if is_all_false:
            # if all the options are false, don't commit.
            flash('At least one option should be chosen as correct','info')
            return redirect(url_for('.edit_question', id=ques.id))
        else:
            db.session.add_all(options)

        try:
            db.session.add(ques)
            db.session.commit()
            flash('Question updated successfully.', 'success')
            return redirect(url_for('.questions', id=ques.id))
        except SQLAlchemyError, e:
            db.session.rollback()
            flash('There was a problem updating the question.', 'danger')
            return redirect(url_for('.edit_question', id=ques.id))
    
    # Fill the form if the form is just displayed
    form.body.data = ques.body
    form.description.data = ques.description

    options = ques.options
    if options:
        try:
            if options[0]:
                form.option1_id.data = options[0].id
                form.option1.data = options[0].body
                form.check_option1.data = options[0].is_right
            if options[1]:
                form.option2_id.data = options[1].id
                form.option2.data, form.check_option2.data = options[1].body, options[1].is_right
            if options[2]:
                form.option3_id.data = options[2].id
                form.option3.data, form.check_option3.data = options[2].body, options[2].is_right
            if options[3]:
                form.option4_id.data = options[3].id
                form.option4.data, form.check_option4.data = options[3].body, options[3].is_right
        except IndexError:
            pass
    
    """Build tag list for the form."""
    tags = []
    for tag in ques.tags:
        tags.append(tag.tagname)

    form.tags.data = tags

    return render_template('question/edit-question.html', form=form)


@question.route('/question/<int:id>')
@login_required
def questions(id):
    ques = Question.query.get(id)
    sol_form = SolutionForm()

    return render_template('question/question.html', 
                            ques=ques,
                            sol_form=sol_form)


@question.route('/get-tags', methods=['GET'])
@login_required
def get_tags():
    query = request.args.get('query')
    tags = Tag.query.filter(Tag.tagname.like('%{}%'.format(query)))
    
    result = {}
    for i, tag in enumerate(tags):
        result[i]=tag.tagname
    return jsonify(result)


@question.route('/check-answer', methods=['POST'])
@login_required
def check_answer():
    ques_id = request.form.get('question-id', 0, type=int)
    option_selected = request.form.getlist('opt')
    
    if not option_selected:
        return bad_request('Choose atleast one Option', 406)

    ques = Question.query.get_or_404(ques_id)

    result = {}
    is_solved = False
    for option_id in option_selected:
        option = Option.query.get_or_404(int(option_id))
        if option.is_right:
            result[str(option.id)]=True
            is_solved = True
        else:
            result[str(option.id)]=False
            is_solved = False
            break

    sq = SQ.query.filter_by(question=ques, user=current_user)\
                 .one_or_none()
    if not sq:
        sq = SQ(question=ques) # So that it complies with proxy
        sq.user = current_user
    sq.attempted += 1

    if is_solved:
        sq.solved = is_solved
        sq.is_set_unsolved = False
        current_user.update_streak()
    
    add_to_db_ajax(sq, 'Check-Answer: Operation Error while writing to DB')

    return jsonify(result)

@question.route('/get-questions')
@login_required
def get_questions():
    # This solution form is needed since _questions.html contains the form.
    sol_form = SolutionForm()

    result = {}
    ques_id = request.args.get('question_id', 0, type=int)

    # if a particular question is given, then return only that
    # question. 

    if ques_id:
        ques = Question.query.get(ques_id)
        if ques:
            result[str(ques.id)] = render_template('question/_question.html',
                                                    ques=ques,
                                                    sol_form=sol_form)
        else:
            return bad_request('The given question does not exist.')
    else:
        if current_user.get_relevant_question():
            for ques in current_user.get_relevant_question():
                result[str(ques.id)] = render_template('question/_question.html',
                                                    ques=ques,
                                                    sol_form=sol_form)
        else:
            return bad_request('No more questions. Add More topics.')
    
    return jsonify(result)


@question.route('/post-solution', methods=['POST'])
@login_required
def post_solution():
    form = SolutionForm()

    if form.validate_on_submit():
        ques_id = request.form.get('question-id', 0, type=int)
        body = request.form.get('body')

        if ques_id:
            ques = Question.query.get(ques_id)
            sol = ques.solution_by_user(current_user)

            # if Solution exists, edit it.
            if sol:
                sol.body = body
                add_to_db_ajax(sol, 'An error occured while editing the solution')
                
                return jsonify(message='Solution edited successfully')
            # else create it.   
            solution = Solution(body=body,
                                user=current_user,
                                question=ques
                            )
            add_to_db_ajax(solution, "An error occured while posting solution.")
            return jsonify(message='Solution posted successfully.')
        else:
            return bad_request('Question does not exist. Solution cannot be posted.')
    return bad_request('Form validation unsuccesful. Solution not posted.')


@question.route('/question/<int:id>/<type_data>')
@login_required
def question_solutions(id, type_data):
    ques = Question.query.get_or_404(id)
    page = request.args.get('page', 2, type=int)
    pagination = None
    
    if type_data == 'view-solutions':
        pagination = ques.solutions.paginate(page,
                                            per_page=current_app.config['PER_PAGE_LIMIT'])
        return jsonify(content=render_template('_solutions.html',
                                                pagination=pagination))
    elif type_data == 'solution':
        a = ques.solution_by_user(current_user)
        
        if not a:
            return dual_response('The user or question does not exist.', 'danger')
        
        return jsonify(id=a.id,solution=a.body)


    return dual_response('Unkown request format.', 'danger')



@question.route('/delete-question/<int:id>')
@login_required
def delete_question(id):
    ques = Question.query.get_or_404(id)

    if ques.user == current_user:
        db.session.delete(ques)
        db.session.commit()
    else:
        return bad_request('You are not authorized to delete this question', 
                            redir=url_for('.questions', id=ques.id))
    flash('The question with ID %s has been successfully deleted.' % ques.id, 'success')
    return redirect(url_for('main.home'))



@question.route('/unsolve', methods=['POST'])
@login_required
def unsolve_question():
    id = request.form.get('question-id', 0, type=int)
    ques = Question.query.get_or_404(id)
    ques_assoc = SQ.query.filter_by(question=ques, user=current_user).one_or_none()

    ques_link = '<a href="%s"class="alert-link">Question %d</a>' % (url_for('.questions', id=ques.id), ques.id)

    if not ques_assoc:
        return bad_request('You have not yet solved or attempted %s.' % ques_link)

    if not ques_assoc.solved:
        return bad_request('You have not yet solved %s' % ques_link)

    ques_assoc.is_set_unsolved = True
    ques_assoc.solved = False
    add_to_db(ques_assoc,'%s cannot be unsolved. Please try again.' % ques_link)

    return dual_response('You have successfully unsolved %s' % ques_link)


@question.route('/report-question', methods=['POST'])
@login_required
def report_questions():
    ques_id = request.form.get('question-id', 0, type=int)
    msg = request.form.get('message', '')

    ques = Question.query.get_or_404(ques_id)
    ques_assoc = RQ.query\
                   .filter_by(question=ques, user=current_user)\
                   .first()
    ques_link = '<a href="%s"class="alert-link">Question %d</a>' % (url_for('.questions', id=ques.id), ques.id)

    if ques_assoc:
        db.session.delete(ques_assoc)
        db.session.commit()
        message = '%s was unreported successfully.' % ques_link
        return jsonify(message=message) 

    rq = RQ(question=ques)

    if msg:
        rq.message = msg

    current_user.questions_reported.append(rq)

    add_to_db(current_user, '%s reporting failed. Please try again.' % ques_link)    
    
    message = '%s reported successfully.' % ques_link
    return dual_response(message)
