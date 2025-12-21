from pathlib import Path

import streamlit.web.bootstrap as bootstrap


def main():
    """Run app."""
    streamlit_file = Path(__file__).parent / "app.py"

    bootstrap.run(str(streamlit_file), False, [], flag_options={})


if __name__ == "__main__":
    main()
