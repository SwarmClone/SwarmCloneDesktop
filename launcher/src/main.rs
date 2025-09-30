#![cfg_attr(windows, windows_subsystem = "windows")]
/**
 * SwarmClone Desktop
 *
 * Copyright (C) 2025 SwarmClone <https://github.com/SwarmClone> and contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the Eclipse Public License, Version 2.0 (EPL-2.0),
 * as published by the Eclipse Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Eclipse Public License 2.0 for more details.
 *
 * You should have received a copy of the Eclipse Public License 2.0
 * along with this program.  For the full text of the Eclipse Public License 2.0,
 * see <https://www.eclipse.org/legal/epl-2.0/>.
 */

extern crate core;

use chrono;
use std::fs::File;
use std::io::{BufReader, Read, Write};
use std::process::{exit, Command, Output};
use encoding_rs::GBK;
use encoding_rs_io::DecodeReaderBytesBuilder;
use sysinfo::{System};

#[cfg(windows)]
static PROGRAM_NAME: &str = r"main.dist\SwarmCloneDesktop.exe";

#[cfg(not(windows))]
static PROGRAM_NAME: &str = "./main.dist/SwarmCloneDesktop";


fn gbk_to_utf8(bytes: &[u8]) -> String {
    let decoder = DecodeReaderBytesBuilder::new()
        .encoding(Some(GBK))
        .build(bytes);
    let mut utf8 = String::new();
    BufReader::new(decoder).read_to_string(&mut utf8).unwrap();
    utf8
}

fn show_crash_dialog(file_path: &str)
{
    let text = format!("SwarmCloneDesktop主程序\n由于遇到意外或者无法解决的严重问题，现已崩溃。\n\n\
                                崩溃日志已生成：{}\n\n\
                                请检查日志并提交给软件维护人员。",
                       file_path);

    msgbox::create("错误",
                   &*text,
                   msgbox::IconType::Error).expect("Failed to create message box")
}

fn open_file_explorer(file_path: &str)
{
    let mut cmd = if cfg!(target_os = "windows") {
        let mut command = Command::new("explorer");
        command.arg(file_path);
        command
    } else if cfg!(target_os = "macos") {
        let mut command = Command::new("open");
        command.arg(file_path);
        command
    } else if cfg!(target_os = "linux") {
        let mut command = Command::new("xdg-open");
        command.arg(file_path);
        command
    } else {
        // 其他平台不支持，直接返回
        return;
    };

    match cmd.spawn() {
        Ok(_) => {},
        Err(_) => {
            // 忽略打开文件浏览器的错误，不影响主要功能
        }
    }
}


fn generate_crash_log(output: Output)
{
    std::fs::create_dir_all("logs").expect("failed to create logs directory");

    let current_time = chrono::Local::now().format("%Y%m%d%H%M%S");
    let current_time_text = chrono::Local::now().format("%Y年%m月%d日%H时%M分%S秒");

    let log_file = format!("logs\\crash_log_{}.log", current_time);

    // 获取绝对路径
    let current_dir = std::env::current_dir().expect("failed to get current directory");
    let log_file_abs_path = current_dir.join(&log_file);
    let log_file_abs_path_str = log_file_abs_path.to_string_lossy();

    show_crash_dialog(&log_file_abs_path_str);

    let mut file = File::create(&log_file).expect("failed to create file");
    let exit_code = output.status.code().unwrap_or(-1).to_string();
    let stdout = gbk_to_utf8(&output.stdout);
    let stderr = gbk_to_utf8(&output.stderr);

    writeln!(file, "应用程序 '{}' 于 {} 遇到意外发生且无法自行解决的严重错误，现在已经崩溃。\n\
            退出代码: {} \n\
            请将本日志提交给软件维护人员，方便我们解决问题。", PROGRAM_NAME, current_time_text,  exit_code).unwrap();

    writeln!(file, "--------------------").unwrap();

    writeln!(file, "{}", get_device_info()).unwrap();

    writeln!(file, "--------------------").unwrap();

    writeln!(file, "以下是该应用程序自启动到崩溃，输出的全部信息:\n\n{}\n{}", stdout, stderr).unwrap();

    open_file_explorer(&log_file_abs_path_str);
}


