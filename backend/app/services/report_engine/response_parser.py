"""Response Parser — extracts structured sections from LLM output.

If parsing fails, the entire output is returned as a single summary section.
"""
import re
from typing import Any


def parse_response(raw_output: str, language: str) -> dict[str, Any]:
    """Parse LLM output into structured report sections.

    Expected structure (markdown):
      ## Health Analysis
      ...
      ## Emotional State
      ...
      ## Health & Emotion Connection
      ...
      ## Priority Actions
      ...

    Returns a dict with:
      - summary: first paragraph (before any ## heading)
      - sections: list of {title, content}
      - raw_output: original text
    """
    if not raw_output or not raw_output.strip():
        return {
            "summary": "",
            "sections": [],
            "raw_output": raw_output or "",
        }

    # Try to parse markdown sections
    section_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    matches = list(section_pattern.finditer(raw_output))

    if not matches:
        return {
            "summary": raw_output.strip()[:300],
            "sections": [
                {
                    "title": "Wellness Analysis" if language == "English" else "健康分析",
                    "content": raw_output.strip(),
                }
            ],
            "raw_output": raw_output,
        }

    sections = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw_output)
        content = raw_output[start:end].strip()
        sections.append({"title": title, "content": content})

    first_heading = matches[0].start()
    summary = raw_output[:first_heading].strip()

    return {
        "summary": summary[:500] if summary else sections[0]["content"][:300],
        "sections": sections,
        "raw_output": raw_output,
    }
