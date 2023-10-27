// cite 
// Part of code inspired by https://github.com/viperproject/prusti-dev/blob
// /2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// and 
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs


extern crate reqwest; 

use std::fs::{self, create_dir};
use std::path::{Path, PathBuf};
use serde_json::*;
use std::fs::File;
use std::io;
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
    }
    println!("Unwrapping: {filename}");
 
}


struct CargoPrusti {
    prusti_home: PathBuf,
    viper_home: PathBuf,
    z3_exe: PathBuf,
    java_home: Option<PathBuf>,
}

impl cmd::Runnable for CargoPrusti {
    fn name(&self) -> cmd::Binary {
        cmd::Binary::Global(self.prusti_home.join("cargo-prusti"))
    }

    fn prepare_command<'w, 'pl>(&self, cmd: cmd::Command<'w, 'pl>) -> cmd::Command<'w, 'pl> {
        let java_home = self
            .java_home
            .as_ref()
            .map(|p| p.to_str().unwrap())
            .unwrap_or("/usr/lib/jvm/default-java");
        cmd.env("VIPER_HOME", self.viper_home.to_str().unwrap())
            .env("Z3_EXE", self.z3_exe.join("z3").to_str().unwrap())
            .env("JAVA_HOME", java_home)
            .env("PRUSTI_CARGO_PATH", "/opt/rustwide/cargo-home/bin/cargo")
    }
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


        // println!("{:#?}", prusti);
        let exit = std::process::Command::new(prusti)
            .status();

        println!("{:#?}", exit.unwrap_err())

          /*   if file.is_ok() {
                let read  = fs::read(crate_path);
                println!("{:#?}", read.unwrap());
                // fs::write(workspace, file.unwrap()).unwrap();
            } */
       }
    }
}

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
    run_prusti();
}