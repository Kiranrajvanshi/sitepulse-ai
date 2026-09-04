import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, Response
from config import Config
from database.db import (
    init_db,
    save_analysis,
    get_all_analyses,
    get_analysis_by_id,
    delete_analysis,
    clear_all_analyses
)
from services.website_analyzer import run_website_analysis, normalize_url

# Configure server-side logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sitepulse.app")

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Ensure database schema is initialized
with app.app_context():
    init_db()

# --------------------------------------------------------------------------
# Main Web Routes
# --------------------------------------------------------------------------

@app.route("/")
def index():
    """Renders the SaaS homepage with hero and URL submission form."""
    return render_template("index.html")

@app.route("/report/<int:analysis_id>")
def view_report(analysis_id: int):
    """Renders the comprehensive health report dashboard for a specific analysis."""
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        return render_template("index.html", error="The requested audit report was not found."), 404
    return render_template("report.html", analysis=analysis)

@app.route("/report/<int:analysis_id>/print")
def print_report(analysis_id: int):
    """Renders a print and PDF-export friendly version of the audit report."""
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        return "Audit report not found", 404
    return render_template("printable_report.html", analysis=analysis)

@app.route("/history")
def history():
    """Renders historical audit archive stored in SQLite."""
    analyses = get_all_analyses(limit=50)
    return render_template("history.html", analyses=analyses)

@app.route("/about")
def about():
    """Renders information about SitePulse AI architecture, methodology and tech stack."""
    return render_template("about.html")

# --------------------------------------------------------------------------
# API Endpoints
# --------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Handles website analysis request asynchronously.
    Validates input, executes audit pipeline, persists to SQLite,
    and returns redirection URL.
    """
    data = request.get_json(silent=True) or {}
    raw_url = data.get("url", "").strip()

    if not raw_url:
        return jsonify({"success": False, "error": "Website URL is required."}), 400

    is_valid, normalized_url, err_msg = normalize_url(raw_url)
    if not is_valid:
        return jsonify({"success": False, "error": err_msg}), 400

    try:
        logger.info(f"Starting audit for: {normalized_url}")
        analysis_data = run_website_analysis(normalized_url)
        
        # Save to SQLite
        analysis_id = save_analysis(analysis_data)
        logger.info(f"Audit completed and saved with ID: {analysis_id}")

        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "report_url": url_for("view_report", analysis_id=analysis_id),
            "is_demo": analysis_data.get("is_demo", False)
        })

    except ValueError as ve:
        logger.warning(f"Validation error during audit of {normalized_url}: {str(ve)}")
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error during audit of {normalized_url}: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": "An internal error occurred during website analysis. Please try again."
        }), 500

@app.route("/api/history/<int:analysis_id>", methods=["DELETE"])
def api_delete_history(analysis_id: int):
    """Deletes an analysis record and associated issues."""
    try:
        success = delete_analysis(analysis_id)
        if success:
            return jsonify({"success": True, "message": "Record deleted successfully."})
        return jsonify({"success": False, "error": "Record not found."}), 404
    except Exception as e:
        logger.error(f"Failed to delete analysis {analysis_id}: {str(e)}")
        return jsonify({"success": False, "error": "Database error while deleting record."}), 500

@app.route("/api/history/clear", methods=["POST"])
def api_clear_history():
    """Clears all audit history from the SQLite database."""
    try:
        count = clear_all_analyses()
        return jsonify({"success": True, "deleted_count": count})
    except Exception as e:
        logger.error(f"Failed to clear history: {str(e)}")
        return jsonify({"success": False, "error": "Database error while clearing history."}), 500

# --------------------------------------------------------------------------
# SEO & Static Files
# --------------------------------------------------------------------------

@app.route("/robots.txt")
def robots_txt():
    return send_from_directory(os.path.join(app.root_path, "templates"), "robots.txt", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap_xml():
    return send_from_directory(os.path.join(app.root_path, "templates"), "sitemap.xml", mimetype="application/xml")

# --------------------------------------------------------------------------
# Error Handlers
# --------------------------------------------------------------------------

@app.errorhandler(404)
def handle_404(e):
    return render_template("index.html", error="Page not found. Redirected to home."), 404

@app.errorhandler(500)
def handle_500(e):
    logger.error(f"Server error: {str(e)}")
    return render_template("index.html", error="A server error occurred. Please try again later."), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
