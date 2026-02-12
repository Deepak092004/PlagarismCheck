from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, bcrypt, cors
from routes.auth_routes import auth_bp
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.file_routes import file_bp
from werkzeug.exceptions import RequestEntityTooLarge





app = Flask(__name__)
app.config.from_object(Config)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large (Max 10MB)"}), 413


# Initialize extensions
db.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
cors.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(file_bp, url_prefix="/api/files")
print(app.url_map)



@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello User {current_user}"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
