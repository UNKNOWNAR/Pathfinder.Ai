import boto3
import os
from config import Config
import json
import re
import logging

class LLMService:
    def __init__(self):
        # We assume AWS credentials are set in the environment or ~/.aws/credentials
        # Using us-east-1 or us-west-2 depending on where you enable models in AWS Bedrock
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
        self.api_key = os.getenv('BEDROCK_API_KEY')
        # Use Inference Profile prefix 'us.' as required for newest Claude 4.5+ models in us-east-1
        self.model_id = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        self.endpoint = "https://bedrock-runtime.us-east-1.amazonaws.com"

    def generate_latex_resume(self, jd_text: str, student_profile: dict) -> str:
        system_prompt = """
        You are an expert technical recruiter and LaTeX developer. Your task is to generate a professional, ATS-friendly resume in raw LaTeX code based on the provided JSON profile and target Job Description (JD).

        You MUST use the exact LaTeX preamble, packages, and structural commands provided in the template below.
        Rewrite the bullet points for Experience and Projects to perfectly match the keywords, impact, and metrics required by the target JD.

        REQUIRED LATEX STRUCTURE:

        \\documentclass[11pt,a4paper]{article}
        \\usepackage[margin=0.65in]{geometry}
        \\usepackage[hidelinks]{hyperref}
        \\usepackage{enumitem}
        \\usepackage{titlesec}
        \\usepackage{parskip}
        \\setlength{\\parskip}{1pt}
        \\pagestyle{empty}
        \\usepackage{xcolor}

        \\titleformat{\\section}{\\large\\bfseries}{}{0em}{}[\\titlerule]

        \\begin{document}

        % ================== HEADER ==================
        \\begin{center}
            {\\LARGE \\textbf{<Inject Name>}}\\\\
            <Inject Email> \\quad \\textbar{} \\quad <Inject Phone> \\\\[0.5em]
            \\href{<Inject LinkedIn URL>}{\\large\\textbf{LinkedIn}} \\quad \\textbar{} \\quad
            \\href{<Inject GitHub URL>}{\\large\\textbf{GitHub}} \\quad \\textbar{} \\quad
            \\href{<Inject LeetCode URL>}{\\large\\textbf{LeetCode}}
        \\end{center}

        % ================== EDUCATION ==================
        \\section*{Education}
        \\textbf{<Inject University>} \\hfill <Inject Grad Year> \\\\
        <Inject Degree> \\\\
        CGPA: <Inject CGPA>

        % ================== TECHNICAL SKILLS ==================
        \\section*{Technical Skills}
        \\textbf{Languages:} <Inject Languages> \\\\
        \\textbf{Frameworks/Tools:} <Inject Frameworks and Tools>

        % ================== EXPERIENCE ==================
        \\section*{Experience}
        % For each experience item:
        \\textbf{<Inject Role>} \\hfill \\textit{<Inject Duration>} \\\\
        \\textbf{<Inject Company>}
        \\begin{itemize}[leftmargin=*]
            \\item <Write JD-tailored bullet point focusing on quantifiable metrics>
            \\item <Write JD-tailored bullet point focusing on tech stack used>
        \\end{itemize}

        % ================== PROJECTS ==================
        \\section*{Projects}
        % For each project item:
        \\textbf{<Inject Project Name>} \\hfill \\textit{<Inject Tech Stack>} \\\\
        <Inject short description>
        \\begin{itemize}[leftmargin=*]
            \\item <Write JD-tailored bullet point proving competence>
            \\item <Write JD-tailored bullet point>
        \\end{itemize}

        % ================== ACHIEVEMENTS ==================
        % ONLY include this section if the student has achievements. If achievements list is empty or null, skip this entire section.
        \\section*{Achievements}
        % For each achievement item:
        \\textbf{<Inject Achievement Title>} \\hfill \\textit{<Inject Issuer> | <Inject Year>} \\\\
        <Inject short description of the achievement>

        \\end{document}

        RULES:
        1. Output ONLY the raw LaTeX code. Do not add any conversational text.
        2. Ensure all LaTeX special characters like &, %, $, #, _ in the JSON text are properly escaped with a backslash.
        """

        user_prompt = f"Here is the Job Description:\n{jd_text}\n\nHere is the candidate's profile data:\n{json.dumps(student_profile)}\n\nGenerate the complete LaTeX document matching the requested structure."

        # Bedrock Claude Messages API format
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2500,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.1
        })

        import requests
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["X-Api-Key"] = self.api_key

        try:
            # First attempt: requests with API key (most direct for Bedrock Marketplace / specialized keys)
            if self.api_key:
                url = f"{self.endpoint}/model/{self.model_id}/invoke"
                response = requests.post(url, headers=headers, data=body, timeout=30)
                if response.status_code == 200:
                    response_body = response.json()
                else:
                    logger.error(f"Bedrock Key call failed: {response.status_code} - {response.text}")
                    # Fallback to boto3 if API key mode fails
                    invoke_response = self.bedrock_client.invoke_model(
                        body=body,
                        modelId=self.model_id,
                        accept='application/json',
                        contentType='application/json'
                    )
                    response_body = json.loads(invoke_response.get('body').read())
            else:
                # Standard boto3 path
                invoke_response = self.bedrock_client.invoke_model(
                    body=body,
                    modelId=self.model_id,
                    accept='application/json',
                    contentType='application/json'
                )
                response_body = json.loads(invoke_response.get('body').read())

            raw_output = response_body.get('content')[0].get('text')

            # BULLETPROOF REGEX EXTRACTION
            # This grabs everything from \documentclass to \end{document} and ignores the rest
            latex_match = re.search(r'(\\documentclass.*?\\end\{document\})', raw_output, re.DOTALL)

            if latex_match:
                latex_code = latex_match.group(1)
            else:
                logging.warning("Regex failed to find complete LaTeX document. Falling back to raw output.")
                latex_code = raw_output.strip()

                # Legacy cleanup just in case
                if latex_code.startswith("```latex"):
                    latex_code = latex_code[8:]
                elif latex_code.startswith("```"):
                    latex_code = latex_code[3:]
                if latex_code.endswith("```"):
                    latex_code = latex_code[:-3]

            return latex_code.strip()

        except Exception as e:
            logging.error(f"Error generating LaTeX resume with AWS Bedrock: {e}")
            raise
