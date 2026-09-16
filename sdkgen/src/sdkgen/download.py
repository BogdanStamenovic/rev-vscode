"""Downloads (or reuses a cache of) the FTC SDK -sources.jar and .aar for
each artifact from Maven Central, and extracts the sources jars.

Cache layout (gitignored, see sdkgen/.gitignore):
  <cache_dir>/<Artifact>-<version>-sources.jar
  <cache_dir>/<Artifact>-<version>.aar
  <cache_dir>/src/<Artifact>/...            (extracted sources jar contents)
"""
from __future__ import annotations

import sys
import urllib.request
import zipfile
from pathlib import Path

ARTIFACTS = [
    "RobotCore", "Hardware", "FtcCommon", "OnBotJava",
    "RobotServer", "Blocks", "Inspection", "Vision",
]

MAVEN_BASE = "https://repo1.maven.org/maven2/org/firstinspires/ftc"


def _maven_url(artifact: str, version: str, suffix: str) -> str:
    return f"{MAVEN_BASE}/{artifact}/{version}/{artifact}-{version}{suffix}"


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"sdkgen: downloading {url}", file=sys.stderr)
    with urllib.request.urlopen(url) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def ensure_sdk_cache(cache_dir: Path, version: str) -> tuple[dict[str, Path], list[Path]]:
    """Returns (artifact -> extracted src dir, list of .aar paths)."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    src_root = cache_dir / "src"
    artifact_src_dirs: dict[str, Path] = {}
    aar_paths: list[Path] = []

    for artifact in ARTIFACTS:
        sources_jar = cache_dir / f"{artifact}-{version}-sources.jar"
        aar = cache_dir / f"{artifact}-{version}.aar"
        extracted_dir = src_root / artifact

        if not sources_jar.exists():
            _download(_maven_url(artifact, version, "-sources.jar"), sources_jar)
        if not aar.exists():
            try:
                _download(_maven_url(artifact, version, ".aar"), aar)
            except Exception as exc:  # noqa: BLE001
                print(f"sdkgen: could not fetch {aar.name} (display names may fall back "
                      f"to humanized xmlTag): {exc}", file=sys.stderr)

        if not extracted_dir.exists() or not any(extracted_dir.rglob("*.java")):
            extracted_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(sources_jar) as zf:
                for member in zf.namelist():
                    if member.endswith(".java"):
                        zf.extract(member, extracted_dir)

        artifact_src_dirs[artifact] = extracted_dir
        if aar.exists():
            aar_paths.append(aar)

    return artifact_src_dirs, aar_paths
