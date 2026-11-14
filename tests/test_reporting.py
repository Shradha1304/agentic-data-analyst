from analyst.reporting import build_report, verify_grounding


def test_build_report_includes_evidence():
    tool_log = [
        {"step": 1, "tool": "get_schema", "result": {"n_rows": 891, "n_cols": 12}},
        {
            "step": 2,
            "tool": "describe_column",
            "result": {"column": "Age", "mean": 29.6991, "median": 28.0, "missing": 177},
        },
    ]

    report = build_report("The dataset has 891 rows and Age averages around 29.7.", tool_log)

    assert "## Evidence" in report["report"]
    assert "dataset has 891 rows and 12 columns" in report["report"]
    assert "Age" in report["report"]


def test_grounding_check_accepts_supported_numbers():
    tool_log = [
        {"step": 1, "tool": "get_schema", "result": {"n_rows": 891, "n_cols": 12}},
        {
            "step": 2,
            "tool": "describe_column",
            "result": {"column": "Age", "mean": 29.6991, "median": 28.0, "missing": 177},
        },
    ]

    check = verify_grounding("The dataset has 891 rows and Age mean is 29.70.", tool_log)

    assert check["verified"] is True
    assert check["issues"] == []
