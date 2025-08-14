import click
import difflib
from pathlib import Path

from super_replace.core.autonomous_replacer import super_replace_autonomous
from super_replace.utils.formatter import format_code_with_black, lint_code_with_ruff

@click.group()
def cli():
    """Super Replace: An intelligent code replacement tool."""
    pass

@cli.command()
@click.argument('target')
@click.argument('replacement')
@click.argument('code_string', required=False) # Optional code string argument
@click.option('--input-file', '-i', type=click.Path(exists=True, dir_okay=False, path_type=Path), help='Path to the input Python file.')
@click.option('--output-file', '-o', type=click.Path(dir_okay=False, path_type=Path), help='Path to the output file. If not provided, output is printed to stdout.')
@click.option('--functions', '-f', multiple=True, help='Specify functions to apply replacement within.')
@click.option('--scope', type=click.Choice(['local', 'global', 'class'], case_sensitive=False), default='local', help='Specify the scope for replacement.')
@click.option('--format', is_flag=True, help='Format the output code using Black.')
@click.option('--lint', is_flag=True, help='Lint the output code using Ruff and display issues.')
@click.option('--dry-run', is_flag=True, help='Show changes without modifying the file.')
def autonomous(
    target: str,
    replacement: str,
    code_string: str | None,
    input_file: Path | None,
    output_file: Path | None,
    functions: tuple,
    scope: str,
    format: bool,
    lint: bool,
    dry_run: bool
):
    """Perform autonomous (rule-based) code replacement.

    TARGET: The string to be replaced.
    REPLACEMENT: The string to replace with.
    CODE_STRING: The code string to modify. Use this OR --input-file.
    """
    if code_string and input_file:
        raise click.BadParameter("Cannot specify both CODE_STRING and --input-file.")
    if not (code_string or input_file):
        raise click.BadParameter("Must specify either CODE_STRING or --input-file.")

    original_code = ""
    if input_file:
        original_code = input_file.read_text()
    elif code_string:
        original_code = code_string

    context_rules = {'functions': list(functions), 'scope': scope}
    modified_code = super_replace_autonomous(original_code, target, replacement, context_rules)

    if format:
        modified_code = format_code_with_black(modified_code)

    if lint:
        lint_output = lint_code_with_ruff(modified_code)
        if lint_output:
            click.echo("\n--- Ruff Linting Issues ---")
            click.echo(lint_output)
            click.echo("---------------------------")
        else:
            click.echo("\n--- Ruff Linting: No issues found ---")

    if dry_run:
        click.echo("\n--- Dry Run: Proposed Changes (Diff) ---")
        diff = difflib.unified_diff(
            original_code.splitlines(keepends=True),
            modified_code.splitlines(keepends=True),
            fromfile='a/code',
            tofile='b/code'
        )
        click.echo(''.join(diff))
        click.echo("----------------------------------------")
    elif output_file:
        output_file.write_text(modified_code)
        click.echo(f"Modified code written to {output_file}")
    else:
        click.echo(modified_code)

if __name__ == '__main__':
    cli()