import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models.file_model import File
from models.result_model import Result
from utils.text_extractor import extract_text
from utils.plagiarism_engine import PlagiarismEngine


file_bp = Blueprint("files", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".docx",
    ".py", ".java", ".c", ".cpp", ".js"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


# ==========================================
# FILE UPLOAD ROUTE
# ==========================================
@file_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    if request.content_length and request.content_length > MAX_FILE_SIZE:
        return jsonify({"error": "File too large (Max 10MB)"}), 400

    filename = secure_filename(file.filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(file_path)

    extension = os.path.splitext(filename)[1].lower()
    extracted_text = extract_text(file_path, extension)

    new_file = File(
        user_id=user_id,
        filename=filename,
        file_type=extension,
        file_path=file_path
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        "message": "File uploaded successfully",
        "file_id": new_file.id,
        "extracted_text_preview": extracted_text[:500]
    }), 201


# ==========================================
# PLAGIARISM CHECK ROUTE
# ==========================================
@file_bp.route("/check", methods=["POST"])
@jwt_required()
def check_plagiarism():
    file1 = request.files.get("file1")
    file2 = request.files.get("file2")

    if not file1 or not file2:
        return jsonify({"error": "Both files are required"}), 400

    text1 = file1.read().decode("utf-8", errors="ignore")
    text2 = file2.read().decode("utf-8", errors="ignore")

    # Individual similarity scores
    tfidf_score = PlagiarismEngine.tfidf_similarity(text1, text2)
    jaccard_score = PlagiarismEngine.jaccard_similarity(text1, text2)
    sequence_score = PlagiarismEngine.sequence_similarity(text1, text2)

    final_score = round(
        (0.4 * tfidf_score) +
        (0.3 * jaccard_score) +
        (0.3 * sequence_score), 4
    )

    percentage_score = float(round(final_score * 100, 2))


    # Classification
    if percentage_score <= 30:
        level = "Low"
    elif percentage_score <= 70:
        level = "Medium"
    else:
        level = "High"

    # Save to database
    result = Result(
        file1_name=file1.filename,
        file2_name=file2.filename,
        plagiarism_score=percentage_score,
        level=level
    )

    db.session.add(result)
    db.session.commit()

    return jsonify({
        "plagiarism_score": percentage_score,
        "level": level,
        "breakdown": {
            "tfidf": float(round(tfidf_score * 100, 2)),
            "jaccard": float(round(jaccard_score * 100, 2)),
            "sequence": float(round(sequence_score * 100, 2))

        },
        "result_id": result.id
    }), 200
    
    # ==========================================
# GET USER RESULT HISTORY
# ==========================================
@file_bp.route("/results", methods=["GET"])
@jwt_required()
def get_user_results():
    user_id = get_jwt_identity()

    results = Result.query.order_by(Result.created_at.desc()).all()

    response = []

    for r in results:
        response.append({
            "result_id": r.id,
            "file1_name": r.file1_name,
            "file2_name": r.file2_name,
            "plagiarism_score": float(r.plagiarism_score),
            "level": r.level,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(response), 200

