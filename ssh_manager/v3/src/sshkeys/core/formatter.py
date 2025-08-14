import click

class FrenchHelpFormatter(click.HelpFormatter):
    def write_usage(self, prog, args="", prefix="Usage: "):
        super().write_usage(prog, args, prefix="Utilisation : ")

    def write_help_text(self, *args, **kwargs):
        super().write_help_text(*args, **kwargs)
        self.write_text(self.getvalue().replace("Show this message and exit.", "Affiche ce message d'aide et quitte."))
