
import json
import pytest

from evaluation import run_regression


def test_experiment_id_contains_dataset_version():
    experiment_id = run_regression.create_experiment_id("1.1")

    assert experiment_id.startswith("regression_v1_1_")
    assert experiment_id.endswith("Z")


def test_experiment_file_cannot_be_overwritten(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        run_regression,
        "RESULTS_DIR",
        tmp_path,
    )

    record = {
        "experiment": {
            "experiment_id": "regression_v1_1_test"
        },
        "summary": {
            "agreements": 65
        }
    }

    # First save succeeds.
    saved_path = run_regression.save_experiment_record(record)

    original_content = saved_path.read_text(
        encoding="utf-8"
    )

    # Second save must fail.
    with pytest.raises(FileExistsError):
        run_regression.save_experiment_record(record)

    # Existing file must remain unchanged.
    assert saved_path.read_text(
        encoding="utf-8"
    ) == original_content

    saved_record = json.loads(original_content)

    assert saved_record["summary"]["agreements"] == 65
