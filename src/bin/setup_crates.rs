// cite 
// Part of code inspired by https://github.com/viperproject/prusti-dev/blob
// /2e47a2705a88ba523dc3ad2e0359799943f26e0f/mir-state-analysis/tests/top_crates.rs
// and 
// https://github.com/viperproject/prusti-dev/blob/master/test-crates/src/main.rs


#![feature(try_trait_v2)]
extern crate reqwest; 

use std::fmt::format;
use std::fs;
use std::path::{Path, PathBuf};
use serde_json::*;
use std::fs::File;
use std::io;
use std::io::Cursor;
use std::env;
use serde::{Serialize, Deserialize};
use std::process::{self, Command};
#[cfg(feature = "unstable-toolchain-ci")]
use crate::tools::RUSTUP_TOOLCHAIN_INSTALL_MASTER;

const CRATELIST_PATH:&str = "./CrateList.json";

async fn read_json() {


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
        }
    } else {
        println!("No crates in CrateList.json");
    }
    
}

async fn fetch_and_write(name: &str, version:&str) {
    let dirname = format!("/tmp/{name}-{version}");
    let filename = format!("{dirname}.crate");
    let crate_name_json = format!("{name}-{version}.json");
    let crate_name_txt = format!("{name}-{version}.txt");

    let cwd = env::current_dir().expect("failed to get cwd");
    let log_dir = cwd.parent().expect("failed to get parent dir").join("log");
    let err_report_path = log_dir.join(
        ["err_report", crate_name_json.as_str()]
            .iter()
            .collect::<PathBuf>(),
    );

    let txt_path = log_dir.join(crate_name_txt.as_str());

    let args: Vec<String> = env::args().collect();

    if !args.contains(&String::from("reset")) && (txt_path.exists() || err_report_path.exists()) {
        return
    }

    if !PathBuf::from(&filename).exists() { 

        let url = format!("https://crates.io/api/v1/crates/{name}/{version}/download");
        let res = reqwest::get(url)
        .await.expect("failed to fetch from crates.io")
        .bytes().await.expect("failed to convert to bytes");
        
        let mut tmp_file = File::create(filename.clone()).expect("failed to create a tmp file");
        let mut content = Cursor::new(res);
        io::copy(&mut content, &mut tmp_file).expect("failed to write to tmp file");

        let status = std::process::Command::new("tar")
        .args(["-xf", &filename, "-C", "/tmp/"])
        .status()
        .unwrap();
        assert!(status.success());
        
        println!("Unwrapping: {dirname}");
    } 


   /*  // reset /tmp
    if PathBuf::from(&filename).exists() { 
      let _ = fs::remove_file(&filename);
    }    */
}


#[tokio::main]
async fn main() {
    let log = Path::new("/tmp/prusti_log");

    if !log.exists() {
        let _ = fs::create_dir(log)
                .expect("failed to create /tmp/prusti_log dir");
    }

    read_json().await;
}