fn get_device_info() -> String {
    let mut info = String::new();
    let mut sys = System::new_all();
    sys.refresh_all();

    info.push_str(&format!("操作系统：{} {}\n", System::long_os_version().unwrap(), System::kernel_version().unwrap()));
    info.push_str(&format!("CPU型号：{}\n", sys.cpus()[0].brand()));
    info.push_str(&format!("CPU核心数量：{}\n", sys.cpus().len()));

    info.push_str("GPU信息：\n");
    match get_gpu_info() {
        Ok(gpu_info) => info.push_str(&gpu_info),
        Err(_) => info.push_str("无法获取GPU信息\n"),
    }

    info.push_str(&format!("总内存：{} GB\n", sys.total_memory() / 1024 / 1024 / 1024));
    info.push_str(&format!("已使用内存：{} GB", sys.used_memory() / 1024 / 1024 / 1024));

    info
}
fn get_gpu_info() -> Result<String, Box<dyn std::error::Error>> {
    let mut gpu_info = String::new();

    #[cfg(windows)]
    {
        // 在Windows上优先使用PowerShell获取GPU信息，因为wmic在新版本Windows中已被弃用
        let output = Command::new("powershell")
            .args([
                "-Command",
                "Get-WmiObject -Class Win32_VideoController | Select-Object -ExpandProperty Name"
            ])
            .output()?;

        if output.status.success() {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let lines: Vec<&str> = stdout
                .lines()
                .map(|line| line.trim())
                .filter(|line| !line.is_empty())
                .collect();

            if lines.is_empty() {
                gpu_info.push_str("  未检测到GPU设备\n");
            } else {
                for (i, gpu_name) in lines.iter().enumerate() {
                    gpu_info.push_str(&format!("  GPU {}: {}\n", i + 1, gpu_name));
                }
            }
        } else {
            // 备用方法：使用旧版wmic命令
            let backup_output = Command::new("wmic")
                .args(["path", "win32_videocontroller", "get", "name", "/value"])
                .output()?;

            if backup_output.status.success() {
                let stdout = String::from_utf8_lossy(&backup_output.stdout);
                let mut gpu_count = 1;
                for line in stdout.lines() {
                    if line.starts_with("Name=") {
                        let gpu_name = line.strip_prefix("Name=").unwrap_or(line).trim();
                        if !gpu_name.is_empty() {
                            gpu_info.push_str(&format!("  GPU {}: {}\n", gpu_count, gpu_name));
                            gpu_count += 1;
                        }
                    }
                }
                if gpu_count == 1 {
                    gpu_info.push_str("  未检测到GPU设备\n");
                }
            } else {
                gpu_info.push_str("  无法获取GPU详细信息\n");
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        // 在macOS上使用system_profiler获取GPU信息
        let output = Command::new("system_profiler")
            .args(["SPDisplaysDataType"])
            .output();

        match output {
            Ok(result) => {
                let stdout = String::from_utf8_lossy(&result.stdout);
                let mut gpu_count = 1;
                for line in stdout.lines() {
                    if line.contains("Chipset Model:") || line.contains("Graphics Chipset Model:") {
                        let gpu_name = line.split(':').nth(1).unwrap_or("").trim();
                        gpu_info.push_str(&format!("  GPU {}: {}\n", gpu_count, gpu_name));
                        gpu_count += 1;
                    }
                }
                if gpu_count == 1 {
                    gpu_info.push_str("  未检测到GPU设备\n");
                }
            }
            Err(_) => {
                gpu_info.push_str("  无法获取GPU详细信息\n");
            }
        }
    }

    #[cfg(all(unix, not(target_os = "macos")))]
    {
        // 在Linux上尝试使用lspci获取GPU信息
        let output = Command::new("lspci")
            .args(["-vnn"])
            .output()
            .or_else(|_| Command::new("lshw").args(["-class", "display"]).output());

        match output {
            Ok(result) => {
                let stdout = String::from_utf8_lossy(&result.stdout);
                let mut gpu_count = 1;
                for line in stdout.lines() {
                    if line.contains("VGA compatible controller") ||
                       line.contains("3D controller") ||
                       line.contains("Display") {
                        gpu_info.push_str(&format!("  GPU {}: {}\n", gpu_count, line.trim()));
                        gpu_count += 1;
                    }
                }
                if gpu_count == 1 {
                    gpu_info.push_str("  未检测到GPU设备\n");
                }
            }
            Err(_) => {
                gpu_info.push_str("  无法获取GPU详细信息\n");
            }
        }
    }

    if gpu_info.is_empty() {
        gpu_info.push_str("  无GPU信息可用\n");
    }

    Ok(gpu_info)
}


fn check_program_exist() {
    if !std::path::Path::new(PROGRAM_NAME).exists() {
        msgbox::create(
            "错误",
            "找不到 SwarmCloneDesktop 核心主程序，\n\n\
            这说明 SwarmCloneDesktop 程序文件已经损坏。\n\n\
            请您尝试重新安装来解决此问题",
            msgbox::IconType::Error
        ).expect("failed to show messagebox");
        exit(1);
    }
}

fn main() {
    check_program_exist();

    let output = Command::new(PROGRAM_NAME)
        .args([""])
        .output();

    match output {
        Ok(result) => {
            let exit_code = result.status.code().unwrap_or(0);
            let should_generate_crash_log = if result.status.success() {
                // 程序正常退出，不需要生成崩溃日志
                false
            } else {
                // 检查是否是正常的终止信号
                if cfg!(unix) {
                    // Unix/Linux/macOS 平台的正常终止信号
                    exit_code != 130 && exit_code != 137 && exit_code != 143
                } else {
                    // Windows平台
                    // Windows上被任务管理器结束通常返回非零但特定的退出代码
                    exit_code < 0 || (exit_code > 1 && exit_code < 128)
                }
            };

            if should_generate_crash_log {
                generate_crash_log(result);
            }
            exit(exit_code)
        },
        Err(e) => {
            if e.kind() == std::io::ErrorKind::NotFound {
                msgbox::create(
                    "错误",
                    "找不到 SwarmCloneDesktop 核心主程序，\n\n\
                    这说明 SwarmCloneDesktop 程序文件已经损坏。\n\n\
                    请您尝试重新安装来解决此问题",
                    msgbox::IconType::Error
                ).expect("failed to show messagebox");
            } else {
                msgbox::create(
                    "错误",
                    &format!("无法启动核心程序: {}。请检查程序文件权限或完整性。", e),
                    msgbox::IconType::Error
                ).expect("failed to show messagebox");
            }
            exit(1);
        }
    }
}
