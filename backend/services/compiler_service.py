import requests
import logging
from services.s3_service import S3Service

logger = logging.getLogger(__name__)

class CompilerService:
    def __init__(self):
        self.s3_service = S3Service()

    def compile_latex_to_pdf(self, latex_string: str, user_id: int) -> dict:
        # 1. Primary Attempt: TeXLive.net (Highly reliable, backed by LearnLaTeX)
        try:
            logger.info("Attempting compilation via TeXLive.net...")
            response = requests.post(
                "https://texlive.net/cgi-bin/latexcgi",
                files={
                    "filename[]": (None, "document.tex"),
                    "filecontents[]": (None, latex_string),
                    "return": (None, "pdf")
                },
                allow_redirects=True, # Follows the 301 redirect directly to the PDF file
                timeout=15
            )
            response.raise_for_status()

            # Verify the response is actually a PDF (starts with PDF magic bytes)
            if response.content.startswith(b'%PDF'):
                pdf_bytes = response.content
                s3_key = self.s3_service.upload_resume_pdf(pdf_bytes, user_id)
                if not s3_key:
                    raise Exception("Failed to upload generated PDF to S3")

                presigned_url = self.s3_service.get_presigned_url(s3_key)
                return {
                    "pdf_bytes": pdf_bytes, # keeping this for backward compatibility if needed
                    "s3_key": s3_key,
                    "url": presigned_url
                }
            else:
                logger.warning("TeXLive returned a response, but it was not a valid PDF. Checking fallback...")

        except requests.exceptions.RequestException as e:
            logger.error(f"TeXLive API failed: {e}")

        # 2. Fallback Attempt: YtoTech LaTeX-on-HTTP
        try:
            logger.info("Falling back to YtoTech API...")
            response = requests.post(
                "https://latex.ytotech.com/builds/sync",
                json={
                    "compiler": "pdflatex",
                    "resources": [
                        {
                            "main": True,
                            "content": latex_string
                        }
                    ]
                },
                timeout=15
            )
            response.raise_for_status()

            if response.content.startswith(b'%PDF'):
                pdf_bytes = response.content
                s3_key = self.s3_service.upload_resume_pdf(pdf_bytes, user_id)
                if not s3_key:
                    raise Exception("Failed to upload generated PDF to S3")

                presigned_url = self.s3_service.get_presigned_url(s3_key)
                return {
                    "pdf_bytes": pdf_bytes,
                    "s3_key": s3_key,
                    "url": presigned_url
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"YtoTech API failed: {e}")

        raise Exception("All cloud LaTeX compilers failed. The LLM may have generated invalid LaTeX syntax.")
