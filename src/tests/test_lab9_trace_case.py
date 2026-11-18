"""Regression test for the M1 trace case (docs/trace_case.md): C-002@11."""
import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders
from lab9.trace_case import investigate

pytestmark = pytest.mark.student


def _ctx(case: dict) -> EvaluatorContext:
    return EvaluatorContext(
        name="C-002@11",
        inputs={"claim_id": "C-002", "seed": 11},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_c002_trace_case_catches_seeded_regression_and_passes_fixed():
    bad = investigate("seeded_regression", "C-002", 11)
    assert bad["trial"]["lab8_pass"] is False
    assert graders.DbFactKept().evaluate(_ctx(bad)).value is False
    assert graders.RefundAmountCorrect().evaluate(_ctx(bad)).value is False

    good = investigate("fixed", "C-002", 11)
    assert good["trial"]["lab8_pass"] is True
    assert graders.DbFactKept().evaluate(_ctx(good)).value is True
    assert graders.RefundAmountCorrect().evaluate(_ctx(good)).value is True
