from db import db
from sqlalchemy.sql import func
import bcrypt

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(50), nullable=False)

    # Method to set password
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Method to check password
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    #QA Chains
    qa_chains = db.relationship('QAChain', backref='user', lazy=True, cascade="all, delete-orphan")

class QAChain(db.Model):
    __tablename__ = "qachains"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key
    #Documents
    documents = db.relationship('Document', backref='qachain', lazy=True, cascade="all, delete-orphan")
    # Questions
    questions = db.relationship('Question', backref='qachain', lazy=True, cascade="all, delete-orphan")
    # Latest Update time
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # LLM CHAIN


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    qa_chain_id = db.Column(db.Integer, db.ForeignKey('qachains.id'), nullable=False)  # Foreign key
    filename = db.Column(db.String(100), nullable=False)
    filedata = db.Column(db.LargeBinary, nullable=False)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    qa_chain_id = db.Column(db.Integer, db.ForeignKey('qachains.id'), nullable=False)  # Foreign key
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
