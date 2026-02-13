import io
import os
import html
import fitz  # PyMuPDF (Required for PDF text extraction)
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

# ReportLab components for PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

# Project specific imports
from extensions import db
from models.file_model import File
from models.result_model import Result
from utils.text_extractor import extract_text
from utils.plagiarism_engine import PlagiarismEngine
from utils.internet_detector import InternetDetector



file_bp = Blueprint("files", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".docx",
    ".py", ".java", ".c", ".cpp", ".js"
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

REPORT_FOLDER = "reports"
os.makedirs(REPORT_FOLDER, exist_ok=True)



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
# INTERNET SOURCE DETECTION
# ==========================================
@file_bp.route('/internet-check', methods=['POST'])
@jwt_required()
def internet_check():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        filename = file.filename
        # --- 2. Upgraded Text Extraction (Handles PDF and TXT) ---
        if filename.lower().endswith('.pdf'):
            # Read PDF stream directly from memory
            pdf_stream = file.read()
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            content = ""
            for page in doc:
                content += page.get_text()
            doc.close()
        else:
            # Fallback to UTF-8 for .txt files
            content = file.read().decode('utf-8')
        
        if not content.strip():
            return jsonify({"error": "Could not extract text or file is empty"}), 400

        # --- 3. Perform Internet Scan using Serper ---
        print(f"--- 🌐 Scanning: {filename} ---")
        matches = InternetDetector.detect_internet_plagiarism(content)

        # --- 4. Calculate Scores ---
        overall_score = 0
        if matches:
            # Get the highest similarity percentage found
            overall_score = max(m['similarity_score'] for m in matches)

        # --- 5. Determine Plagiarism Level ---
        level = "Unique"
        if overall_score > 70: level = "High"
        elif overall_score > 30: level = "Moderate"
        elif overall_score > 0.1: level = "Low"

        # --- 6. Save to PostgreSQL (Using verified columns) ---
        new_result = Result(
            user_id=get_jwt_identity(),
            file1_name=filename,
            file2_name="Web Search",
            plagiarism_score=overall_score,
            tfidf_score=overall_score, # Placeholder for overall
            jaccard_score=0,           # Web search usually uses cosine/tfidf
            sequence_score=0,
            level=level,
            internet_matches=matches,  # Saved to jsonb column
            original_text=content,     # Saved to text column for highlighting
            created_at=datetime.utcnow()
        )

        db.session.add(new_result)
        db.session.commit()

        # --- 7. Return Response ---
        return jsonify({
            "message": "Internet scan completed",
            "result_id": new_result.id,
            "overall_score": overall_score,
            "level": level,
            "matches": matches[:5]  # Sending top 5 matches to frontend
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ INTERNET CHECK ERROR: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500
    
# ==========================================
# GET USER RESULT HISTORY (WITH PAGINATION)
# ==========================================
@file_bp.route("/results", methods=["GET"])
@jwt_required()
def get_user_results():
    user_id = get_jwt_identity()

    # Get query parameters (default values included)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    # Paginated query (only user's results)
    pagination = Result.query.filter_by(user_id=user_id) \
        .order_by(Result.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)

    results = pagination.items

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

    return jsonify({
        "total_results": pagination.total,
        "total_pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": per_page,
        "results": response
    }), 200


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
    
    # Fetch result from DB
    result = Result.query.filter_by(id=result_id, user_id=user_id).first()

    if not result:
        return jsonify({"error": "Report not found"}), 404

    try:
        # Define Path
        REPORT_FOLDER = "reports"
        os.makedirs(REPORT_FOLDER, exist_ok=True)
        file_path = os.path.join(REPORT_FOLDER, f"report_{result_id}.pdf")

        # Setup Document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # 1. Header Section
        elements.append(Paragraph("<b>Plagiarism Detection Report</b>", styles["Title"]))
        elements.append(Paragraph(f"Analysis Date: {datetime.now().strftime('%b %d, %Y')}", styles["Normal"]))
        elements.append(Spacer(1, 0.3 * inch))

        # 2. Summary Section
        summary_style = ParagraphStyle('Summary', fontSize=14, leading=16, alignment=1, textColor=colors.red)
        score = getattr(result, 'plagiarism_score', 0)
        elements.append(Paragraph(f"<b>OVERALL SIMILARITY: {score}%</b>", summary_style))
        elements.append(Spacer(1, 0.4 * inch))

        # 3. TOP SOURCES TABLE
        elements.append(Paragraph("<b>Top Sources Detected:</b>", styles["Heading2"]))
        
        # Safe access to internet_matches
        matches = getattr(result, 'internet_matches', []) or []
        
        source_data = [["#", "Source URL", "Match %"]]
        if matches:
            for i, match in enumerate(matches[:10], 1): # Top 10 sources
                url = match.get('url', 'N/A')
                sim_score = match.get('similarity_score', 0)
                # Create a clickable link in the PDF
                url_p = Paragraph(f"<link href='{url}' color='blue'>{url[:60]}...</link>", styles["Normal"])
                source_data.append([str(i), url_p, f"{sim_score}%"])
        else:
            source_data.append(["-", "No internet matches found", "0%"])

        table = Table(source_data, colWidths=[0.5*inch, 4.0*inch, 1.0*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))

        # 4. HIGHLIGHTED TEXT SECTION
        elements.append(Paragraph("<b>Detailed Analysis & Highlights:</b>", styles["Heading2"]))
        
        raw_text = getattr(result, 'original_text', "No text available for analysis.")
        processed_text = html.escape(raw_text)
        
        # Highlight logic
        if matches:
            for match in matches:
                snippet = match.get('snippet', '')
                if snippet and len(snippet) > 20:
                    escaped_snippet = html.escape(snippet)
                    # Wrap the snippet in a red bold font tag
                    highlighted = f"<font color='red'><b>{escaped_snippet}</b></font>"
                    processed_text = processed_text.replace(escaped_snippet, highlighted)

        # Body text style that allows XML/HTML tags
        body_style = ParagraphStyle('BodyText', fontSize=10, leading=14)
        elements.append(Paragraph(processed_text, body_style))

        # Build PDF
        doc.build(elements)
        
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500



@file_bp.route("/results/<int:result_id>", methods=["DELETE"])
@jwt_required()
def delete_result(result_id):
    user_id = get_jwt_identity()

    result = Result.query.filter_by(
        id=result_id,
        user_id=user_id
    ).first()

    if not result:
        return jsonify({"error": "Result not found"}), 404

    db.session.delete(result)
    db.session.commit()

    return jsonify({"message": "Result deleted successfully"}), 200

