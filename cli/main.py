"""
MetricAnchor CLI — power-user interface to the running API.

Usage:
    python -m cli.main --help
    python -m cli.main ingest retail_sales.csv
    python -m cli.main profile <dataset_id>
    python -m cli.main model init <dataset_id>
    python -m cli.main model list <dataset_id>
    python -m cli.main ask <dataset_id> "revenue by region"
    python -m cli.main eval run

Environment:
    METRICANCHOR_API_URL   Base URL of the API  (default: http://localhost:8000)
    METRICANCHOR_API_KEY   Bearer token if auth is enabled (optional)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# ── App / console ──────────────────────────────────────────────────────────────

app = typer.Typer(
    name="metricanchor",
    help="Trust-first analytics CLI — ingest data, define metrics, ask questions.",
    add_completion=False,
    rich_markup_mode="rich",
)
model_app = typer.Typer(help="Semantic model commands.")
app.add_typer(model_app, name="model")

console = Console()
err = Console(stderr=True, style="bold red")

# ── Config ─────────────────────────────────────────────────────────────────────

DEFAULT_API_URL = "http://localhost:8000"


def _api_url() -> str:
    return os.getenv("METRICANCHOR_API_URL", DEFAULT_API_URL).rstrip("/")


def _client() -> httpx.Client:
    headers: dict[str, str] = {"Content-Type": "application/json"}
    key = os.getenv("METRICANCHOR_API_KEY", "")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return httpx.Client(base_url=_api_url(), headers=headers, timeout=60.0)


def _check_api(client: httpx.Client) -> None:
    try:
        r = client.get("/api/health")
        r.raise_for_status()
    except Exception:
        err.print(
            f"Cannot reach API at {_api_url()}\n"
            "Run 'make up' to start the stack, or set METRICANCHOR_API_URL."
        )
        raise typer.Exit(1) from None


# ── ingest ─────────────────────────────────────────────────────────────────────


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="CSV or Parquet file to upload", exists=True),
    show_profile: bool = typer.Option(
        True, "--profile/--no-profile", help="Print column profile after upload"
    ),
):
    """Upload a CSV or Parquet file and register it as a dataset."""
    with _client() as client:
        _check_api(client)
        console.print(f"Uploading [bold]{file.name}[/bold] …", end=" ")
        with open(file, "rb") as fh:
            r = client.post(
                "/api/datasets",
                files={
                    "file": (
                        file.name,
                        fh,
                        "text/csv" if file.suffix == ".csv" else "application/octet-stream",
                    )
                },
                timeout=120.0,
            )
        if r.status_code not in (200, 201):
            console.print("[red]FAILED[/red]")
            err.print(f"HTTP {r.status_code}: {r.text}")
            raise typer.Exit(1)

        ds = r.json()
        console.print("[green]done[/green]")
        console.print()

        t = Table(show_header=False, box=box.SIMPLE)
        t.add_row("[dim]dataset_id[/dim]", ds["id"])
        t.add_row("[dim]name[/dim]", ds["name"])
        t.add_row("[dim]rows[/dim]", f"{ds.get('row_count', '?'):,}")
        t.add_row("[dim]columns[/dim]", str(ds.get("column_count", "?")))
        t.add_row("[dim]format[/dim]", ds.get("file_format", "?"))
        console.print(t)

        if show_profile and ds.get("profile"):
            _print_profile(ds["profile"])

        console.print(f"\nNext: [bold]python -m cli.main model init {ds['id']}[/bold]")


# ── profile ────────────────────────────────────────────────────────────────────


@app.command()
def profile(
    dataset_id: str = typer.Argument(..., help="Dataset ID to profile"),
):
    """Print the column profile for an existing dataset."""
    with _client() as client:
        _check_api(client)
        r = client.get(f"/api/datasets/{dataset_id}")
        if r.status_code == 404:
            err.print(f"Dataset '{dataset_id}' not found.")
            raise typer.Exit(1)
        r.raise_for_status()
        ds = r.json()

    console.print(f"[bold]{ds['name']}[/bold]  [dim]({ds['id']})[/dim]")
    console.print(
        f"  {ds.get('row_count', '?'):,} rows · {ds.get('column_count', '?')} columns · {ds.get('file_format', '?').upper()}\n"
    )

    if ds.get("profile"):
        _print_profile(ds["profile"])
    else:
        console.print("[yellow]No profile available for this dataset.[/yellow]")


def _print_profile(profile: dict) -> None:
    t = Table(
        "Column",
        "Type",
        "Null%",
        "Distinct",
        "Min",
        "Max",
        "Samples",
        box=box.SIMPLE_HEAD,
        header_style="bold cyan",
    )
    for col in profile.get("columns", []):
        flags = ""
        if col.get("is_date"):
            flags += " [dim][date][/dim]"
        elif col.get("is_numeric"):
            flags += " [dim][num][/dim]"
        elif col.get("is_bool"):
            flags += " [dim][bool][/dim]"
        t.add_row(
            col["name"] + flags,
            col.get("data_type", ""),
            f"{col.get('null_pct', 0):.1f}%",
            str(col.get("distinct_count", "")),
            str(col.get("min_value", "") or ""),
            str(col.get("max_value", "") or ""),
            ", ".join(col.get("sample_values", [])[:4]),
        )
    console.print(t)


# ── model ──────────────────────────────────────────────────────────────────────


@model_app.command("init")
def model_init(
    dataset_id: str = typer.Argument(..., help="Dataset ID to scaffold a model for"),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write YAML to this file (default: print to stdout)"
    ),
):
    """
    Scaffold a semantic model YAML from a dataset's column profile.

    The generated file is a starting point — edit it to add descriptions,
    aliases, synonyms, and business rules before uploading.
    """
    with _client() as client:
        _check_api(client)
        r = client.get(f"/api/datasets/{dataset_id}")
        if r.status_code == 404:
            err.print(f"Dataset '{dataset_id}' not found.")
            raise typer.Exit(1)
        r.raise_for_status()
        ds = r.json()

    yaml_text = _scaffold_model(ds)

    if output:
        output.write_text(yaml_text)
        console.print(f"Wrote scaffold to [bold]{output}[/bold]")
        console.print("\nNext: edit the file, then upload with:")
        console.print(f"  python -m cli.main model create {dataset_id} {output}")
    else:
        console.print(Syntax(yaml_text, "yaml", theme="monokai", line_numbers=False))


@model_app.command("create")
def model_create(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    yaml_file: Path = typer.Argument(..., help="Path to semantic model YAML file", exists=True),
):
    """Upload a semantic model YAML file to the API."""
    import yaml as pyyaml

    with open(yaml_file) as f:
        definition = pyyaml.safe_load(f)

    with _client() as client:
        _check_api(client)
        r = client.post(
            "/api/semantic_models",
            json={
                "dataset_id": dataset_id,
                "name": definition.get("name", "model"),
                "definition": definition,
            },
        )
        if r.status_code == 422:
            err.print("Validation failed:")
            detail = r.json().get("detail", r.text)
            if isinstance(detail, list):
                for e in detail:
                    err.print(f"  • {e}")
            else:
                err.print(f"  {detail}")
            raise typer.Exit(1)
        r.raise_for_status()
        model = r.json()

    console.print(f"[green]Semantic model created[/green]  id=[bold]{model['id']}[/bold]")
    console.print(f'\nNext: python -m cli.main ask {dataset_id} "your question"')


@model_app.command("list")
def model_list(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
):
    """List semantic models for a dataset."""
    with _client() as client:
        _check_api(client)
        r = client.get(f"/api/semantic_models?dataset_id={dataset_id}")
        r.raise_for_status()

    models = r.json().get("semantic_models", [])
    if not models:
        console.print(f"[yellow]No semantic models for dataset {dataset_id}.[/yellow]")
        console.print(f"Create one with: python -m cli.main model init {dataset_id}")
        return

    t = Table(
        "ID",
        "Name",
        "Metrics",
        "Dimensions",
        "Created",
        box=box.SIMPLE_HEAD,
        header_style="bold cyan",
    )
    for m in models:
        defn = m.get("definition", {})
        t.add_row(
            m["id"][:8] + "…",
            m["name"],
            str(len(defn.get("metrics", []))),
            str(len(defn.get("dimensions", []))),
            m.get("created_at", "")[:10],
        )
    console.print(t)


@model_app.command("validate")
def model_validate(
    yaml_file: Path = typer.Argument(..., help="Path to semantic model YAML file", exists=True),
):
    """Validate a local semantic model YAML file (no upload)."""
    import yaml as pyyaml

    with open(yaml_file) as f:
        definition = pyyaml.safe_load(f)

    with _client() as client:
        _check_api(client)
        r = client.post("/api/semantic_models/validate", json=definition)
        r.raise_for_status()
        result = r.json()

    if result.get("valid"):
        console.print(f"[green]✓[/green] {yaml_file.name} is valid")
        for w in result.get("warnings", []):
            console.print(f"  [yellow]warning:[/yellow] {w}")
    else:
        console.print(f"[red]✗[/red] {yaml_file.name} has errors:")
        for e in result.get("errors", []):
            console.print(f"  [red]error:[/red] {e}")
        for w in result.get("warnings", []):
            console.print(f"  [yellow]warning:[/yellow] {w}")
        raise typer.Exit(1)


def _scaffold_model(ds: dict) -> str:
    """Generate a starter semantic model YAML from a dataset profile."""
    import yaml as pyyaml

    name = ds["name"]
    profile = ds.get("profile", {})
    columns = profile.get("columns", [])

    # Classify columns
    metrics: list[dict] = []
    dimensions: list[dict] = []
    time_col: str | None = None

    for col in columns:
        col_name = col["name"]
        if col.get("is_date"):
            dimensions.append(
                {
                    "name": col_name,
                    "column": col_name,
                    "description": f"Date: {col_name}",
                    "aliases": [],
                    "is_date": True,
                }
            )
            if time_col is None:
                time_col = col_name
        elif col.get("is_numeric"):
            metrics.append(
                {
                    "name": col_name,
                    "description": f"TODO: describe {col_name}",
                    "expression": f"SUM({col_name})",
                    "aliases": [],
                    "format": "number",
                }
            )
        elif col.get("is_bool"):
            dimensions.append(
                {
                    "name": col_name,
                    "column": col_name,
                    "description": f"Boolean flag: {col_name}",
                    "aliases": [],
                }
            )
        else:
            dimensions.append(
                {
                    "name": col_name,
                    "column": col_name,
                    "description": f"TODO: describe {col_name}",
                    "aliases": [],
                }
            )

    model: dict = {
        "name": name,
        "dataset": name,
        "description": f"TODO: describe the {name} dataset",
        "grain": "TODO: one row per ...",
        "metrics": metrics
        or [
            {
                "name": "row_count",
                "description": "Number of rows",
                "expression": "COUNT(*)",
                "aliases": ["count", "total"],
                "format": "number",
            }
        ],
        "dimensions": dimensions,
    }
    if time_col:
        model["time_column"] = time_col

    return (
        "# Auto-generated by: metricanchor model init\n# Edit descriptions, aliases, and synonyms before using.\n\n"
        + pyyaml.dump(model, default_flow_style=False, sort_keys=False, allow_unicode=True)
    )


# ── ask ────────────────────────────────────────────────────────────────────────


@app.command()
def ask(
    dataset_id: str = typer.Argument(..., help="Dataset ID to query"),
    question: str = typer.Argument(..., help="Natural language question"),
    model_id: str | None = typer.Option(
        None, "--model", "-m", help="Semantic model ID (uses latest if omitted)"
    ),
    show_sql: bool = typer.Option(True, "--sql/--no-sql", help="Print generated SQL"),
    show_provenance: bool = typer.Option(False, "--provenance", help="Print full provenance trace"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Ask a natural-language analytics question against a dataset."""
    payload: dict = {"question": question, "dataset_id": dataset_id}
    if model_id:
        payload["model_id"] = model_id

    with _client() as client:
        _check_api(client)
        console.print(f"[dim]Asking:[/dim] {question} …")
        r = client.post("/api/questions", json=payload, timeout=120.0)
        if r.status_code == 422:
            err.print(f"Validation error: {r.json().get('detail', r.text)}")
            raise typer.Exit(1)
        r.raise_for_status()

    result = r.json()

    if json_output:
        console.print_json(json.dumps(result))
        return

    _print_answer(result, show_sql=show_sql, show_provenance=show_provenance)


