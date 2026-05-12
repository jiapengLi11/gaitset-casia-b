import argparse
import tarfile
import zipfile
from pathlib import Path

import py7zr
import rarfile


def extract_zip(file_path: Path, output_dir: Path) -> bool:
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"Extracted ZIP: {file_path}")
        return True
    except Exception as exc:
        print(f"Failed to extract ZIP {file_path}: {exc}")
        return False


def extract_tar(file_path: Path, output_dir: Path) -> bool:
    try:
        with tarfile.open(file_path, "r:*") as tar_ref:
            tar_ref.extractall(output_dir)
        print(f"Extracted TAR: {file_path}")
        return True
    except Exception as exc:
        print(f"Failed to extract TAR {file_path}: {exc}")
        return False


def extract_rar(file_path: Path, output_dir: Path) -> bool:
    try:
        with rarfile.RarFile(file_path) as rar_ref:
            rar_ref.extractall(output_dir)
        print(f"Extracted RAR: {file_path}")
        return True
    except Exception as exc:
        print(f"Failed to extract RAR {file_path}: {exc}")
        return False


def extract_7z(file_path: Path, output_dir: Path) -> bool:
    try:
        with py7zr.SevenZipFile(file_path, mode="r") as z_ref:
            z_ref.extractall(output_dir)
        print(f"Extracted 7Z: {file_path}")
        return True
    except Exception as exc:
        print(f"Failed to extract 7Z {file_path}: {exc}")
        return False


def batch_extract(input_dir: str, output_dir: str | None = None, create_subdirs: bool = True) -> None:
    input_path = Path(input_dir)
    output_path = input_path / "extracted" if output_dir is None else Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    zip_extensions = [".zip"]
    tar_extensions = [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2"]
    rar_extensions = [".rar"]
    sevenz_extensions = [".7z"]
    all_extensions = zip_extensions + tar_extensions + rar_extensions + sevenz_extensions

    total_files = 0
    success_files = 0

    for file_path in input_path.iterdir():
        if not file_path.is_file():
            continue
        if not any(str(file_path).lower().endswith(ext) for ext in all_extensions):
            continue

        total_files += 1
        file_output_dir = output_path / file_path.stem if create_subdirs else output_path
        file_output_dir.mkdir(parents=True, exist_ok=True)

        success = False
        if any(file_path.name.lower().endswith(ext) for ext in zip_extensions):
            success = extract_zip(file_path, file_output_dir)
        elif any(file_path.name.lower().endswith(ext) for ext in tar_extensions):
            success = extract_tar(file_path, file_output_dir)
        elif any(file_path.name.lower().endswith(ext) for ext in rar_extensions):
            success = extract_rar(file_path, file_output_dir)
        elif any(file_path.name.lower().endswith(ext) for ext in sevenz_extensions):
            success = extract_7z(file_path, file_output_dir)

        if success:
            success_files += 1

    print("\nBatch extraction complete.")
    print(f"Found {total_files} compressed files.")
    print(f"Successfully extracted {success_files} files.")
    print(f"Output directory: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch extract archives in a directory.")
    parser.add_argument("--input", "-i", required=True, help="Input directory path")
    parser.add_argument("--output", "-o", help="Output directory path")
    parser.add_argument("--no-subdirs", action="store_true", help="Do not create one subdirectory per archive")
    args = parser.parse_args()

    batch_extract(
        input_dir=args.input,
        output_dir=args.output,
        create_subdirs=not args.no_subdirs,
    )
