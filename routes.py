


import os
import secrets
from sqlalchemy import or_

from flask import render_template , url_for, flash , redirect, request, abort
from googletrans import Translator
from firsttry import app, db, bcrypt

from firsttry.models import User, Post, Like, Books
# from firsttry.aws_models import Books
from flask_login import login_user, logout_user, login_required,  current_user


from firsttry.forms import RegisterationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm

# from firsttry.database import load_book, load_latest, load_book_high_ratings






# @app.route("/homepage")
# def hello_home():
#   output1 = load_latest()
#   output2 = load_book_high_ratings()
#   return render_template('homepage.html',
#                          latestbooks=output1,
#                          popularbooks=output2)

@app.route('/back')
def go_back():
    return redirect(request.referrer)

def load_book_from_author(author_name):
    books = Books.query.filter(Books.author.ilike(f'%{author_name}%')).all()
    # if len(books) == 0:
    #     inputs = author_name.split()
    #     for word in inputs:
    #         books += Books.query.filter(Books.author.ilike(f'%{word}%')).all()
    return [book.to_dict() for book in books]

def load_book_from_bookname(book_input):
    books = Books.query.filter(Books.titleComplete.ilike(f'%{book_input}%')).all()
    # if len(books) == 0:
    #     inputs = book_input.split()
    #     for word in inputs:
    #         books += Books.query.filter(Books.titleComplete.ilike(f'%{word}%')).all()
    return [book.to_dict() for book in books]

def load_books_from_search(book_input):
    out1 = load_book_from_genre(book_input)
    out2 = load_book_from_bookname(book_input)
    out3 = load_book_from_author(book_input)
    out1 += out2
    out1 += out3
    if len(out1) > 50:
        return out1[:50]
    else:
        return out1



def load_book(id):
    book = Books.query.filter_by(id=id).first()
    if book is None:
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('hello_home'))
    return [book.to_dict()]



def load_latest():
    books = Books.query.filter(Books.Date > 2010).all()
    return [book.to_dict() for book in books[:50]]



def load_book_high_ratings():
    books = []
    with app.app_context():
        high_ratings_books = Books.query.filter(Books.likes >= 800000).all()
        for book in high_ratings_books[:50]:
            books.append(book.to_dict())
    return books

   
def load_book_from_genre(genre_input):
    books = []
    for book in Books.query.filter(or_(Books.genre0.like(f'%{genre_input}%'),
                                        Books.genre1.like(f'%{genre_input}%'),
                                        Books.genre2.like(f'%{genre_input}%'),
                                        Books.genre3.like(f'%{genre_input}%'))).limit(51):
        books.append(book.to_dict())
    return books



@app.route('/')
@app.route("/homepage")
def hello_home():
  output1 = load_latest()
  output2 = load_book_high_ratings()
  return render_template('homepage.html',
                         latestbooks=output1,
                         popularbooks=output2)

@app.route('/home', methods=["GET", "POST"])
def Home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)
        

        if request.method == "POST":
            try:
                selected_language = request.form['select-language']
                translator = Translator()
                for post in posts:
                    txt_to_translate = post.content
                    title_to_translate = post.title

                    chunks = [
                        txt_to_translate[i:i + 5000]
                        for i in range(0, len(txt_to_translate), 5000)
                    ]

                    translated_chunks = [
                        translator.translate(chunk, dest=selected_language) for chunk in chunks
                    ]

                    translated_txt = "".join(
                        [chunk.text for chunk in translated_chunks])

                    # translated_txt = translator.translate(txt_to_translate, dest = selected_language)
                    translated_title = translator.translate(title_to_translate, dest = selected_language)
                    post.content = translated_txt
                    post.title = translated_title.text
            except:
                for post in posts:
                    post.content = "<ERROR: We are not able to handle this request right now>"
                    post.title = "<ERROR: We are not able to handle this request right now>"
            
            return render_template("home-final.html" , posts=posts)
        else:
            return render_template("home-final.html" , posts=posts)
    else:
        flash('You need to log in first!', 'info')
        return redirect(url_for('login'))



