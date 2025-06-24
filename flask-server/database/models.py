from db import db
from sqlalchemy.sql import func

# Association table
question_documents = db.Table(
    "question_documents",
    db.Column("question_id", db.Integer, db.ForeignKey("question_log.id"), primary_key=True),
    db.Column("document_id", db.Integer, db.ForeignKey("document.id"), primary_key=True)
)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime(timezone=True), server_default=func.now())

class QuestionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    documents = db.relationship("Document", secondary=question_documents, backref="question_logs")
