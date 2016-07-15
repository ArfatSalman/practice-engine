from flask import render_template, session, redirect, url_for
from flask import request, jsonify, flash
from flask_login import current_user, login_required, login_user
from sqlalchemy.exc import SQLAlchemyError
from . import main
from .. import db
from ..models import (
                        User, 
                        Question, 
                        Tag,
                        FavouriteQuestionAssoc as FQ,
                        UpvoteQuestionAssoc as UQ,
                        DownvoteQuestionAssoc as DQ,
                        Solution,
                        UpvoteDownvoteSolutionAssoc as UDS,
                        UserSetting as US)
from .forms import UserTagsForm
from ..question.forms import SolutionForm
from ..question.views import associate_tags
from ..utilities import print_debug, bad_request, add_to_db, add_to_db_ajax
import random


@main.route('/', methods=['GET', 'POST'])
def index():
    login_user(User.query.get(2))
    if current_user.is_authenticated:
        print_debug('User is authenticated in /')
        return redirect(url_for('.home'))
    else:
        return render_template('index.html')


@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = UserTagsForm()

    sol_form = SolutionForm()

    tags = current_user.associated_tags.all()

    ques = current_user.get_relevant_question()

    side_ques = []
    if len(ques) > 0:
        if len(ques) > 5:
            ques = random.sample(set(ques), 5)
        ques, side_ques = ques[0], ques[1:]
    else:
        ques = ques[0]

    return render_template('home.html',
                           tags=tags, 
                            ques=ques,
                            side_ques=side_ques, 
                            form=form,
                            sol_form=sol_form)


