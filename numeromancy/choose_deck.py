import os
import shutil
from pathlib import Path

def create_eval_decks():
    # Define the decklists directory
    decklists_dir = Path("../data/decklists")

    # Create the eval_decks directory beside decklists_dir
    eval_decks_dir = Path("../data/eval_decks")
    eval_decks_dir.mkdir(exist_ok=True)

    # Iterate over all directories in decklists_dir
    for archetype_dir in decklists_dir.iterdir():
        if archetype_dir.is_dir():
            # Create a directory in eval_decks with the same name
            eval_archetype_dir = eval_decks_dir / archetype_dir.name
            eval_archetype_dir.mkdir(exist_ok=True)

            # Get the first file from each subdirectory
            for sub_dir in archetype_dir.iterdir():
                if sub_dir.is_dir():
                    # Get the first file in the subdirectory
                    first_file = None
                    for file in sub_dir.iterdir():
                        if file.is_file():
                            first_file = file
                            break

                    # Copy the first file to eval_decks directory
                    if first_file:
                        destination = eval_archetype_dir / first_file.name
                        shutil.copy2(first_file, destination)
                        print(f"Copied {first_file} to {destination}")

if __name__ == "__main__":
    create_eval_decks()
