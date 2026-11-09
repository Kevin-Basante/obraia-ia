"""Instructions sent to the model together with the figures of a report."""

LANGUAGES = {"es": "Spanish (Colombia)", "en": "English"}

SUMMARY_PROMPT = """\
You are a construction project manager in Colombia. Below are the figures of the
{report} report of a small building project, as JSON. Write for the owner of the
project, who is not an engineer.

Write in {language}:
- summary: one paragraph of 3 to 5 sentences about how the work is going: progress,
  current phase, late tasks{money_rule}.
- recommendations: 2 to 4 short, concrete next steps, one sentence each.

Rules:
- Use only the figures given. Do not invent dates, amounts or names.
- Money is in Colombian pesos. In both languages write amounts like $ 68.645.101 and
  percents like 36,4%, the same format the rest of the report uses.
- Plain text only: no markdown, no lists inside the summary.
{public_rule}
Figures:
{figures}
"""

MONEY_RULE = ", spending against the approved budget and the risk of delay and cost overrun"
PUBLIC_RULE = "- This report is public: never mention budgets, expenses, money or risk scores.\n"


def summary_prompt(language: str, report_type: str, figures_json: str) -> str:
    full = report_type == "full"
    return SUMMARY_PROMPT.format(
        report="full" if full else "public",
        language=LANGUAGES.get(language, "English"),
        money_rule=MONEY_RULE if full else "",
        public_rule="" if full else PUBLIC_RULE,
        figures=figures_json,
    )
