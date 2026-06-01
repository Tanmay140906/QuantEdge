import os
from dotenv import load_dotenv

# Load .env so GROQ_API_KEY is available to the app
load_dotenv()

# Then launch streamlit (this file is imported by app.py at the top if you prefer,
# or you can run:  python run.py  which calls streamlit programmatically)

if __name__ == "__main__":
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])