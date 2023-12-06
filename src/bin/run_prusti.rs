use std::env;
use std::fs;
use std::path::{Path, PathBuf};



// cite https://github.com/viperproject/prusti-dev/blob/2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs
fn setup_prusti(name: &str, version:&str) {
    let dirname = format!("/tmp/{name}-{version}");

    let cwd = std::env::current_dir().unwrap();
    let target = if cfg!(debug_assertions) {
        "debug"
    } else {
        "release"
    };

    let prusti = cwd.join(
        ["target", target, "prusti-release-macos", "cargo-prusti"]
            .iter()
            .collect::<PathBuf>(),
    );

    let env_root_path = fs::read_to_string("./.env").unwrap();
    let _ = env::set_current_dir(Path::new(env_root_path.as_str()));
    let z3_path = env::current_dir().unwrap().join("viper_tools/z3/bin/z3");
    env::set_var("Z3_EXE", z3_path);
    let host_viper_home = env::current_dir().unwrap().join("viper_tools/backends");
    env::set_var("viper_home",  host_viper_home);
    let host_java_home = env::var("JAVA_HOME")
        .ok()
        .map(|s| s.into())
        .or_else(find_java_home)
        .expect("Please set JAVA_HOME");
 env::set_var("java_home",  host_java_home);


    let pwd_path = env::current_dir().unwrap();
    let cache = pwd_path.clone().join("cache");
    let tmp_path = pwd_path.clone().join("log");

    let _cmd = std::process::Command::new(prusti)
        .env("PRUSTI_LOG_DIR", tmp_path.as_os_str())
        .env("PRUSTI_CACHE_PATH", cache)
        .env("PRUSTI_ENABLE_CACHE", "true")
        .env("PRUSTI_SKIP_UNSUPPORTED_FEATURES", "true")
        // .env("PRUSTI_DUMP_VIPER_PROGRAM", "true")
        // .env("PRUSTI_DUMP_PATH_CTXT_IN_DEBUG_INFO", "true")
        // .env("PRUSTI_CHECK_PANICS", "true")
        // .env("PRUSTI_DUMP_DEBUG_INFO", "true")
        // .env("PRUSTI_LOG", "info")
        .current_dir(&dirname)
        .status()
        .expect("failed to run prusti");

        // assert!(cmd.success());
}

/// Find the Java home directory
pub fn find_java_home() -> Option<PathBuf> {
    std::process::Command::new("java")
        .arg("-XshowSettings:properties")
        .arg("-version")
        .output()
        .ok()
        .and_then(|output| {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            for line in stdout.lines().chain(stderr.lines()) {
                if line.contains("java.home") {
                    let pos = line.find('=').unwrap() + 1;
                    let path = line[pos..].trim();
                    return Some(PathBuf::from(path));
                }
            }
            None
        })
}

fn main() {
    let args: Vec<String> = env::args().collect();
    for arg in args {

        if arg.contains(".txt") {
            let mut crate_name = arg.replace("crate:", "");
            crate_name = crate_name.replace(".txt", "");
            let names: Vec<&str> = crate_name.split("-").collect();
            
            let mut name = names[0].to_owned();
            if names.len() > 2 {
                let mut i = 1;

                while i < names.len() - 1 {
                    name = name + "-" + names[i];
                    i += 1
                }
            }
            let name_str =name.as_str();
            let ver = names[1];

            setup_prusti(name_str, ver)
        }
    }
}


