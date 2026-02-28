import requests

class CompilerService:
    def compile_latex_to_pdf(self, latex_string: str) -> bytes:
        # 1. Primary Attempt: TeXLive.net (Highly reliable, backed by LearnLaTeX)
        try:
            print("Attempting compilation via TeXLive.net...")
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
                return response.content
            else:
                print("TeXLive returned a response, but it was not a valid PDF. Checking fallback...")
                
        except requests.exceptions.RequestException as e:
            print(f"TeXLive API failed: {e}")

        # 2. Fallback Attempt: YtoTech LaTeX-on-HTTP
        try:
            print("Falling back to YtoTech API...")
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
                return response.content
                
        except requests.exceptions.RequestException as e:
            print(f"YtoTech API failed: {e}")
            
        raise Exception("All cloud LaTeX compilers failed. The LLM may have generated invalid LaTeX syntax.")