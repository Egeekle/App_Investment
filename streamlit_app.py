"""Streamlit app entry point"""

from src.app.main import *

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", "src/app/main.py"]
    stcli.main()

