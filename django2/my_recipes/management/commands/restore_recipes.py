"""Management command to restore recipes."""

from typing import Any

from django.core.management.base import BaseCommand, CommandError

from my_recipes.backup import RecipeBackup


class Command(BaseCommand):
    help = "Restore recipes from a JSON backup file"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "input_file",
            type=str,
            help="Path to the JSON backup file to restore",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing recipes with the same name",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            recipes = RecipeBackup.restore_recipes(
                input_file=options["input_file"],
                overwrite=options.get("overwrite", False),
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully restored {len(recipes)} recipes:"
                )
            )
            for recipe in recipes:
                self.stdout.write(f"  - {recipe.name}")
        except FileNotFoundError:
            raise CommandError(
                f"Backup file not found: {options['input_file']}"
            )
        except ValueError as e:
            raise CommandError(f"Restore failed: {str(e)}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {str(e)}")
