"""Management command to backup recipes."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from my_recipes.backup import RecipeBackup


class Command(BaseCommand):
    help = "Backup recipes to a JSON file"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--ids",
            type=int,
            nargs="+",
            help="Recipe IDs to backup. If not specified, all recipes are backed up.",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Path to output JSON file. If not specified, creates a timestamped file.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            output_file = RecipeBackup.backup_recipes(
                recipe_ids=options.get("ids"),
                output_file=options.get("output"),
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backup created successfully: {output_file}"
                )
            )
        except Exception as e:
            raise CommandError(f"Backup failed: {str(e)}")
