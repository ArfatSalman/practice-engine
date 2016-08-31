import random, datetime

from flask import render_template, session, redirect, url_for
from flask import request, jsonify, flash, current_app, abort
from flask_login import current_user, login_required, login_user
from flask_mail import Message
from sqlalchemy.exc import SQLAlchemyError

from . import main
from .. import db, mail
from ..models import (  User, 
                        Question, 
                        Tag,
                        FavouriteQuestionAssoc as FQ,
                        UpvoteQuestionAssoc as UQ,
                        DownvoteQuestionAssoc as DQ,
                        Solution,
                        UpvoteDownvoteSolutionAssoc as UDS,
                        UserSetting as US,
                        SolvedQuestionsAssoc as SQ)
from .forms import UserTagsForm, ContactUsForm
from ..question.forms import SolutionForm
from ..question.views import associate_tags
from ..utilities import print_debug, bad_request, add_to_db, add_to_db_ajax, dual_response


@main.before_app_request
def ping():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
        add_to_db(current_user, 'Last Seen Unsuccessful.')


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
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

    return render_template('home.html',
                           tags=tags, 
                            ques=ques,
                            side_ques=side_ques, 
                            form=form,
                            sol_form=sol_form)

def add_tags(tags):

    if current_user.associated_tags.count() > 10:
        return bad_request('You cannot add any more tags. Delete some tags and try again.', category='warning')

    if not tags:
            return bad_request('At least one tag is required', 406)

    """
    This loop checks to see if any matching tags
    for this user exists or not. Since, SQLAlchemy will
    either generate unique contraint error or Add multiple 
    duplicate entries. Hence, it is checked manually."""
    for tag in tags:
        if tag not in current_user.associated_tags:
            current_user.associated_tags.append(tag)

    add_to_db(current_user, 'Tags could not be properly saved. Please try again.')

    result = {}
    for tag in current_user.associated_tags:
        result[tag.tagname] = dict(id=tag.id, count=tag.questions.count())
    return jsonify(result)

def remove_tag(tag):
    
    if tag not in current_user.associated_tags:
        return bad_request('The tag %s is not associated to you.')


    current_user.associated_tags.remove(tag)

    add_to_db(current_user, 'Tag cannot be removed.')

    return jsonify(message='Tag removed successfully.', tagname=tag.tagname)


@main.route('/add-user-tags', methods=['POST'])
@login_required
def add_user_tags():
    form = UserTagsForm()

    if form.validate_on_submit():

        # returns a list of tags that are not in the DB
        tags = associate_tags(form)
        
        return add_tags(tags)


    return bad_request('Form submission is not correct', 403)


@main.route('/remove-user-tags', methods=['POST'])
@login_required
def remove_user_tags():
    result = {}

    tag_id = request.form.get('id', 0, type=int)
    tag = Tag.query.get_or_404(tag_id)

    return remove_tag(tag)


@main.route('/user-tags', methods=['POST'])
@login_required
def user_tags():
    tag_id = request.form.get('tag', 0, type=int)
    tag = Tag.query.get_or_404(tag_id)

    if tag in current_user.associated_tags:
        return remove_tag(tag)
    else:
        return add_tags([tag])


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
                            user=user)


@main.route('/user/<int:id>/<ques_type>')
@login_required
def user_questions(id, ques_type):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 2, type=int)
    pagination = None
    filename = None
    
    if ques_type == 'posted':    
        pagination = user.questions.paginate(page,
                                            per_page=current_app.config['PER_PAGE_LIMIT'])
        filename = "_posted.html"
    elif ques_type == 'solved':
        pagination = user.questions_solved\
                         .paginate(page,
                                   per_page=current_app.config['PER_PAGE_LIMIT'])
        filename = "_solved.html"
    elif ques_type == 'favourited':
        pagination = user.questions_fav\
                         .paginate(page, per_page=current_app.config['PER_PAGE_LIMIT'])
        filename = '_favourited.html'
    elif ques_type == 'upvoted':
        pagination = user.questions_upvoted\
                         .paginate(page, per_page=current_app.config['PER_PAGE_LIMIT'])
        filename = '_upvoted.html'
    elif ques_type == 'downvoted':
        pagination = user.questions_downvoted\
                         .paginate(page, per_page=current_app.config['PER_PAGE_LIMIT'])
        filename = '_downvoted.html'
    else:
        return bad_request("Wrong request format.")
    return jsonify(content=render_template(filename,
                                            pagination=pagination))

@main.route('/user/info', methods=['POST', 'GET'])
@login_required
def user_info():
    desc = request.form.get('description', '')
    username = request.form.get('username', '')

    if username:
        current_user.username = username
        msg = 'Username updated successfully.'
    elif desc:
        current_user.description = desc
        msg = 'Description updated successfully.'
    else:
        return bad_request('Field Empty.')

    add_to_db(current_user, 'Update unsuccessful')
    redir = url_for('.user', id=current_user.id)

    return dual_response(msg, redir=redir)


@main.route('/tags/<tagname>')
@login_required
def tags(tagname):
    page = request.args.get('page', 0, type=int)

    tag = Tag.query.filter_by(tagname=tagname).first()

    if not tag:
        return abort(404)
    
    if page:
        pagination = tag.questions.paginate(page, 
                              per_page=current_app.config['PER_PAGE_LIMIT'])
        return jsonify(content=render_template('_tags.html',
                                pagination=pagination))

    return render_template('tags.html',
                            tag=tag,
                            ques=tag.questions)

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
    elif name == 'HO':
        if setting.hide_options:
            setting.hide_options = False
        else:
            setting.hide_options = True
    else:
        return bad_request('Setting Not Found')

    add_to_db_ajax(setting, 'Setting Unsuccessful')

    return jsonify(message='Setting successful')


@main.route('/contact-us', methods=['POST', 'GET'])
@login_required
def contact_us():
    form = ContactUsForm()

    if form.validate_on_submit():

        msg = Message('Message - Practice Engine', sender='giney.paradise@gmail.com')
        
        body = 'User ID - %s\n' % current_user.id
        body += 'Email - %s\n' % current_user.email
        body += '| Message - %s' % form.message.data

        msg.recipients = ['giney.paradise@gmail.com']
        msg.body = body
        
        mail.send(msg)

        return dual_response('Your feedback has been successfully sent.', redir=url_for('.home'))

    return render_template('contact.html', form=form)