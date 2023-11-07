// cite 
// Part of code inspired by https://github.com/viperproject/prusti-dev/blob
// /2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// and 
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs

// TODO: refactor later to use sandbox
#![feature(try_trait_v2)]
extern crate reqwest; 

use std::fs::{self, create_dir};
use std::path::{Path, PathBuf};
use serde_json::*;
use std::fs::File;
use std::io;
use std::env;
use log::*;
use serde::{Serialize, Deserialize};
use crate::io::Cursor;
use std::process;
use std::io::BufReader;
use std::os::unix::fs::PermissionsExt;
#[cfg(feature = "unstable-toolchain-ci")]
use crate::tools::RUSTUP_TOOLCHAIN_INSTALL_MASTER;

const CRATELIST_PATH:&str = "./CrateList.json";

async fn read_json() -> io::Result<()> {


    let path = Path::new(&CRATELIST_PATH);
    let mut file = fs::read_to_string(path)
    .expect("failed to read CrateList");

    let file_str = file.as_mut_str();
    
    let json_file: serde_json::Value = serde_json::from_str(file_str)
    .expect("CrateList.json not well formatted");

    if let Some(crates) = json_file["crates"].as_array() {
        /* for (i, crate_) in crates.iter().enumerate() {
            println!("{:#?}", crate_["Package"]); } */

        let packages: Vec<Value> = crates.iter()
            .map(|crate_| crate_["Package"].clone())
            .collect();

        for package in  packages {
            let mut name = package["name"].to_owned().to_string();
            let mut version = package["version"].to_owned().to_string();

            // remove '/"' in the beginning and end
            name.remove(0);
            name.remove(name.len() -1);
            version.remove(0);
            version.remove(version.len()-1);

            fetch_and_write(name.as_str(), version.as_str()).await;
            run_prusti(name.as_str(), version.as_str());
        }
    } else {
        println!("No crates in CrateList.json")
    }

    Ok(())
    
}

async fn fetch_and_write(name: &str, version:&str) {
    let dirname = format!("/tmp/{name}-{version}");
    let filename = format!("{dirname}.crate");

    if !PathBuf::from(&filename).exists() { 
        let url = format!("https://crates.io/api/v1/crates/{name}/{version}/download");
        let res = reqwest::get(url)
        .await.expect("failed to fetch from crates.io")
        .bytes().await.expect("failed to convert to bytes");
        
        let mut tmp_file = File::create(filename.clone()).expect("failed to create a tmp file");
        let mut content = Cursor::new(res);
        io::copy(&mut content, &mut tmp_file).expect("failed to write to tmp file");
        // println!("Unwrapping: {filename}");
    }
    // info!("{filename} already exists")
}


fn run_prusti(name: &str, version: &str) {
    let _ = init_prusti(name, version);
}

// cite https://github.com/viperproject/prusti-dev/blob/2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs
fn init_prusti(name: &str, version:&str) -> io::Result<()> {
    let dirname = format!("/tmp/{name}-{version}");
    let filename = format!("{dirname}.crate");

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

    // automate chmod 755?
    /*
     let prusti = cwd.join(
        ["target", target, "prusti-release-macos"]
            .iter()
            .collect::<PathBuf>(),
    );

    let _change_cwd = env::set_current_dir(prusti.clone());
    let prusti_macos_path = env::current_dir().expect("failed to change dir to prusti_macos");
    assert_eq!(prusti_macos_path, prusti);
    
    for prusti_dev in fs::read_dir(prusti_macos_path.clone())? {
            let prusti_dev_path = prusti_dev?.path();

            if !prusti_dev_path.ends_with(".DS_Store")  && !prusti_dev_path.ends_with("deps")  {
                let mut perms = fs::metadata(prusti_dev_path.clone())?.permissions();
                perms.set_readonly(false);
                fs::set_permissions(prusti_dev_path.clone(), perms)?;
            }
    } */


    let env_root_path = fs::read_to_string("./.env").unwrap();
    let _ = env::set_current_dir(Path::new(env_root_path.as_str()));
    let z3_path = env::current_dir().unwrap().join("viper_tools/z3/bin/z3");
    let host_viper_home = env::current_dir().unwrap().join("viper_tools/backends");
    

    env::set_var("Z3_EXE", z3_path);
    env::set_var("viper_home",  host_viper_home);
    let pwd = env::current_dir();
    let p = pwd?.join("log");
    env::set_var("LOG_DIR", p.clone());

    // println!("Running: {prusti:?} on {dirname}");

    if dirname.clone() == "/tmp/crc32fast-1.2.0" {

        let exit = std::process::Command::new(prusti)
        .env("PRUSTI_LOG_DIR", p.clone().as_os_str())
        .env("PRUSTI_DUMP_DEBUG_INFO", "true")
        .env("PRUSTI_DUMP_VIPER_PROGRAM", "true")
        .env("PRUSTI_SKIP_UNSUPPORTED_FEATURES", "true")
        // .env("PRUSTI_NO_VERIFY_DEPS", "true")
        .current_dir(&dirname)
        .status()
        .expect("failed");
    }


    
/*     let exit = std::process::Command::new(prusti)
        .env("PRUSTI_SKIP_UNSUPPORTED_FEATURES", "true")
        // .env("PRUSTI_LOG", "debug")
        .env("PRUSTI_NO_VERIFY_DEPS", "true")
        // .env("PRUSTI_TOP_CRATES", "true")
        .current_dir(&dirname)
        .status()
        .unwrap(); */

    // assert!(exit.success());
    Ok(())
}



#[tokio::main]
async fn main() {
    let cwd = std::env::current_dir().unwrap();
    let log = cwd.join("log");

    if !PathBuf::from(log.clone()).exists() {
        let _ = fs::create_dir(log)
                .expect("failed to create debug_info dir");
    }

    let _ = read_json().await;
}