#!/usr/bin/env python3

import typer
import os
from main import run_test_tool

app = typer.Typer()


def validate_inputs(
    env: str, config_path: str, output_dir: str, summary_type: str, skip_pause: bool
):
    if env not in ["dev", "expr", "stg1", "prod"]:
        raise ValueError(
            "Invalid environment. Please choose one of 'dev', 'stg1', 'expr', or 'prod'."
        )
    if config_path and not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' does not exist.")
    if summary_type not in ["all", "endpoint", "cid"]:
        raise ValueError(
            "Invalid summary type. Please choose 'all', 'endpoint', or 'cid'."
        )
    if not isinstance(skip_pause, bool):
        raise ValueError("skip_pause must be a boolean value.")


@app.callback()
def start(
    env: str = typer.Option("", help="Environment (dev/expr/stg1/prod)"),
    config_path: str = typer.Option("", help="Path to the config.json file"),
    output_dir: str = typer.Option("", help="Output directory for the test run"),
    summary_type: str = typer.Option(
        "endpoint", help="Summary type: 'all', 'endpoint', 'cid'"
    ),
    skip_pause: bool = typer.Option(False, help="Do not pause in between runs"),
):
    """Runs the API test tool with specified options."""
    validate_inputs(env, config_path, output_dir, summary_type, skip_pause)
    run_test_tool(env, config_path, output_dir, summary_type, skip_pause)


@app.command()
def setup_env(
    username: str = typer.Option(..., prompt=True, help="Username for the .env file"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password for the .env file"
    ),
):
    """Creates an .env file with the provided username and password."""
    with open(".env", "w") as f:
        f.write(f"USERNAME={username}\n")
        f.write(f"PASSWORD={password}\n")
    typer.echo("Environment variables saved to .env file.")


if __name__ == "__main__":
    app()
