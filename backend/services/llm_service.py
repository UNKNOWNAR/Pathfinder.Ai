import os
import json
import re
import logging
import requests

class LLMService:
    # ─── Primary: Amazon Bedrock (Qwen 3 Next 80B) ───────────────────────────
    BEDROCK_API_KEY  = os.getenv('BEDROCK_API_KEY', '')
    BEDROCK_REGION   = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
    BEDROCK_MODEL    = 'qwen.qwen3-next-80b-a3b'

    # ─── Final Fallback: Groq ─────────────────────────────────────────────────
    # If Bedrock/Qwen fails, Qwen siblings share the same access path and
    # will fail together — skip straight to Groq.
    GROQ_API_KEY   = os.getenv('GROQ_API_KEY', '')
    GROQ_MODEL     = 'llama-3.3-70b-versatile'
    GROQ_ENDPOINT  = 'https://api.groq.com/openai/v1/chat/completions'

    def __init__(self):
        # Keep legacy attr names so nothing else in codebase breaks
        self.api_key   = self.GROQ_API_KEY
        self.model_id  = self.GROQ_MODEL
        self.endpoint  = self.GROQ_ENDPOINT

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
        2. If a specific section (e.g. Experience or Projects) is empty in the JSON, skip that section in the LaTeX output.
        3. For missing personal details (phone, LinkedIn, etc.), use a placeholder like "Not Provided" or omit the line entirely to maintain a professional look.
        4. Never refuse to generate the resume; use the information available to provide the best possible tailored result.
        5. Ensure all LaTeX special characters like &, %, $, #, _ in the JSON text are properly escaped with a backslash.
        """

        user_prompt = f"Here is the Job Description:\n{jd_text}\n\nHere is the candidate's profile data:\n{json.dumps(student_profile)}\n\nGenerate the complete LaTeX document matching the requested structure."

        try:
            raw_output = self.call_llm(system_prompt, user_prompt, max_tokens=2500, temperature=0.1)

            # BULLETPROOF REGEX EXTRACTION
            latex_match = re.search(r'(\\documentclass.*?\\end\{document\})', raw_output, re.DOTALL)

            if latex_match:
                latex_code = latex_match.group(1)
            else:
                logging.warning("Regex failed to find complete LaTeX document. Falling back to raw output.")
                latex_code = raw_output.strip()
                if latex_code.startswith("```latex"):
                    latex_code = latex_code[8:]
                elif latex_code.startswith("```"):
                    latex_code = latex_code[3:]
                if latex_code.endswith("```"):
                    latex_code = latex_code[:-3]

            return latex_code.strip()

        except Exception as e:
            logging.error(f"Error generating LaTeX resume: {e}")
            raise

    # ─── Unified LLM Caller: Bedrock-first, Groq-fallback ────────────────────

    def call_llm(self, system_prompt: str, user_prompt: str,
                  max_tokens: int = 500, temperature: float = 0.5) -> str:
        """
        Try Bedrock Qwen 3 Next 80B first.
        If it fails, skip straight to Groq — Qwen siblings share the same
        access path so trying them would be wasted latency.
        """
        # 1️⃣ Try Bedrock (Qwen 3 Next 80B)
        result = self._call_bedrock_direct(
            self.BEDROCK_MODEL, system_prompt, user_prompt, max_tokens, temperature
        )
        if result:
            return result

        # 2️⃣ Bedrock unavailable — fall back to Groq immediately
        logging.warning("Bedrock unavailable. Falling back to Groq.")
        return self._call_groq(system_prompt, user_prompt, max_tokens, temperature)

    def _call_bedrock_direct(self, model_id: str, system_prompt: str,
                              user_prompt: str, max_tokens: int, temperature: float) -> str | None:
        """
        Call Amazon Bedrock via Bearer token API key (ABSK key).
        Returns the text response, or None if the call fails.
        """
        if not self.BEDROCK_API_KEY:
            logging.debug("BEDROCK_API_KEY not set, skipping Bedrock call.")
            return None

        url = (f"https://bedrock-runtime.{self.BEDROCK_REGION}.amazonaws.com"
               f"/model/{model_id}/converse")
        headers = {
            "Authorization": f"Bearer {self.BEDROCK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "system": [{"text": system_prompt}],
            "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature}
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                content = (response.json()
                           .get('output', {})
                           .get('message', {})
                           .get('content', [{}])[0]
                           .get('text', ''))
                return content.strip()
            else:
                logging.warning(f"Bedrock [{model_id}] returned {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            logging.warning(f"Bedrock [{model_id}] exception: {e}")
            return None

    def _call_groq(self, system_prompt: str, user_prompt: str,
                   max_tokens: int, temperature: float) -> str:
        """Call Groq API as the final fallback."""
        if not self.GROQ_API_KEY:
            logging.error("GROQ_API_KEY is also missing — all LLM options exhausted.")
            raise ValueError("No LLM backend available. Please configure BEDROCK_API_KEY or GROQ_API_KEY.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.GROQ_API_KEY}"
        }
        body = {
            "model": self.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        try:
            resp = requests.post(self.GROQ_ENDPOINT, headers=headers, json=body, timeout=60)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logging.error(f"Groq API call also failed: {e}")
            raise
