from extensions import db
from datetime import datetime


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    file1_name = db.Column(db.String(255), nullable=False)
    file2_name = db.Column(db.String(255), nullable=False)
    plagiarism_score = db.Column(db.Float, nullable=False)
    level = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Result {self.plagiarism_score}%>"
