use std::process::Command;
use std::env;
use std::path::Path;

fn main() {
    #[cfg(windows)]
    {
        let rc_path = "res/windows.rc";

        if !Path::new(rc_path).exists() {
            println!("cargo:warning=Resource file not found: {}", rc_path);
            return;
        }

        let icon_path = "assets/icon.ico";
        if !Path::new(icon_path).exists() {
            println!("cargo:warning=Icon file not found: {}", icon_path);
        }

        let out_path = env::var("OUT_DIR").unwrap();
        let res_path = format!("{}/resource.res", out_path);

        let rc_exe = "./rc.exe";
        let current_dir = env::current_dir().unwrap();
        let rc_exe_path = current_dir.join("rc.exe");

        if rc_exe_path.exists() {
            let abs_rc_exe = rc_exe_path.to_string_lossy();
            let abs_rc_path = current_dir.join(rc_path);
            let abs_rc_path_str = abs_rc_path.to_string_lossy();

            println!("cargo:warning=Compiling resources with:");
            println!("cargo:warning=RC exe: {}", abs_rc_exe);
            println!("cargo:warning=RC file: {}", abs_rc_path_str);
            println!("cargo:warning=Output: {}", res_path);

            let output = Command::new(&*abs_rc_exe)
                .args(&["/Fo", &res_path, &*abs_rc_path_str])
                .output();

            match output {
                Ok(result) => {
                    let stdout = String::from_utf8_lossy(&result.stdout);
                    let stderr = String::from_utf8_lossy(&result.stderr);

                    if !stdout.is_empty() {
                        println!("cargo:warning=RC stdout: {}", stdout);
                    }
                    if !stderr.is_empty() {
                        println!("cargo:warning=RC stderr: {}", stderr);
                    }

                    if !result.status.success() {
                        println!("cargo:warning=Resource compilation failed, but continuing build...");
                    } else {
                        println!("cargo:rustc-link-arg={}", res_path);
                    }
                }
                Err(e) => {
                    println!("cargo:warning=Failed to execute resource compiler: {}, skipping...", e);
                }
            }
        } else {
            println!("cargo:warning=Local rc.exe not found. Skipping resource compilation.");
        }
    }
}
