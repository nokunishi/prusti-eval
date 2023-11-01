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
use std::process::Command;
use std::io::BufReader;
use std::os::unix::fs::PermissionsExt;

const CRATELIST_PATH:&str = "./CrateList.json";

async fn read_json() {
    let path = Path::new(CRATELIST_PATH);
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
        println!("Unwrapping: {filename}");
    }
    // println!("{filename} already exists");
}

struct CargoPrusti {
    prusti_home: PathBuf,
    viper_home: PathBuf,
    z3_exe: PathBuf,
    java_home: Option<PathBuf>,
}

#[derive(Deserialize)]
struct RustToolchainFile {
    toolchain: Toolchain,
}

#[derive(Serialize, Deserialize, Debug)]
struct Config {
    toolchain: Toolchain
}

#[derive(Serialize, Deserialize, Debug)]
struct Toolchain {
    channel: String,
    components: Option<Vec<String>>
}

fn get_rust_toolchain() -> Toolchain {
    let content = include_str!("../../rust-toolchain");
    let rust_toolchain: RustToolchainFile =
        toml::from_str(content).expect("failed to parse rust-toolchain file");
    rust_toolchain.toolchain
}

// cite https://github.com/viperproject/prusti-dev/blob/2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs
fn run_prusti(name: &str, version:&str) {
    let dirname = format!("/tmp/{name}-{version}");
    let filename = format!("{dirname}.crate");

    let status = std::process::Command::new("tar")
        .args(["-xf", &filename, "-C", "/tmp/"])
        .status()
        .unwrap();
    assert!(status.success());
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .append(true)
        .open(format!("{dirname}/Cargo.toml"))
        .unwrap();

    use std::io::Write;
    writeln!(file, "\n[workspace]").unwrap();   

    let cwd = std::env::current_dir().unwrap();
    assert!(
        cfg!(debug_assertions),
        "Must be run in debug mode, to enable full checking"
    );
     let host_prusti_home = if cfg!(debug_assertions) {
        Path::new("target/debug")
    } else {
        Path::new("target/release")
    };
    let host_viper_home = Path::new("viper_tools/backends");
    let host_z3_home = Path::new("viper_tools/z3/bin");
    let host_java_home = env::var("JAVA_HOME")
        .ok()
        .map(|s| s.into())
        .or_else(find_java_home)
        .expect("Please set JAVA_HOME");
    let host_java_policies = collect_java_policies();

     // clippy false positive (https://github.com/rust-lang/rust-clippy/issues/10577)
    #[allow(clippy::redundant_clone)]
    let guest_java_home = host_java_home.clone();
       info!("Using host's Java home {:?}", host_java_home);
    let cargo_prusti = CargoPrusti {
        prusti_home: host_prusti_home.to_path_buf(),
        viper_home: host_viper_home.to_path_buf(),
        z3_exe:  host_z3_home.to_path_buf(),
        java_home: Some(guest_java_home.clone()),
    };

    install_toolchain();
}



pub fn install_toolchain() {
    info!("Install the toolchain...");
    let rust_toolchain = get_rust_toolchain();
    info!("toolchain: {}", rust_toolchain.channel);

    let config = Config {
        toolchain: rust_toolchain
    };

    let config_toml = toml::to_string(&config).unwrap();

    let toml_path = env::current_dir().unwrap().join("Cargo.toml");
    let content = fs::read_to_string(&toml_path.clone()).unwrap();
    let toolchain = toml::from_str::<Config>(&content.clone().as_str());

    if toolchain.is_ok() {
        info!("Rust Toolchain already configed")
    } else {
        let backup_path = env::current_dir().unwrap().join("tmp_toml");  
        let _ = fs::write(&backup_path, content.clone());
        let new_content = content + "\n" + config_toml.as_str();
        fs::write(toml_path, new_content).expect("failed to config Rust toolchain in toml")
    }

    // toml::to_string
}

/// Find the Java home directory
pub fn find_java_home() -> Option<PathBuf> {
    Command::new("java")
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

pub fn collect_java_policies() -> Vec<PathBuf> {
    glob::glob("/etc/java-*")
        .unwrap()
        .map(|result| result.unwrap())
        .collect()
}

/* 

/* cite: https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs*/
use clap::Parser;
use log::{error, info, warn, LevelFilter};
use serde::Deserialize;
use env_logger::Builder;
use std::{
    env,
    error::Error,
    process::Stdio
};


/// How a crate should be tested. All tests use `check_panics=false`, `check_overflows=false` and
/// `skip_unsupported_features=true`.
#[derive(Clone, Copy, Debug, Deserialize, PartialEq, Eq)]
enum TestKind {
    /// Test that Prusti does not crash nor generate "internal/invalid" when the
    /// `allow_unreachable_unsupported_code` flag is set.
    NoErrorsWithUnreachableUnsupportedCode,
    /// Test that Prusti does not crash nor generate "internal/invalid" errors.
    NoErrors,
    /// Test that Prusti does not crash nor generate "invalid" errors.
    NoCrash,
    /// Skip the crate. Prusti crashes or the crate does not compile with the standard compiler.
    Skip,
}

#[derive(Debug, Deserialize)]
struct CrateRecord {
    name: String,
    version: String,
    test_kind: TestKind,
}

fn setup_logs() {
    let mut env = env_logger::Builder::new();
    env.filter_module("test_crates", log::LevelFilter::Info);
    if let Ok(content) = std::env::var("TEST_CRATES_LOG") {
        env.parse_filters(&content);
    }
    info!("{:#?}", env.build());
}

struct CargoPrusti {
    prusti_home: PathBuf,
    viper_home: PathBuf,
    z3_exe: PathBuf,
    java_home: Option<PathBuf>,
}

fn run_prusti() {
    let crates = fs::read_dir("/tmp/").expect("failed to read /tmp file");

    for crate_ in crates {
        let crate_file = crate_.unwrap();
        let crate_path = crate_file.path();
        let dirname = crate_path.to_str().expect("failed to convert path to str");

       if dirname.contains(".crate") {
            let file = fs::OpenOptions::new()
                .write(true)
                .append(true)
                .open(format!("{dirname}/Cargo.toml"));
        
        let status = std::process::Command::new("tar")
            .args(["-xf", &dirname, "-C", "/tmp/"])
            .status()
            .unwrap();

        assert!(status.success());

        let target = if cfg!(debug_assertions) {
            "debug"
        } else {
            "release"
        };
       }
    }
} */

#[tokio::main]
async fn main() {
    let cwd = std::env::current_dir().unwrap();
    let workspace = cwd.join("data");
            
    if !PathBuf::from(workspace.clone()).exists() {
        println!("{:#?}", workspace);
        let _ = fs::create_dir(workspace)
                .expect("failed to create workspace dir");
    }

    read_json().await;
}