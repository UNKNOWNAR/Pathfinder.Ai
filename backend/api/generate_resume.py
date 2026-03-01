from flask_restful import Resource
import io
from flask import request, send_file
from services.llm_service import LLMService
from services.compiler_service import CompilerService
from models.profile import Profile
from flask_jwt_extended import jwt_required, get_jwt_identity

# Initialize services
llm_service = LLMService()
compiler_service = CompilerService()

class GenerateResume(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()
            jd_text = data.get('jd_text') if data else None
            
            user_id = get_jwt_identity()
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                return {'message': 'Student profile not found'}, 404

            if not jd_text:
                return {'message': 'Job Description (jd_text) is required'}, 400
            
            student_data = profile.to_dict()
            
            print("Generating LaTeX code via Hugging Face...")
            latex_code = llm_service.generate_latex_resume(
                jd_text=jd_text, 
                student_profile=student_data
            )
            
            print("Compiling LaTeX to PDF...")
            pdf_bytes = compiler_service.compile_latex_to_pdf(latex_code)
            
            print("Successfully generated PDF.")
            
            # Return as downloadable file
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='Pathfinder_Tailored_Resume.pdf'
            )
            
        except Exception as e:
            print(f"Error in generate resume: {str(e)}")
            return {"error": str(e)}, 500
        
