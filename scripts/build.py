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
from pathlib import Path


def check_python():
    if sys.version_info.major < 3 or sys.version_info.minor < 9:
        print("请使用 python-3.9 以上版本进行打包！（推荐使用 python-3.10）")
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
        # 没有就现装
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

def run_nuitka_build():
    os.chdir("../build")
    build_command = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--plugin-enable=pyside6",
        "-o", "app_main",
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
        # 使用pefile提高Windows下的处理速度
        build_command.append("--experimental=use_pefile")

        # 注意：在 python-3.13-windows 环境中，nuitka 目前仅支持使用 MSVC 打包
        if sys.version_info.minor >= 13:
            build_command.append("--msvc=latest")

        if os.path.exists(icon_paths["win32"]):
            build_command.append(f"--windows-icon-from-ico={icon_paths['win32']}")
        else:
            print(f"警告：未找到Windows图标文件 {icon_paths['win32']}")

    elif sys.platform == "linux":
        if os.path.exists(icon_paths["linux"]):
            build_command.append(f"--linux-icon={icon_paths['linux']}")
        else:
            print(f"警告：未找到Linux图标文件 {icon_paths['linux']}")

    elif sys.platform == "darwin":
        build_command.append("--macos-create-app-bundle")    # 创建 MacOS 应用包
        if os.path.exists(icon_paths["darwin"]):
            build_command.append(f"--macos-icon={icon_paths['darwin']}")
        else:
            print(f"警告：未找到macOS图标文件 {icon_paths['darwin']}")

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
        print("错误：找不到打包后的启动器文件，"
              "这可能是因为cargo构建启动器失败了。\n"
              "建议您检查自己的构建环境然后重试")
        sys.exit(1)
    exe_path.copy(Path("../build/"))

def build():
    check_python()
    find_nuitka()
    run_nuitka_build()
    run_launcher_build()

if __name__ == "__main__":
    build()