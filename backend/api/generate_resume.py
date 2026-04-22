from flask_restful import Resource
import io
from flask import request, send_file
from services.llm_service import LLMService
from services.compiler_service import CompilerService
from models.profile import Profile
from flask_jwt_extended import jwt_required, get_jwt_identity
from limiter import limiter

import logging

# Initialize services
logger = logging.getLogger(__name__)
llm_service = LLMService()
compiler_service = CompilerService()

class GenerateResume(Resource):
    @jwt_required()
    @limiter.limit("5 per hour")
    def post(self):
        user_id = get_jwt_identity()
        logger.info(f"POST /api/generate-resume triggered - User ID: {user_id}")
        
        try:
            data = request.get_json()
            jd_text = data.get('jd_text') if data else None

            if not jd_text:
                logger.warning(f"User {user_id} attempted resume generation with missing JD text.")
                return {'message': 'Job Description (jd_text) is required'}, 400

            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                logger.error(f"GenerateResume: Profile for user {user_id} not found in DB.")
                return {'message': 'Student profile not found'}, 404

            student_data = profile.to_dict()
            logger.info(f"Generating LaTeX code via LLM for user {user_id}...")
            
            latex_code = llm_service.generate_latex_resume(
                jd_text=jd_text,
                student_profile=student_data
            )
            
            if not latex_code:
                logger.error(f"LLM failed to return LaTeX code for user {user_id}")
                return {"message": "AI failed to generate resume code. Try a shorter JD."}, 500

            logger.info(f"Compiling LaTeX to PDF for user {user_id} (Length: {len(latex_code)})")
            
            try:
                compile_result = compiler_service.compile_latex_to_pdf(latex_code, profile.user_id)
            except Exception as comp_err:
                logger.error(f"Compiler service failed for user {user_id}: {str(comp_err)}")
                return {"message": f"Compilation Error: {str(comp_err)}"}, 500

            pdf_bytes = compile_result["pdf_bytes"]
            s3_key = compile_result["s3_key"]
            presigned_url = compile_result["url"]

            logger.info(f"Successfully generated PDF and uploaded to S3: {s3_key}")

            # Update Profile Resumes Array (Max 10)
            from models import db
            current_resumes = list(profile.resumes or [])

            # Add new resume at the beginning
            new_resume_entry = {
                "s3_key": s3_key,
                "url": presigned_url,
                "filename": f"Resume_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "created_at": __import__('datetime').datetime.utcnow().isoformat()
            }

            # Keep only the latest 10 resumes
            current_resumes.insert(0, new_resume_entry)

            if len(current_resumes) > 10:
                oldest_resume = current_resumes.pop()
                old_s3_key = oldest_resume.get("s3_key")
                if old_s3_key:
                    try:
                        compiler_service.s3_service.delete_file(old_s3_key)
                    except:
                        pass

            profile.resumes = current_resumes
            db.session.commit()
            logger.info(f"Profile updated for user {user_id} with new resume key {s3_key}")

            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='Pathfinder_Tailored_Resume.pdf'
            )
            
        except Exception as e:
            logger.error(f"UNHANDLED Error in generate resume (User {user_id}): {str(e)}", exc_info=True)
            return {"error": str(e)}, 500
        
