from pathlib import Path

from services.analysis_service import analyze_conversation


def main():
    print("This project includes a basic analysis pipeline and API endpoint.")
    print("Use /api/analyze or run python scripts/batch_analyze.py after importing data.")

    # If sample data exists and ready, you can wire in further processing here.
    print(f"Project root: {Path(__file__).resolve().parents[1]}")


if __name__ == "__main__":
    main()
