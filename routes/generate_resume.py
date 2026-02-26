from flask import Blueprint, request, jsonify, send_file
import io
from services.llm_service import LLMService
from services.compiler_service import CompilerService

# Initialize the Flask Blueprint
resume_bp = Blueprint('resume', __name__)

llm_service = LLMService()
compiler_service = CompilerService()

@resume_bp.route("/api/generate-resume", methods=["POST"])
def generate_resume():
    try:
        # Flask way of getting JSON payload (replaces Pydantic ResumeRequest)
        data = request.get_json()
        
        if not data or 'jd_text' not in data or 'student_profile' not in data:
            return jsonify({"error": "Missing jd_text or student_profile in payload"}), 400
            
        print("Generating LaTeX code via Hugging Face...")
        latex_code = llm_service.generate_latex_resume(
            jd_text=data['jd_text'], 
            student_profile=data['student_profile']
        )
        
        print("Compiling LaTeX to PDF...")
        pdf_bytes = compiler_service.compile_latex_to_pdf(latex_code)
        
        print("Successfully generated PDF.")
        
        # Flask way of returning a downloadable file from raw bytes
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='Pathfinder_Tailored_Resume.pdf'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500