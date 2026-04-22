import os
import json
import re
import logging

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model_id = "llama-3.3-70b-versatile"
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

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

        import requests
        
        if not self.api_key:
            logging.error("GROQ_API_KEY is missing.")
            raise ValueError("Groq API configuration missing")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        body = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2500
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=body, timeout=60)
            response.raise_for_status()
            data = response.json()
            raw_output = data["choices"][0]["message"]["content"]

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
