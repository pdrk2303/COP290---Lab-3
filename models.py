from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer 
from firsttry import db, login_manager, app
from flask_login import UserMixin





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin) :
    # __bind_key__ = 'local_db'
    id = db.Column( db.Integer, primary_key =True )
    username=db.Column(db.String(20), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    image_file=db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts= db.relationship('Post', backref='author' , lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)


    def has_liked_post(self, post):
        return Like.query.filter_by(user_id=self.id, post_id=post.id).count() > 0


    def get_reset_token(self, SALT=b'randomsalt'):
        s  = Serializer(app.config['SECRET_KEY'], salt=SALT)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try :
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"
    

class Post(db.Model) :
    # __bind_key__ = 'local_db'
    id = db.Column( db.Integer, primary_key =True )
    title=db.Column(db.String(100), nullable=False)  
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content= db.Column(db.Text, nullable=False)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id') , nullable=False) 
    likes = db.relationship('Like', backref='post', lazy=True)
    # likes_count = db.Column(db.Integer, default=0)

     
    def __repr__(self):
        return f"Post('{self.title}', '{self.likes}')"
    

class Like(db.Model):
    # __bind_key__ = 'local_db'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    def __repr__(self):
        return f"Like('{self.user_id}', '{self.post_id}')"


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)
    title = db.Column(db.String(1024))
    titleComplete = db.Column(db.String(1024))
    description = db.Column(db.Text)
    imageUrl = db.Column(db.Text)
    genre0 = db.Column(db.String(1024))
    genre1 = db.Column(db.String(1024))
    genre2 = db.Column(db.String(1024))
    genre3 = db.Column(db.String(1024))
    publisher = db.Column(db.String(1024))
    author = db.Column(db.String(1024))
    likes = db.Column(db.String(1024))
    numPages = db.Column(db.String(1024))
    Date = db.Column(db.String(1024))
    Summary = db.Column(db.Text)

    def __repr__(self):
        return f"Books('{self.title}', '{self.author}', '{self.Date}')"

    def to_dict(self):
        return  {
            'id' : self.id,
            'url' : self.url,
            'title' : self.title,
            'titleComplete' : self.titleComplete,
            'description' : self.description,
            'imageUrl' : self.imageUrl,
            'genre0' : self.genre0,
            'genre1' : self.genre1,
            'genre2' : self.genre2,
            'genre3' : self.genre3,
            'publisher' : self.publisher,
            'author' : self.author,
            'likes' : self.likes,
            'numPages' : self.numPages,
            'Date' : self.Date,
            'Summary' : self.Summary
        }
    