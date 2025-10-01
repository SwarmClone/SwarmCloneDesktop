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
    let text = format!("SwarmCloneDesktop Main Program\nAn unexpected or unrecoverable error has occurred, and the program has crashed.\n\n\
                                Crash log generated: {}\n\n\
                                Please check the log and submit it to the software maintainers.",
                       file_path);

    msgbox::create("Error",
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
        // Other platforms not supported, return directly
        return;
    };

    match cmd.spawn() {
        Ok(_) => {},
        Err(_) => {
            // Ignore errors when opening file explorer,
            // does not affect main functionality
        }
    }
}


fn generate_crash_log(output: Output)
{
    std::fs::create_dir_all("logs").expect("failed to create logs directory");

    let current_time = chrono::Local::now().format("%Y%m%d%H%M%S");
    let current_time_text = chrono::Local::now().format("%Y-%m-%d %H:%M:%S");

    let log_file = format!("logs\\crash_log_{}.log", current_time);

    // Get absolute path
    let current_dir = std::env::current_dir().expect("failed to get current directory");
    let log_file_abs_path = current_dir.join(&log_file);
    let log_file_abs_path_str = log_file_abs_path.to_string_lossy();

    show_crash_dialog(&log_file_abs_path_str);

    let mut file = File::create(&log_file).expect("failed to create file");
    let exit_code = output.status.code().unwrap_or(-1).to_string();
    let stdout = gbk_to_utf8(&output.stdout);
    let stderr = gbk_to_utf8(&output.stderr);

    writeln!(file, "Application '{}' encountered an unexpected and unrecoverable error at {} and has crashed.\n\
            Exit code: {} \n\
            Please submit this log to the software maintainers to help us resolve the issue.", PROGRAM_NAME, current_time_text,  exit_code).unwrap();

    writeln!(file, "--------------------").unwrap();

    writeln!(file, "{}", get_device_info()).unwrap();

    writeln!(file, "--------------------").unwrap();

    writeln!(file, "Below is all the output information from this application from startup to crash:\n\n{}\n{}", stdout, stderr).unwrap();

    open_file_explorer(&log_file_abs_path_str);
}


fn get_device_info() -> String {
    let mut info = String::new();
    let mut sys = System::new_all();
    sys.refresh_all();

    info.push_str(&format!("Operating System: {} {}\n", System::long_os_version().unwrap(), System::kernel_version().unwrap()));
    info.push_str(&format!("CPU Model: {}\n", sys.cpus()[0].brand()));
    info.push_str(&format!("CPU Core Count: {}\n", sys.cpus().len()));

    info.push_str("GPU Information:\n");
    match get_gpu_info() {
        Ok(gpu_info) => info.push_str(&gpu_info),
        Err(_) => info.push_str("Unable to get GPU information\n"),
    }

    info.push_str(&format!("Total Memory: {} GB\n", sys.total_memory() / 1024 / 1024 / 1024));
    info.push_str(&format!("Used Memory: {} GB", sys.used_memory() / 1024 / 1024 / 1024));

    info
}
fn get_gpu_info() -> Result<String, Box<dyn std::error::Error>> {
    let mut gpu_info = String::new();

    #[cfg(windows)]
    {
        // On Windows, prefer using PowerShell to get GPU information
        // as wmic is deprecated in newer Windows versions
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
                gpu_info.push_str("  No GPU devices detected\n");
            } else {
                for (i, gpu_name) in lines.iter().enumerate() {
                    gpu_info.push_str(&format!("  GPU {}: {}\n", i + 1, gpu_name));
                }
            }
        } else {
            // Fallback method: use the old wmic command
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
                    gpu_info.push_str("  No GPU devices detected\n");
                }
            } else {
                gpu_info.push_str("  Unable to get detailed GPU information\n");
            }
        }
    }

    #[cfg(target_os = "macos")]
    {
        // On macOS, use system_profiler to get GPU information
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
                    gpu_info.push_str("  No GPU devices detected\n");
                }
            }
            Err(_) => {
                gpu_info.push_str("  Unable to get detailed GPU information\n");
            }
        }
    }

    #[cfg(all(unix, not(target_os = "macos")))]
    {
        // On Linux, try to use lspci to get GPU information
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
                    gpu_info.push_str("  No GPU devices detected\n");
                }
            }
            Err(_) => {
                gpu_info.push_str("  Unable to get detailed GPU information\n");
            }
        }
    }

    if gpu_info.is_empty() {
        gpu_info.push_str("  No GPU information available\n");
    }

    Ok(gpu_info)
}


fn check_program_exist() {
    if !std::path::Path::new(PROGRAM_NAME).exists() {
        msgbox::create(
            "Error",
            "Cannot find the SwarmCloneDesktop core program.\n\n\
            This indicates that the SwarmCloneDesktop program files are corrupted.\n\n\
            Please try reinstalling to resolve this issue.",
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
                // Program exited normally, no need to generate crash log
                false
            } else {
                // Check if it's a normal termination signal
                if cfg!(unix) {
                    // Normal termination signals on Unix/Linux/macOS platforms
                    exit_code != 130 && exit_code != 137 && exit_code != 143
                } else {
                    // Windows platform
                    // On Windows, being terminated by Task Manager usually returns
                    // a non-zero but specific exit code
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
                    "Error",
                    "Cannot find the SwarmCloneDesktop core program.\n\n\
                    This indicates that the SwarmCloneDesktop program files are corrupted.\n\n\
                    Please try reinstalling to resolve this issue.",
                    msgbox::IconType::Error
                ).expect("failed to show messagebox");
            } else {
                msgbox::create(
                    "Error",
                    &format!("Unable to start core program: {}. Please check program file permissions or integrity.", e),
                    msgbox::IconType::Error
                ).expect("failed to show messagebox");
            }
            exit(1);
        }
    }
}
