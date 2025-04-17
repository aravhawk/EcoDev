"""
send_batch.py
----------------
Generate a JSONL file that contains **all** problems listed in ``data/problem_list.py``
(currently 2000) in the format expected by the OpenAI *batch* endpoint and
immediately submit the batch request.

Running the script:

    python3 send_batch.py

This will create/update ``ecodev_2000_problems.jsonl`` in the ``data`` directory,
upload it to OpenAI with ``purpose="batch"`` and finally create the batch
request.  The behavior is equivalent to the old workflow that required three
separate commands (splitting –> jsonl –> send).
"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import List

from openai import OpenAI

import env

JSONL_PATH = pathlib.Path("data/ecodev_2000_problems.jsonl")
MODEL = "o4-mini"
EFFORT = "high"


def load_problems() -> List[str]:
    """Import and return the list of problems."""

    try:
        from data.problem_list import problems

    except ImportError as exc:  # pragma: no cover
        print("Could not import `data.problem_list.problems`:", exc)
        sys.exit(1)

    if not isinstance(problems, list):  # pragma: no cover – sanity guard
        print("`data.problem_list.problems` should be a list of strings.")
        sys.exit(1)

    return problems


def write_jsonl(problems: List[str], path: pathlib.Path = JSONL_PATH) -> None:
    """Serialize *problems* to *path* in JSONL format expected by the batch API."""

    with path.open("w", encoding="utf-8") as fp:
        for idx, problem in enumerate(problems, start=1):
            entry = {
                "custom_id": f"request-{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [{"role": "user", "content": problem}],
                    "reasoning_effort": EFFORT,
                },
            }

            # Using `json.dumps` ensures compact 1‑line representation.
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")


def create_and_send_batch(jsonl_path: pathlib.Path) -> None:
    """Upload *jsonl_path* and create the batch job via OpenAI SDK."""

    client = OpenAI(api_key=env.api_key)

    print(f"Uploading '{jsonl_path}' (purpose='batch')…")

    with jsonl_path.open("rb") as fp:
        batch_input_file = client.files.create(file=fp, purpose="batch")

    print("File uploaded – id:", batch_input_file.id)

    print("Creating batch request…")

    response = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": jsonl_path.stem},
    )

    print("Batch request submitted.")
    print("Batch id:", response.id)


def main() -> int:
    problems = load_problems()

    if not problems:
        print("Problem list is empty – nothing to do.")
        return 1

    print(f"Loaded {len(problems)} problems.")

    # 1. Write JSONL file (overwriting any existing one to guarantee freshness).
    write_jsonl(problems)
    print(f"Written JSONL file to '{JSONL_PATH}'.")

    # 2. Upload & create batch.
    try:
        create_and_send_batch(JSONL_PATH)
    except Exception as exc:
        print("Error while communicating with OpenAI API:", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
