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
    // let host_viper_home = env::current_dir().unwrap().join("viper_tools/backends");
    // env::set_var("viper_home",  host_viper_home);

    let pwd_path = env::current_dir().unwrap();
    let cache = pwd_path.clone().join("cache");

    let cmd = std::process::Command::new(prusti)
        // .env("PRUSTI_LOG_DIR", log.as_os_str())
        //.env("PRUSTI_DUMP_DEBUG_INFO", "true")
        .env("PRUSTI_CACHE_PATH", cache)
        .env("PRUSTI_ENABLE_CACHE", "true")
        .env("PRUSTI_SKIP_UNSUPPORTED_FEATURES", "true")
        // .env("PRUSTI_LOG", "info")
        .current_dir(&dirname)
        .status()
        .expect("failed to run prusti");

        // assert!(cmd.success());
}

fn main() {
    let args: Vec<String> = env::args().collect();
    for arg in args {
        let mut name = "";
        let mut ver = "";

        if arg.contains("crate") {
            let mut crate_name = arg.replace("crate:", "");
            crate_name = crate_name.replace(".txt", "");
            
            let names: Vec<&str> = crate_name.split("-").collect();
            name = names[0];
            ver = names[1];

            setup_prusti(name, ver)
        }
    }
}


