#!/usr/bin/env python3
# download_audios.py — self-contained download+extract for VoxPopuli

import argparse
import os
import tarfile
from pathlib import Path

from tqdm import tqdm
from torch.hub import download_url_to_file

from voxpopuli import LANGUAGES, LANGUAGES_V2, YEARS, DOWNLOAD_BASE_URL


def get_args():
    parser = argparse.ArgumentParser(
        description="Download and extract VoxPopuli audio tarballs"
    )
    parser.add_argument(
        "--root", "-r", type=str, required=True,
        help="Base directory under which 'raw_audios/' will be created"
    )
    parser.add_argument(
        "--subset", "-s", type=str, required=True,
        choices=["400k", "100k", "10k", "asr"] + LANGUAGES + LANGUAGES_V2,
        help="Which language subset or size to download"
    )
    return parser.parse_args()


def download_url(url: str, dest_dir: str, filename: str) -> Path:
    """
    Download `url` into `dest_dir/filename` using torch.hub helper.
    Returns the Path to the downloaded file.
    """
    os.makedirs(dest_dir, exist_ok=True)
    out_path = Path(dest_dir) / filename
    download_url_to_file(url, str(out_path))
    return out_path


def extract_archive(archive_path: Path, dest_dir: str) -> None:
    """
    Extract the .tar archive at `archive_path` into `dest_dir`.
    """
    with tarfile.open(str(archive_path), "r") as tar:
        tar.extractall(path=dest_dir)


def download(args):
    # Construct list of URLs based on subset
    if args.subset in LANGUAGES_V2:
        langs = [args.subset.split("_")[0]]
        years = YEARS + [f"{y}_2" for y in YEARS]
    elif args.subset in LANGUAGES:
        langs = [args.subset]
        years = YEARS
    else:
        langs = {
            "400k": LANGUAGES,
            "100k": LANGUAGES,
            "10k": LANGUAGES,
            "asr": ["original"]
        }[args.subset]
        years = {
            "400k": YEARS + [f"{y}_2" for y in YEARS],
            "100k": YEARS,
            "10k": [2019, 2020],
            "asr": YEARS
        }[args.subset]

    url_list = [
        f"{DOWNLOAD_BASE_URL}/audios/{lang}_{year}.tar"
        for lang in langs for year in years
    ]

    raw_dir = Path(args.root) / "raw_audios"
    print(f"{len(url_list)} files to download into '{raw_dir}'")

    for url in tqdm(url_list, unit="file"):
        fname = Path(url).name
        tar_path = download_url(url, str(raw_dir), fname)
        extract_archive(tar_path, str(raw_dir))
        tar_path.unlink()  # remove .tar after extraction


def main():
    args = get_args()
    download(args)


if __name__ == "__main__":
    main()