@main.route('/add-user-tags', methods=['POST'])
@login_required
def add_user_tags():
    form = UserTagsForm()

    if form.validate_on_submit():
        tags = associate_tags(form)
        
        if not tags:
            return bad_request('At least one tag is required', 406)
        
        """This loop checks to see if any matching tags
        for this user exists or not. Since, SQLAlchemy will
        either generate unique contraint error or Add multiple 
        duplicate entries. Hence, it is checked manually."""
        for tag in tags:
            if tag not in current_user.associated_tags:
                current_user.associated_tags.append(tag)
        try:
            db.session.add(current_user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            msg = 'Tags could not be properly saved. Please try again.'
            return jsonify(bad_request(msg, 500))

        result = {}
        for tag in current_user.associated_tags:
            result[tag.tagname] = tag.id
        return jsonify(result)

    return bad_request('Form submission is not correct', 403)


@main.route('/remove-user-tags', methods=['POST'])
@login_required
def remove_user_tags():
    result = {}

    tag_id = request.form.get('id', 0, type=int)
    tag = Tag.query.get_or_404(tag_id)

    current_user.associated_tags.remove(tag)

    try:
        db.session.add(current_user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        msg = 'Tag cannot be removed.'
        return bad_request(msg, 500)
    
    result['message'] = 'Remove Successful'
    return jsonify(result)


@main.route('/upvote', methods=['POST'])
@login_required
def upvote():

    ques_id = request.form.get('question-id', 0, type=int)
    ques = Question.query.get_or_404(ques_id)

    if current_user.has_downvoted(ques):
        msg = "You can't upvote and downvote the same question"
        return bad_request(msg)

    if current_user.has_upvoted(ques):
        assoc = current_user.questions_upvoted.filter(UQ.question == ques).one()
        current_user.questions_upvoted.remove(assoc)
        msg = 'Upvote Removed'
    else:
        current_user.ques_upvoted.append(ques)
        msg = 'Upvoted'

    add_to_db_ajax(current_user, 'Upvote unsuccessful', 500)

    return jsonify(message=msg)


@main.route('/downvote', methods=['POST'])
@login_required
def downvote():
    ques_id = request.form.get('question-id', 0, type=int)
    ques = Question.query.get_or_404(ques_id)

    if current_user.has_upvoted(ques):
        msg = "You can't upvote and downvote the same question"
        return bad_request(msg)

    if current_user.has_downvoted(ques):
        assoc = current_user.questions_downvoted.filter(DQ.question == ques).one()

        current_user.questions_downvoted.remove(assoc)
        msg = 'Downvote Removed'
    else:
        current_user.ques_downvoted.append(ques)
        msg = 'Downvoted'

    add_to_db_ajax(current_user, 'Downvote unsuccessful', 500)

    return jsonify(message=msg)


@main.route('/vote-solution', methods=['POST'])
@login_required
def vote_solution():
    sol_id = request.form.get('id', 0, type=int)
    sol = Solution.query.get(sol_id)

    is_upvote = request.form.get('is_upvote', 1, type=int)

    if is_upvote:
        assoc = current_user.has_upvoted(sol)
        if assoc:
            current_user.solutions_voted.remove(assoc)
            err_msg = 'Error in removing the upvote from the solution.'
            msg = 'Solution upvote removed.'
        else:
            # create a new assoc
            current_user.sols_voted.append(sol)
            err_msg = 'Error in upvoting the solution.'
            msg='Solution Upvoted.'
    else:
        assoc = current_user.has_downvoted(sol)
        if assoc:
            current_user.solutions_voted.remove(assoc)
            err_msg = 'Error in removing the downvote from the solution.'
            msg ='Solution downvote removed.'
        else:
            assoc = UDS(sol)
            assoc.is_upvote = is_upvote
            current_user.solutions_voted.append(assoc)
            err_msg = 'Error in downvoting the solution.'
            msg ='Solution downvoted.'

    add_to_db_ajax(current_user, err_msg)
    return jsonify(message=msg)



@main.route('/favourite-question', methods=['POST'])
@login_required
def fav_ques():
    ques_id = request.form.get('question-id', 0, type=int)
    ques = Question.query.get_or_404(ques_id)

    if current_user.has_favourited(ques):
        # get the association
        assoc = current_user.questions_fav.filter(FQ.question == ques).one()
        current_user.questions_fav.remove(assoc)
        msg = 'Favourite Removed'
    else:
        # Using association Proxy
        current_user.ques_fav.append(ques)
        msg = 'Question Favourited'

    add_to_db_ajax(current_user, 'Favourite Operation unsuccessful', 500)

    return jsonify(message=msg)


@main.route('/user/<int:id>', methods=['GET'])
@login_required
def user(id):
    user = User.query.get_or_404(id)

    return render_template('user.html',
                            user = user,
                            per_page_limit=2)


@main.route('/user/<int:id>/<ques_type>')
@login_required
def user_questions(id, ques_type):
    user = User.query.get_or_404(id)

    if ques_type == 'posted':
        page = 2
        pagination = user.questions.paginate(page, per_page=2)
        return render_template("_posted.html",
                                pagination=pagination)

    return ""

@main.route('/tags/<tagname>')
@login_required
def tags(tagname):
    tag = Tag.query.filter_by(tagname=tagname).first()
    ques = None
    if tag:
        ques = tag.questions

    return render_template('tags.html',
                            ques=ques)

@main.route('/user-setting', methods=['POST'])
@login_required
def user_setting():
    name = request.form.get('name')
    setting = current_user.setting
    
    if not setting:
        setting = US()
        setting.user = current_user
    
    if name == 'HD':
        if setting.hide_difficulty:
            setting.hide_difficulty = False
        else:
            setting.hide_difficulty = True
    elif name == 'KSQ':
        if setting.repeat_solved_questions:
            setting.repeat_solved_questions = False
        else:
            setting.repeat_solved_questions = True
    elif name == 'AL':
        if setting.auto_load_questions:
            setting.auto_load_questions = False
        else:
            setting.auto_load_questions = True
    elif name == 'HS':
        if setting.hide_solutions:
            setting.hide_solutions = False
        else:
            setting.hide_solutions = True
    else:
        return bad_request('Setting Not Found')

    add_to_db_ajax(setting, 'Setting Unsuccessful')

    return jsonify(message='Setting successful')
