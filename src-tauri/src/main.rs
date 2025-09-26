// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri_plugin_log::log;

fn main() {
    log::info!("Starting SwarmClone Desktop App");
    swarmclone_desktop_app_lib::run()
}
