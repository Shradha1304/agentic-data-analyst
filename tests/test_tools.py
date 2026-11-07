from pathlib import Path

import pandas as pd
import pytest

from analyst.tools import get_schema, describe_column, plot_histogram


@pytest.fixture
def df():
    return pd.read_csv("data/Titanic-Dataset.csv")


# ---- get_schema ----
def test_schema_shape(df):
    schema = get_schema(df)
    assert schema["n_rows"] == 891
    assert schema["n_cols"] == 12


# ---- describe_column ----
def test_age_mean(df):
    result = describe_column(df, "Age")
    assert result["type"] == "numeric"
    assert abs(result["mean"] - 29.6991) < 0.01
    assert result["missing"] == 177


def test_categorical(df):
    result = describe_column(df, "Sex")
    assert result["top_values"]["male"] == 577


def test_bad_column(df):
    result = describe_column(df, "age")
    assert "error" in result
    assert "Age" in result["error"]


# ---- plot_histogram ----
def test_histogram_creates_file(df):
    result = plot_histogram(df, "Age")
    assert "error" not in result
    assert Path(result["chart_path"]).exists()


def test_histogram_non_numeric(df):
    result = plot_histogram(df, "Sex")
    assert "error" in result


def test_histogram_bad_column(df):
    result = plot_histogram(df, "age")
    assert "error" in result
    assert "Age" in result["error"]