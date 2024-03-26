use std::env;
use std::fs;
use std::path::{Path, PathBuf};

/*
    Cite:  
    https://github.com/viperproject/prusti-dev/blob/2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
    https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs
*/
fn setup_prusti(name: &str, version:&str) {
    let dirname = format!("/tmp/{name}-{version}");

    let cwd = std::env::current_dir().unwrap();
    let target = if cfg!(debug_assertions) {
        "debug"
    } else {
        "release"
    };

    let prusti = cwd.join(
        ["target", target, "prusti-release-macos-x86", "cargo-prusti"]
            .iter()
            .collect::<PathBuf>(),
    );

    // TODO: might want to automate download if asserted false
    assert!(prusti.exists());

    let env_root_path = fs::read_to_string("./.env").unwrap();
    let _ = env::set_current_dir(Path::new(env_root_path.as_str()));
    let z3_path = env::current_dir().unwrap().join("viper_tools/z3/bin/z3");
    env::set_var("Z3_EXE", z3_path);
    let host_viper_home = env::current_dir().unwrap().join("viper_tools/backends");
    env::set_var("viper_home",  host_viper_home);

    // TODO: fix, check ./tmp/log
    let log_dir = Path::new("/tmp/log");
    let log_name = format!("{name}-{version}");
    let log_crate = log_dir.join(log_name);
    let _ = fs::create_dir(log_crate.clone());

    let _cmd = std::process::Command::new(prusti)
        .env("PRUSTI_LOG_DIR", log_crate.clone().as_os_str())
        .env("PRUSTI_DUMP_DEBUG_INFO", "true")
        .env("PRUSTI_ENABLE_CACHE", "false")
        .current_dir(&dirname)
        .status()
        .expect("failed to run prusti");

}



fn main() {
    let args: Vec<String> = env::args().collect();

    let crate_name = args.get(args.len() - 1).unwrap();
    let names: Vec<&str> = crate_name.split("-").collect();
    let ver = names[names.len()-1];
    let name = crate_name.replace(&("-".to_owned() + ver), "");
    setup_prusti(name.as_str(), ver);
}


