import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models.file_model import File
from models.result_model import Result
from utils.text_extractor import extract_text
from utils.plagiarism_engine import PlagiarismEngine
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.pagesizes import A4

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
    user_id = get_jwt_identity()
    

    if not file1 or not file2:
        return jsonify({"error": "Both files are required"}), 400

    text1 = file1.read().decode("utf-8", errors="ignore")
    text2 = file2.read().decode("utf-8", errors="ignore")

    
    tfidf_score = PlagiarismEngine.tfidf_similarity(text1, text2)
    jaccard_score = PlagiarismEngine.jaccard_similarity(text1, text2)
    sequence_score = PlagiarismEngine.sequence_similarity(text1, text2)

   
    final_score = (
        (0.4 * tfidf_score) +
        (0.3 * jaccard_score) +
        (0.3 * sequence_score)
    )

    percentage_score = float(round(final_score * 100, 2))

    
    if percentage_score <= 30:
        level = "Low"
    elif percentage_score <= 70:
        level = "Medium"
    else:
        level = "High"

    
    result = Result(
        user_id=user_id, 
        
        file1_name=file1.filename,
        file2_name=file2.filename,
        plagiarism_score=percentage_score,

        tfidf_score=float(round(tfidf_score * 100, 2)),
        jaccard_score=float(round(jaccard_score * 100, 2)),
        sequence_score=float(round(sequence_score * 100, 2)),

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

    # If later you add user_id to Result model,
    # you can filter by user_id. For now we fetch all.
    results = Result.query.filter_by(user_id=user_id)\
                      .order_by(Result.created_at.desc())\
                      .all()


    response = []

    for r in results:
        response.append({
            "result_id": r.id,
            "file1_name": r.file1_name,
            "file2_name": r.file2_name,
            "plagiarism_score": float(r.plagiarism_score),

           
            "tfidf_score": float(r.tfidf_score),
            "jaccard_score": float(r.jaccard_score),
            "sequence_score": float(r.sequence_score),

            "level": r.level,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify(response), 200

# ==========================================
# GET SINGLE RESULT
# ==========================================
@file_bp.route("/results/<int:result_id>", methods=["GET"])
@jwt_required()
def get_single_result(result_id):
    user_id = get_jwt_identity()

    result = Result.query.filter_by(
        id=result_id,
        user_id=user_id
    ).first()

    if not result:
        return jsonify({"error": "Result not found"}), 404

    return jsonify({
        "result_id": result.id,
        "file1_name": result.file1_name,
        "file2_name": result.file2_name,
        "plagiarism_score": float(result.plagiarism_score),
        "tfidf_score": float(result.tfidf_score),
        "jaccard_score": float(result.jaccard_score),
        "sequence_score": float(result.sequence_score),
        "level": result.level,
        "created_at": result.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }), 200



# ==========================================
# GET ANALYTICS SUMMARY
# ==========================================
@file_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    user_id = get_jwt_identity()

    results = Result.query.filter_by(user_id=user_id).all()

    if not results:
        return jsonify({
            "total_checks": 0,
            "average_score": 0,
            "highest_score": 0,
            "level_distribution": {
                "Low": 0,
                "Medium": 0,
                "High": 0
            }
        }), 200

    total_checks = len(results)
    scores = [float(r.plagiarism_score) for r in results]

    average_score = round(sum(scores) / total_checks, 2)
    highest_score = max(scores)

    low = sum(1 for r in results if r.level == "Low")
    medium = sum(1 for r in results if r.level == "Medium")
    high = sum(1 for r in results if r.level == "High")

    return jsonify({
        "total_checks": total_checks,
        "average_score": average_score,
        "highest_score": highest_score,
        "level_distribution": {
            "Low": low,
            "Medium": medium,
            "High": high
        }
    }), 200
    
# ==========================================
# GENERATE PDF REPORT
# ==========================================
@file_bp.route("/report/<int:result_id>", methods=["GET"])
@jwt_required()
def generate_report(result_id):
    user_id = get_jwt_identity()

    result = Result.query.filter_by(
        id=result_id,
        user_id=user_id
    ).first()

    if not result:
        return jsonify({"error": "Report not found"}), 404
    REPORT_FOLDER = "reports"
    os.makedirs(REPORT_FOLDER, exist_ok=True)

    file_path = os.path.join(REPORT_FOLDER, f"report_{result_id}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Plagiarism Detection Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"File 1: {result.file1_name}", styles["Normal"]))
    elements.append(Paragraph(f"File 2: {result.file2_name}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"Plagiarism Score: {result.plagiarism_score}%", styles["Normal"]))
    elements.append(Paragraph(f"Level: {result.level}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Score Breakdown:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"TF-IDF: {result.tfidf_score}%", styles["Normal"]))
    elements.append(Paragraph(f"Jaccard: {result.jaccard_score}%", styles["Normal"]))
    elements.append(Paragraph(f"Sequence: {result.sequence_score}%", styles["Normal"]))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)
