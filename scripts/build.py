# SwarmClone Desktop
#
# Copyright (C) 2025 SwarmClone <https://github.com/SwarmClone> and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Eclipse Public License, Version 2.0 (EPL-2.0),
# as published by the Eclipse Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Eclipse Public License 2.0 for more details.
#
# You should have received a copy of the Eclipse Public License 2.0
# along with this program.  For the full text of the Eclipse Public License 2.0,
# see <https://www.eclipse.org/legal/epl-2.0/>.

import os
import subprocess
import sys
import shutil
from pathlib import Path


def check_python():
    if sys.version_info.major < 3 or sys.version_info.minor < 9:
        print("Please use Python 3.9 or higher for packaging! (Python 3.10 recommended)")
        sys.exit(1)

def find_nuitka():
    where_nuitka = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "show",
            "nuitka",
        ]
    )
    if where_nuitka.returncode != 0:
        # Install if not found
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "nuitka",
            ]
        )
def install_dependencies():
    install_command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "-r",
        "../requirements.txt",
    ]
    subprocess.run(install_command, check=True)

def run_nuitka_build():
    os.chdir("../build")
    build_command = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--plugin-enable=pyside6",
        "-o", "SwarmCloneDesktop",
        "../src/main.py",
        "--remove-output",
        "--no-pyi-file",
        "--prefer-source-code",
        "--assume-yes-for-downloads",
        "--disable-console",
        "--lto=yes",
        "--jobs=8",
    ]

    icon_paths = {
        "win32": "../src/assets/icons/app.ico",
        "linux": "../src/assets/icons/app.png",
        "darwin": "../src/assets/icons/app.icns"
    }

    if sys.platform == "win32":
        # Use pefile to improve processing speed on Windows
        build_command.append("--experimental=use_pefile")

        # Note: In python-3.13-windows environment, nuitka currently only supports packaging with MSVC
        if sys.version_info.minor >= 13:
            build_command.append("--msvc=latest")

        if os.path.exists(icon_paths["win32"]):
            build_command.append(f"--windows-icon-from-ico={icon_paths['win32']}")
        else:
            print(f"Warning: Windows icon file not found {icon_paths['win32']}")

    elif sys.platform == "linux":
        if os.path.exists(icon_paths["linux"]):
            build_command.append(f"--linux-icon={icon_paths['linux']}")
        else:
            print(f"Warning: Linux icon file not found {icon_paths['linux']}")

    elif sys.platform == "darwin":
        build_command.append("--macos-create-app-bundle")    # Create MacOS application bundle
        if os.path.exists(icon_paths["darwin"]):
            build_command.append(f"--macos-app-icon={icon_paths['darwin']}")
        else:
            print(f"Warning: macOS icon file not found {icon_paths['darwin']}")

    subprocess.run(build_command, check=True)

def run_launcher_build():
    os.chdir("../launcher")
    subprocess.run(
        [
            "cargo",
            "build",
            "--release"
        ]
    )

    if sys.platform == "win32":
        exe_path = Path("../launcher/target/release/SwarmCloneDesktop.exe")
    else:
        exe_path = Path("../launcher/target/release/SwarmCloneDesktop")

    if not exe_path.exists():
        print("Error: Cannot find the packaged launcher file, "
              "this may be because the cargo launcher build failed.\n"
              "Please check your build environment and try again")
        sys.exit(1)

    shutil.copy(exe_path, Path("../build/"))

def build():
    check_python()
    install_dependencies()
    find_nuitka()
    run_nuitka_build()
    run_launcher_build()

if __name__ == "__main__":
    build()
