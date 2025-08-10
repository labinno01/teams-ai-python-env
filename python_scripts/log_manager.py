import typer
import os
from datetime import datetime, timedelta
import glob
import zipfile
import re

from .utils.display import ICON_SUCCESS, ICON_ERROR, ICON_INFO
from .utils.logger import LOG_DIR, LOG_FILE, ensure_log_dir_exists

app = typer.Typer(help="Manages log files for the project, including rotation, compression, and cleanup.")

@app.command()
def rotate():
    """
    Rotates the current log file by renaming it with a timestamp.
    """
    ensure_log_dir_exists()
    if not os.path.exists(LOG_FILE):
        typer.echo(f"{ICON_INFO} Le fichier de log actuel ({LOG_FILE}) n'existe pas. Aucune rotation nécessaire.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rotated_log_file = os.path.join(LOG_DIR, f"execution_log_{timestamp}.jsonl")

    try:
        os.rename(LOG_FILE, rotated_log_file)
        typer.echo(f"{ICON_SUCCESS} Fichier de log rotaté : {LOG_FILE} -> {rotated_log_file}")
    except OSError as e:
        typer.echo(f"{ICON_ERROR} Erreur lors de la rotation du log : {e}")
        raise typer.Exit(code=1)

@app.command()
def compress(
    days_old: int = typer.Option(7, "--days-old", "-d", help="Compress log files older than this many days.")
):
    """
    Compresses old .jsonl log files into zip archives.
    """
    ensure_log_dir_exists()
    cutoff_date = datetime.now() - timedelta(days=days_old)

    log_files = glob.glob(os.path.join(LOG_DIR, "execution_log_*.jsonl"))
    compressed_count = 0

    for log_file in log_files:
        try:
            # Extract timestamp from filename (e.g., execution_log_2023-10-27_12-30-00.jsonl)
            filename = os.path.basename(log_file)
            match = re.match(r"execution_log_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.jsonl", filename)
            if not match:
                continue
            
            file_timestamp_str = match.group(1)
            file_date = datetime.strptime(file_timestamp_str, "%Y-%m-%d_%H-%M-%S")

            if file_date < cutoff_date:
                zip_filename = log_file.replace(".jsonl", ".zip")
                with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(log_file, os.path.basename(log_file))
                os.remove(log_file)
                typer.echo(f"{ICON_SUCCESS} Fichier compressé : {log_file} -> {zip_filename}")
                compressed_count += 1
        except Exception as e:
            typer.echo(f"{ICON_ERROR} Erreur lors de la compression de {log_file} : {e}")

    if compressed_count == 0:
        typer.echo(f"{ICON_INFO} Aucun fichier de log à compresser plus ancien que {days_old} jours.")
    else:
        typer.echo(f"{ICON_SUCCESS} {compressed_count} fichier(s) de log compressé(s).")

@app.command()
def cleanup(
    days_to_keep: int = typer.Option(30, "--days-to-keep", "-k", help="Delete archives older than this many days.")
):
    """
    Deletes old log archives (zip files) older than a specified number of days.
    """
    ensure_log_dir_exists()
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    archive_files = glob.glob(os.path.join(LOG_DIR, "*.zip"))
    deleted_count = 0

    for archive_file in archive_files:
        try:
            # Extract timestamp from filename (e.g., execution_log_2023-10-27_12-30-00.zip)
            filename = os.path.basename(archive_file)
            match = re.match(r"execution_log_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.zip", filename)
            if not match:
                continue
            
            file_timestamp_str = match.group(1)
            file_date = datetime.strptime(file_timestamp_str, "%Y-%m-%d_%H-%M-%S")

            if file_date < cutoff_date:
                os.remove(archive_file)
                typer.echo(f"{ICON_SUCCESS} Archive supprimée : {archive_file}")
                deleted_count += 1
        except Exception as e:
            typer.echo(f"{ICON_ERROR} Erreur lors de la suppression de {archive_file} : {e}")

    if deleted_count == 0:
        typer.echo(f"{ICON_INFO} Aucune archive de log à supprimer plus ancienne que {days_to_keep} jours.")
    else:
        typer.echo(f"{ICON_SUCCESS} {deleted_count} archive(s) de log supprimée(s).")

@app.command(name="run-maintenance")
def run_maintenance_command(
    days_old_compress: int = typer.Option(7, "--compress-days-old", "-d", help="Compress log files older than this many days."),
    days_to_keep_cleanup: int = typer.Option(30, "--cleanup-days-to-keep", "-k", help="Delete archives older than this many days.")
):
    """
    Runs a full log maintenance cycle: rotate, compress, and cleanup.
    """
    typer.echo(f"{ICON_INFO} Démarrage du cycle de maintenance des logs...")
    rotate()
    compress(days_old=days_old_compress)
    cleanup(days_to_keep=days_to_keep_cleanup)
    typer.echo(f"{ICON_SUCCESS} Cycle de maintenance des logs terminé.")

if __name__ == "__main__":
    app()
