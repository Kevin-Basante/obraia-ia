from app.reports.prompt import summary_prompt


def test_the_public_prompt_forbids_money():
    public = summary_prompt("es", "public", "{}")
    full = summary_prompt("es", "full", "{}")

    assert "Spanish (Colombia)" in public
    assert "never mention budgets" in public
    assert "never mention budgets" not in full
    assert "approved budget" in full