@app.route('/about')
def about():
    return render_template("about.html", title=about)

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated :
        return redirect(url_for('Home'))
    form = RegisterationForm()
    if form.validate_on_submit() :
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template("register-final.html", title='Register', form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated :
        return redirect(url_for('Home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data) :
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for(hello_home)) if next_page else redirect(url_for('hello_home'))
        else:
            flash('Login Unsuccessful. Please check email and Password','danger')
    return render_template("login-final.html", title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('hello_home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn )
    form_picture.save(picture_path)

    return picture_fn


@app.route('/account' , methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('myaccount.html', title='Account', image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('Home'))
    return render_template('newpost.html', title='New Post',
                           form=form, legend='New Post')



@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    # likes = Like.query.filter_by(post_id=post_id).count()
    return render_template('post-final.html', title=post.title, post=post)



@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('updatepost.html', title='Update Post',
                           form=form, legend='Update Post')



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('Home'))

@app.route("/user/<string:username>", methods=["GET", "POST"])
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    
    if request.method == "POST":
        try:
            selected_language = request.form['select-language']
            translator = Translator()
            for post in posts:
                txt_to_translate = post.content
                title_to_translate = post.title

                chunks = [
                    txt_to_translate[i:i + 5000]
                    for i in range(0, len(txt_to_translate), 5000)
                ]

                translated_chunks = [
                    translator.translate(chunk, dest=selected_language) for chunk in chunks
                ]

                translated_txt = "".join(
                    [chunk.text for chunk in translated_chunks])


                #translated_txt = translator.translate(txt_to_translate, dest = selected_language)
                translated_title = translator.translate(title_to_translate, dest = selected_language)
                post.content = translated_txt
                post.title = translated_title.text
        except:
            for post in posts:
                post.content = "<ERROR: We are not able to handle this request right now>"
                post.title = "<ERROR: We are not able to handle this request right now>"
        
        return render_template('user_posts-final.html', posts=posts, user=user)
    else:
        return render_template('user_posts-final.html', posts=posts, user=user)




@app.route("/home", methods=['POST'])
def search_genre():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))
  # return render_template('finalrecomm.html')


# @app.route("/search/genre")
# def hello_searched_genre(inp):
# out = load_book_from_genre(inp)
# return render_template('finalrecomm.html')


@app.route("/search", methods=['POST'])
def hello_searched_genre():
  data = request.form
  inp = data['search_text']
  out = load_books_from_search(inp)
  return render_template('finalrecomm.html', booksinput=out)


# @app.route("/overview/<book_id>")
# def hello_specific_book(book_id):
#   output1 = load_book(book_id)
#   return render_template('finalreview.html', booksinput=output1)


@app.route("/overview/<book_id>", methods=["GET", "POST"])
def hello_specific_book(book_id):
  output1 = load_book(book_id)

  if request.method == "POST":
    try:
      txt_to_translate = output1[0]['description']
      summary_translate = output1[0]['Summary']
      selected_language = request.form['select-language']
      translator = Translator()

      chunks = [
        txt_to_translate[i:i + 5000]
        for i in range(0, len(txt_to_translate), 5000)
      ]

      translated_chunks = [
        translator.translate(chunk, dest=selected_language) for chunk in chunks
      ]

      translated_txt_overview = "".join(
        [chunk.text for chunk in translated_chunks])

      chunks = [
        summary_translate[i:i + 5000]
        for i in range(0, len(summary_translate), 5000)
      ]

      translated_chunks = [
        translator.translate(chunk, dest=selected_language) for chunk in chunks
      ]

      translated_txt_summary = "".join(
        [chunk.text for chunk in translated_chunks])

      # translated_txt_overview = translator.translate(txt_to_translate,
      #                                                dest=selected_language)
      # translated_txt_summary = translator.translate(summary_translate,
      #                                               dest=selected_language)

      txt = translated_txt_overview
      txt2 = translated_txt_summary
    except:
      txt = "<ERROR: We are not able to handle this request right now>"
      txt2 = "<ERROR: We are not able to handle this request right now>"

    return render_template('finalreview.html',
                           booksinput=output1,
                           overview=txt,
                           summary=txt2)
  else:
    return render_template('finalreview.html',
                           booksinput=output1,
                           overview=output1[0]['description'],
                           summary=output1[0]['Summary'])



@app.route("/overview/<book_id>", methods=['POST'])
def search_genre1():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))


@app.route("/genre/<genre_input>")
def hello_genre(genre_input):
  output2 = load_book_from_genre(genre_input)
  return render_template('finalrecomm.html', booksinput=output2)


@app.route("/genre/<genre_input>", methods=['POST'])
def search_genre2():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))


@app.route("/book/<bookname_input>")
def hello_book(bookname_input):
  output2 = load_book_from_bookname(bookname_input)
  return render_template('finalrecomm.html', booksinput=output2)


