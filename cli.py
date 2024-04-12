import typer
from main import run_main

app = typer.Typer()


@app.command()
def start(
    env: str = typer.Option(..., help="Environment (dev/expr/stg1/prod)"),
    output_dir: str = typer.Option("runs/", help="Output directory for the test run"),
    summary_type: str = typer.Option(
        "all", help="Summary type: 'all', 'by_endpoint', 'by_cid'"
    ),
    config_path: str = typer.Option("", help="Path to the config.json file"),
):
    """Runs the API test tool with specified options."""
    run_main(env, output_dir, summary_type, config_path)


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
