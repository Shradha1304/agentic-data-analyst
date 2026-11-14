import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def extract_numbers(value: Any) -> list[float]:
    if value is None:
        return []
    text = json.dumps(value, sort_keys=True)
    matches = re.findall(r"[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?", text)
    return [float(match) for match in matches]


def _tolerance_for(value: float) -> float:
    return max(0.01, abs(value) * 0.01)


def verify_grounding(summary: str, tool_log: list[dict]) -> dict:
    summary_numbers = extract_numbers(summary)
    evidence_numbers = []
    for entry in tool_log:
        evidence_numbers.extend(extract_numbers(entry.get("result")))

    if not summary_numbers:
        return {
            "verified": True,
            "issues": [],
            "checked_numbers": 0,
            "evidence_numbers": len(evidence_numbers),
        }

    issues = []
    for number in summary_numbers:
        if not evidence_numbers:
            issues.append(f"No supporting tool results found for number {number}.")
            continue

        matched = any(abs(number - ref) <= _tolerance_for(ref) for ref in evidence_numbers)
        if not matched:
            issues.append(f"Number {number} is not supported by the tool output evidence.")

    return {
        "verified": not issues,
        "issues": issues,
        "checked_numbers": len(summary_numbers),
        "evidence_numbers": len(evidence_numbers),
    }


def summarize_tool_result(tool_name: str, result: dict) -> str:
    if not isinstance(result, dict):
        return f"{tool_name} returned a non-dictionary result."

    if "n_rows" in result and "n_cols" in result:
        return f"dataset has {result['n_rows']} rows and {result['n_cols']} columns."

    if "mean" in result and "median" in result and "missing" in result:
        return (
            f"{result.get('column', tool_name)}: mean={result['mean']}, median={result['median']}, "
            f"missing={result['missing']}."
        )

    if "top_values" in result:
        top = ", ".join(f"{k}={v}" for k, v in list(result["top_values"].items())[:5])
        return f"{result.get('column', tool_name)} top values: {top}."

    if "chart_path" in result:
        return f"chart saved at {result['chart_path']}."

    return json.dumps(result, sort_keys=True)[:200]


def build_report(summary: str, tool_log: list[dict]) -> dict:
    clean_summary = (summary or "").strip()
    evidence_lines = []

    for entry in tool_log:
        tool_name = entry.get("tool")
        result = entry.get("result")
        if not tool_name or result is None:
            continue
        evidence_lines.append(
            f"- Step {entry.get('step', '?')} ({tool_name}): {summarize_tool_result(tool_name, result)}"
        )

    report = clean_summary
    if evidence_lines:
        report = f"{report}\n\n## Evidence\n" + "\n".join(evidence_lines)

    return {
        "report": report,
        "citations": evidence_lines,
    }


def write_run_log(task: str, summary: str, tool_log: list[dict], report: str, grounding: dict) -> str:
    outputs_dir = Path("outputs") / "run_logs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = outputs_dir / f"run_{timestamp}.json"

    payload = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "task": task,
        "summary": summary,
        "tool_log": tool_log,
        "report": report,
        "grounding_check": grounding,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    return str(path)
