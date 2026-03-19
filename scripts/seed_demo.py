"""
Seed MetricAnchor with demo datasets and semantic models.

Usage:
    python scripts/seed_demo.py [--api-url http://localhost:8000] [--reset]

What it does:
    1. Uploads sample_data/*.csv as datasets
    2. Creates a semantic model for each from examples/*/semantic_model.yml
    3. Prints a summary with dataset IDs for use in demos

Requires:
    pip install httpx pyyaml
"""

import argparse
import json
import sys
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).parent.parent
SAMPLE_DATA = ROOT / "sample_data"
EXAMPLES = ROOT / "examples"

DATASETS = [
    {
        "csv": "retail_sales.csv",
        "model_dir": "retail_sales",
        "model_name": "retail_sales",
    },
    {
        "csv": "support_tickets.csv",
        "model_dir": "support_tickets",
        "model_name": "support_tickets",
    },
    {
        "csv": "saas_funnel.csv",
        "model_dir": "saas_funnel",
        "model_name": "saas_funnel",
    },
]


def upload_dataset(client: httpx.Client, csv_path: Path) -> dict:
    with open(csv_path, "rb") as f:
        resp = client.post(
            "/api/datasets",
            files={"file": (csv_path.name, f, "text/csv")},
            timeout=30,
        )
    resp.raise_for_status()
    return resp.json()


def find_dataset_by_name(client: httpx.Client, name: str) -> dict | None:
    resp = client.get("/api/datasets", timeout=10)
    resp.raise_for_status()
    for ds in resp.json().get("datasets", []):
        if ds["name"] == name or ds["original_filename"] == name:
            return ds
    return None


def create_semantic_model(
    client: httpx.Client,
    dataset_id: str,
    name: str,
    definition: dict,
) -> dict:
    resp = client.post(
        "/api/semantic_models",
        json={"dataset_id": dataset_id, "name": name, "definition": definition},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def list_semantic_models(client: httpx.Client, dataset_id: str) -> list[dict]:
    resp = client.get(f"/api/semantic_models?dataset_id={dataset_id}", timeout=10)
    resp.raise_for_status()
    return resp.json().get("semantic_models", [])


def delete_semantic_models(client: httpx.Client, dataset_id: str) -> int:
    models = list_semantic_models(client, dataset_id)
    for m in models:
        client.delete(f"/api/semantic_models/{m['id']}", timeout=10)
    return len(models)


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed MetricAnchor demo data")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Base URL of the running API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing semantic models for demo datasets before re-creating",
    )
    args = parser.parse_args()

    client = httpx.Client(base_url=args.api_url)

    # Health check
    try:
        resp = client.get("/api/health", timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: API not reachable at {args.api_url}: {e}")
        print("Run 'make up' first, then retry.")
        sys.exit(1)

    print(f"Connected to {args.api_url}\n")

    results = []

    for cfg in DATASETS:
        csv_path = SAMPLE_DATA / cfg["csv"]
        model_yml = EXAMPLES / cfg["model_dir"] / "semantic_model.yml"

        print(f"── {cfg['csv']} ──────────────────────────────────────────")

        if not csv_path.exists():
            print(f"  SKIP: {csv_path} not found. Run: python sample_data/generate.py")
            continue

        # Upload dataset (or find existing one with same filename)
        ds_name = csv_path.stem  # e.g. "retail_sales"
        existing = find_dataset_by_name(client, csv_path.name)
        if existing:
            print(f"  Dataset already exists (id={existing['id']}) — skipping upload")
            dataset = existing
        else:
            print(f"  Uploading {csv_path.name}…", end=" ", flush=True)
            dataset = upload_dataset(client, csv_path)
            print(f"done  (id={dataset['id']}, rows={dataset.get('row_count','?')})")

        dataset_id = dataset["id"]

        # Optionally reset existing semantic models
        if args.reset:
            deleted = delete_semantic_models(client, dataset_id)
            if deleted:
                print(f"  Deleted {deleted} existing semantic model(s)")

        # Load semantic model YAML
        if not model_yml.exists():
            print(f"  SKIP: {model_yml} not found — no semantic model created")
            results.append({"dataset": ds_name, "dataset_id": dataset_id, "model_id": None})
            continue

        with open(model_yml) as f:
            definition = yaml.safe_load(f)

        # Create semantic model
        existing_models = list_semantic_models(client, dataset_id)
        if existing_models and not args.reset:
            model = existing_models[0]
            print(f"  Semantic model already exists (id={model['id']}) — use --reset to replace")
        else:
            print(f"  Creating semantic model '{cfg['model_name']}'…", end=" ", flush=True)
            model = create_semantic_model(client, dataset_id, cfg["model_name"], definition)
            print(f"done  (id={model['id']})")

        results.append({
            "dataset": ds_name,
            "dataset_id": dataset_id,
            "model_id": model["id"],
        })
        print()

    # Summary
    print("══════════════════════════════════════════════════════════════")
    print("Seed complete. Copy these IDs for quick API testing:\n")
    for r in results:
        print(f"  {r['dataset']}")
        print(f"    dataset_id: {r['dataset_id']}")
        print(f"    model_id:   {r['model_id']}")
        print()

    print(f"Open {args.api_url.replace('8000','3000')} to start asking questions.")


if __name__ == "__main__":
    main()