@app.route("/book/<bookname_input>", methods=['POST'])
def search_genre3():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))


@app.route("/author/<author_input>")
def hello_author(author_input):
  output2 = load_book_from_author(author_input)
  return render_template('finalrecomm.html', booksinput=output2)


@app.route("/author/<author_input>", methods=['POST'])
def search_genre4():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))


@app.route("/popularbooks")
def hello_popular_seeall():
  output = load_book_high_ratings()
  return render_template('finalrecomm.html', booksinput=output)


@app.route("/popularbooks", methods=['POST'])
def search_genre5():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))


@app.route("/latest")
def hello_latest():
  output = load_latest()
  return render_template('finalrecomm.html', booksinput=output)


@app.route("/latest", methods=['POST'])
def search_genre6():
  data = request.form
  print(data)
  input = data['search_text']
  print(input)
  output = load_books_from_search(input)
  # print(output)
  return redirect(url_for('hello_searched_genre', inp=output))




# def send_reset_email(user):
#     token = User.get_reset_token()
#     msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
#     msg.body = '''To reset your password, visit the following link:{url_for('reset_token', token=token, _external=True)} If you didn't make this request then simply ignore this email'''

# @app.route("/reset_password", methods=['GET', 'POST'])
# def reset_request():
#     if current_user.is_authenticated :
#         return redirect(url_for('Home'))
#     form = RequestResetForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         send_reset_email(user)
#         flash('An email has been sent with instructions to reset your password', 'info')
#         return(redirect(url_for('login')))
#     return render_template('reset_request.html', title='Reset Password', form=form)


# @app.route("/reset_password/<token>", methods=['GET', 'POST'])
# def reset_token(token):
#     if current_user.is_authenticated :
#         return redirect(url_for('Home'))
#     user = User.verify_reset_token(token)
#     if user is None:
#         flash('That is an invalid/expired token', 'warning')
#         return redirect(url_for('reset_request'))
#     form = ResetPasswordForm()
#     if form.validate_on_submit() :
        
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user.password = hashed_password
#         db.session.commit()
#         flash(f'Your password has been updated! You can now log in', 'success')
#         return redirect(url_for('login'))
#     return render_template('reset_token.html' , title='Reset Passwod', form=form)


@app.route("/home/like/<int:post_id>", methods=['GET','POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)

    # like = Like.query.filter_by(user_id=current_user.id, post=post).first()
    if Like.query.filter_by(post=post, user_id=current_user.id).first():
        flash('You already liked this post', 'warning')
    else:
        like = Like(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        # post.likes_count += 1
        db.session.commit()
        flash('Your like has been added!', 'success')
    return redirect(url_for('go_back'))




@app.route("/home/unlike/<int:post_id>", methods=['GET', 'POST'])
@login_required
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    # like = Like.query.filter_by(user_id=current_user.id, post=post).first()
    if not Like.query.filter_by(user_id=current_user.id, post=post).first():
        flash('You have not liked this post yet', 'warning')
    else:
        like = Like.query.filter_by(post=post, user_id=current_user.id ).first()
        db.session.delete(like)
        # post.likes_count -= 1
        db.session.commit()
        flash('Your dislike has been added!', 'success')
    return redirect(url_for('go_back'))


# @app.route("/like/<int:post_id>", methods=['POST'])
# @login_required
# def like(post_id):
#     post = Post.query.get_or_404(post_id)
#     like = Like(user_id=current_user.id, post_id=post_id)
#     db.session.add(like)
#     db.session.commit()
#     flash('Liked!', 'success')
#     return redirect(url_for('post', post_id=post.id))


# @login_required
# def likePost(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author == current_user:
#         flash('You cannot like your own post', 'warning')
#         return redirect(url_for('Home'))

#     like = Like.query.filter_by(author=current_user, post=post).first()
#     if like:
#         flash('You have already liked this post', 'warning')
#         return redirect(url_for('post', post_id=post.id))

#     like = Like(author=current_user, post=post)
#     db.session.add(like)
#     db.session.commit()

#     return jsonify({'message': 'Post liked successfully'}), 200

# @login_required
# def dislikePost(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author == current_user:
#         return jsonify({'message': 'You cannot dislike your own post'}), 403

#     like = Like.query.filter_by(author=current_user, post=post).first()
#     if not like:
#         return jsonify({'message': 'You have not liked this post yet'}), 400

#     db.session.delete(like)
#     db.session.commit()

#     return jsonify({'message': 'Post disliked successfully'}), 200

