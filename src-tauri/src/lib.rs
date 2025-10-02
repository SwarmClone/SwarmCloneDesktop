// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use serde::{Deserialize, Serialize};
use tauri::tray::TrayIconBuilder;
use tauri::menu::{Menu, MenuItem};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::sync::Arc;
use tauri::Manager;
use tokio::sync::RwLock;

lazy_static::lazy_static! {
    static ref CONFIG_CACHE: Arc<RwLock<Option<AppConfig>>> = Arc::new(RwLock::new(None));
}

#[derive(Serialize, Deserialize, Clone)]
struct AppConfig {
    configs: HashMap<String, String>,
}

#[tauri::command]
async fn get_config(key: &str) -> Result<String, String> {
    // 先从缓存中读取
    {
        let cache = CONFIG_CACHE.read().await;
        if let Some(ref config) = *cache {
            return Ok(config.configs.get(key).cloned().unwrap_or_default());
        }
    }

    // 缓存未命中，从文件读取
    let config_path = get_config_path();

    if config_path.exists() {
        match fs::read_to_string(&config_path) {
            Ok(content) => {
                match serde_json::from_str::<AppConfig>(&content) {
                    Ok(config) => {
                        // 更新缓存
                        {
                            let mut cache = CONFIG_CACHE.write().await;
                            *cache = Some(config.clone());
                        }
                        Ok(config.configs.get(key).cloned().unwrap_or_default())
                    }
                    Err(_) => Ok(String::new()),
                }
            }
            Err(_) => Ok(String::new()),
        }
    } else {
        Ok(String::new())
    }
}

#[tauri::command]
async fn set_config(key: &str, value: &str) -> Result<(), String> {
    let config_path = get_config_path();

    // 确保配置目录存在
    if let Some(parent) = config_path.parent() {
        fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    }

    // 读取现有配置或创建新配置
    let mut app_config = {
        let mut cache = CONFIG_CACHE.write().await;
        if let Some(ref mut cached_config) = *cache {
            cached_config.clone()
        } else {
            if config_path.exists() {
                match fs::read_to_string(&config_path) {
                    Ok(content) => {
                        serde_json::from_str::<AppConfig>(&content)
                            .unwrap_or_else(|_| AppConfig {
                                configs: HashMap::new(),
                            })
                    }
                    Err(_) => AppConfig {
                        configs: HashMap::new(),
                    },
                }
            } else {
                AppConfig {
                    configs: HashMap::new(),
                }
            }
        }
    };

    // 更新配置
    app_config.configs.insert(key.to_string(), value.to_string());

    // 保存到文件
    let json = serde_json::to_string(&app_config).map_err(|e| e.to_string())?;
    fs::write(&config_path, json).map_err(|e| e.to_string())?;

    // 更新缓存
    {
        let mut cache = CONFIG_CACHE.write().await;
        *cache = Some(app_config);
    }

    Ok(())
}

fn get_config_path() -> PathBuf {
    // 保存到用户目录/.swarmclone/config.json
    if let Some(home_dir) = dirs::home_dir() {
        home_dir.join(".swarmclone").join("config.json")
    } else {
        PathBuf::from(".swarmclone").join("config.json")
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let open_i = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;

            let menu = Menu::with_items(app, &[&quit_i, &open_i])?;

            let Some(window) = app.get_webview_window("main") else {
                return Err("Failed to get main window".into());
            };

            let _tray = TrayIconBuilder::new()
                .icon(app.default_window_icon().unwrap().clone())
                .menu(&menu)
                .show_menu_on_left_click(false)
                .on_menu_event(move |app, event| match event.id.as_ref() {
                    "quit" => {
                        if let Some(window) = app.get_window("main") {
                            window.close().unwrap();
                        }
                    }
                    "show" => {
                        window.show().unwrap();
                    }
                    _ => {
                        println!("menu item {:?} not handled", event.id);
                    }
                })
                .build(app)?;
            Ok(())
        })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            get_config,
            set_config
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
