from pathlib import Path


README = Path(__file__).parents[1] / "README.md"


def test_readme_documents_personal_finance_launch_and_seeded_credentials():
    readme = README.read_text(encoding="utf-8")

    assert "python finance_app.py" in readme
    assert "demo@finwise.app" in readme
    assert "demo123" in readme
