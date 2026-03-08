from flask_restful import Resource
import io
from flask import request, send_file
from services.llm_service import LLMService
from services.compiler_service import CompilerService
from models.profile import Profile
from flask_jwt_extended import jwt_required, get_jwt_identity
from limiter import limiter

# Initialize services
llm_service = LLMService()
compiler_service = CompilerService()

class GenerateResume(Resource):
    decorators = [limiter.limit("5 per hour", key_func=get_jwt_identity)]

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
            compile_result = compiler_service.compile_latex_to_pdf(latex_code, profile.user_id)
            pdf_bytes = compile_result["pdf_bytes"]
            s3_key = compile_result["s3_key"]
            presigned_url = compile_result["url"]

            print(f"Successfully generated PDF and uploaded to S3: {s3_key}")

            # Update Profile Resumes Array (Max 2)
            from models import db
            current_resumes = profile.resumes or []

            # Add new resume at the beginning
            new_resume_entry = {
                "s3_key": s3_key,
                "url": presigned_url,
                "created_at": __import__('datetime').datetime.utcnow().isoformat()
            }

            # Keep only the latest 10 resumes
            current_resumes.insert(0, new_resume_entry)

            # If we exceed the limit, delete the oldest one from S3 and remove from array
            if len(current_resumes) > 10:
                oldest_resume = current_resumes.pop()
                try:
                    old_s3_key = oldest_resume.get("s3_key")
                    if old_s3_key:
                        compiler_service.s3_service.delete_file(old_s3_key)
                except Exception as del_err:
                    print(f"Failed to delete old resume from S3: {del_err}")

            # Need to create a new list or SQLAlchemy JSON mutation won't be detected
            profile.resumes = list(current_resumes)
            db.session.commit()

            # Return as downloadable file
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='Pathfinder_Tailored_Resume.pdf'
            )
            
        except Exception as e:
            import logging
            logging.error(f"Error in generate resume: {str(e)}", exc_info=True)
            return {"error": str(e)}, 500
        
