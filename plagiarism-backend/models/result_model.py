from extensions import db
from datetime import datetime


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


    file1_name = db.Column(db.String(255), nullable=False)
    file2_name = db.Column(db.String(255), nullable=False)

    plagiarism_score = db.Column(db.Float, nullable=False)

    
    tfidf_score = db.Column(db.Float, nullable=False)
    jaccard_score = db.Column(db.Float, nullable=False)
    sequence_score = db.Column(db.Float, nullable=False)

    level = db.Column(db.String(20), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    internet_matches = db.Column(db.JSON) # This stores the list of {url, score}
    original_text = db.Column(db.Text)    # You need this to generate the highlighted text

    def __repr__(self):
        return f"<Result {self.plagiarism_score}%>"