def _print_answer(result: dict, show_sql: bool, show_provenance: bool) -> None:
    console.print()

    # Error
    if result.get("error"):
        console.print(
            Panel(
                f"[red]{result['error']}[/red]",
                title="[bold red]Pipeline Error[/bold red]",
                border_style="red",
            )
        )
        return

    # Clarification
    if result.get("clarifying_question"):
        console.print(
            Panel(
                result["clarifying_question"],
                title="[yellow]Clarification Needed[/yellow]",
                border_style="yellow",
            )
        )
        return

    # Answer
    if result.get("answer"):
        console.print(
            Panel(result["answer"], title="[bold green]Answer[/bold green]", border_style="green")
        )

    # Result table (first 20 rows)
    rows = result.get("rows", [])
    cols = result.get("columns", [])
    if rows and cols:
        console.print()
        t = Table(*cols, box=box.SIMPLE_HEAD, header_style="bold cyan", show_lines=False)
        for row in rows[:20]:
            t.add_row(*[str(v) if v is not None else "[dim]null[/dim]" for v in row])
        console.print(t)
        if len(rows) > 20:
            console.print(f"  [dim]… {len(rows) - 20} more rows[/dim]")

    # Confidence + metadata strip
    confidence = result.get("confidence", "")
    conf_color = {"high": "green", "medium": "yellow", "low": "red"}.get(confidence, "dim")
    meta_parts = [
        f"confidence=[{conf_color}]{confidence}[/{conf_color}]",
        f"chart={result.get('chart_type', '?')}",
        f"rows={result.get('row_count', 0):,}",
        f"ms={result.get('execution_ms', 0)}",
    ]
    console.print("\n  " + " · ".join(meta_parts))

    if result.get("assumptions"):
        console.print()
        for a in result["assumptions"]:
            console.print(f"  [dim]⚠  {a}[/dim]")

    if result.get("caveats"):
        for c in result["caveats"]:
            console.print(f"  [dim]ℹ  {c}[/dim]")

    # SQL
    if show_sql and result.get("sql"):
        console.print()
        console.print(Syntax(result["sql"], "sql", theme="monokai", line_numbers=False))

    # Semantic mappings
    mappings = result.get("semantic_mappings", [])
    if mappings:
        console.print()
        t2 = Table(
            "Phrase",
            "Resolved to",
            "Via",
            "Type",
            box=box.SIMPLE,
            show_header=True,
            header_style="dim",
        )
        for m in mappings:
            t2.add_row(
                m.get("phrase", ""), m.get("resolved_to", ""), m.get("via", ""), m.get("type", "")
            )
        console.print(t2)

    # Provenance
    if show_provenance and result.get("provenance"):
        console.print()
        console.print(Syntax(json.dumps(result["provenance"], indent=2), "json", theme="monokai"))


# ── eval ───────────────────────────────────────────────────────────────────────

eval_app = typer.Typer(help="Evaluation commands.")
app.add_typer(eval_app, name="eval")


@eval_app.command("run")
def eval_run(
    dataset: str | None = typer.Option(
        None, "--dataset", "-d", help="Run only cases for this dataset"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Write JSON report to this file"
    ),
):
    """
    Run the offline eval suite against the sample CSVs.

    No API key required — uses the stub LLM.
    Requires: python3 sample_data/generate.py (if CSVs not yet generated).
    """
    import asyncio

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    from evals.report import print_report, write_report
    from evals.runner import run_evals

    console.print("[dim]Running eval suite …[/dim]")
    results = asyncio.run(run_evals(filter_dataset=dataset))
    print_report(results)
    if output:
        write_report(results, path=str(output))
    else:
        write_report(results)

    failed = sum(1 for r in results if not r.passed)
    if failed:
        raise typer.Exit(1)


# ── datasets ───────────────────────────────────────────────────────────────────


@app.command("datasets")
def list_datasets():
    """List all uploaded datasets."""
    with _client() as client:
        _check_api(client)
        r = client.get("/api/datasets")
        r.raise_for_status()

    ds_list = r.json().get("datasets", [])
    if not ds_list:
        console.print("[yellow]No datasets yet.[/yellow]")
        console.print("Upload one with: python -m cli.main ingest <file.csv>")
        return

    t = Table(
        "ID",
        "Name",
        "Rows",
        "Cols",
        "Format",
        "Created",
        box=box.SIMPLE_HEAD,
        header_style="bold cyan",
    )
    for ds in ds_list:
        t.add_row(
            ds["id"][:8] + "…",
            ds["name"],
            f"{ds.get('row_count', '?'):,}" if ds.get("row_count") else "?",
            str(ds.get("column_count", "?")),
            ds.get("file_format", "?").upper(),
            ds.get("created_at", "")[:10],
        )
    console.print(t)


# ── status ─────────────────────────────────────────────────────────────────────


@app.command()
def status():
    """Check API health and print configuration."""
    with _client() as client:
        try:
            r = client.get("/api/health")
            r.raise_for_status()
            h = r.json()
        except Exception as e:
            err.print(f"API unreachable at {_api_url()}: {e}")
            raise typer.Exit(1) from None

    console.print(
        Panel(
            f"[green]●[/green] API is up\n"
            f"  URL:     {_api_url()}\n"
            f"  Version: {h.get('version', '?')}\n"
            f"  LLM:     {h.get('llm_provider', '?')} / {h.get('llm_model', '?')}\n"
            f"  Mode:    {'[green]live[/green]' if h.get('llm_live') else '[yellow]stub[/yellow]'}\n"
            f"  Time:    {h.get('timestamp', '?')}",
            title="[bold]MetricAnchor Status[/bold]",
            border_style="green",
        )
    )


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()
