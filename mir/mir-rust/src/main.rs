#![feature(rustc_private)]

extern crate rustc_borrowck;
extern crate rustc_data_structures;
extern crate rustc_driver;
extern crate rustc_hir;
extern crate rustc_interface;
extern crate rustc_middle;
extern crate rustc_span;

use std::process::Command;

use rustc_borrowck::consumers::BodyWithBorrowckFacts;
use rustc_hir::ItemKind;
use rustc_middle::ty::TyCtxt;
use rustc_utils::{
  mir::borrowck_facts,
  BodyExt,
};

use std::env;
use std::fs::*;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};
use std::io::prelude::*;


fn read_env() -> Result<String, io::Error> {

    for line in read_to_string("../../.env").unwrap().lines() {
        if line.contains("WORKSPACE") {
          let mut i = 0;
          let mut root = String::new();
          root.push('"');

          for c in line.chars() {
              if i != 0 {
                root.push(c)
              }
              if c == '"' {
                 i ^= 1
              }
          }

          return Ok(root)
        }
    }
    let null = String::new();
    return Ok(null)
}


fn run_python(file: String) {
    let x = Command::new("python3")
        .arg("format.py")
        .arg(file)
        .output()
        .expect("failed to execute process");
}

/* 
----
For most codes below, some modifications were made to:
Crichton, W(2021) flowistry(v0.5.41)[https://github.com/willcrichton/flowistry/tree/master?tab=License-1-ov-file]
---
*/



fn compute_dependencies<'tcx>(
  tcx: TyCtxt<'tcx>,
  body_with_facts: &BodyWithBorrowckFacts<'tcx>,
) {
  let mut root = read_env().unwrap();

  if root.len() == 0  {
    println!("failed to read root env var");
    return
  } else {
    root = root.replace('\"', "");
  }
  let args = std::env::args().collect::<Vec<_>>();
  let name = &args[1].replace(".rs", ".txt");
  let mut f = File::create(name).unwrap();
  f.write_all(body_with_facts.body.to_string(tcx).unwrap().as_bytes());
}

struct Callbacks;
impl rustc_driver::Callbacks for Callbacks {
  fn config(&mut self, config: &mut rustc_interface::Config) {
    borrowck_facts::enable_mir_simplification();
    config.override_queries = Some(borrowck_facts::override_queries);
  }

  fn after_crate_root_parsing<'tcx>(
    &mut self,
    _compiler: &rustc_interface::interface::Compiler,
    queries: &'tcx rustc_interface::Queries<'tcx>
  ) -> rustc_driver::Compilation {
    queries.global_ctxt().unwrap().enter(|tcx| {
    
      let hir = tcx.hir();
      
      let mut args = std::env::args().collect::<Vec<_>>();

    /*
     Python::with_gil(|py| {
    let module = PyModule::import(py, "format")?;
    let fun = module.getattr("fomart")?;
    let args = (file,);
    let result = fun.call1(args)?;
    assert_eq!(result.extract::<&str>()?, "56");
    Ok(())
}) */
      let mut file = String::new();

      for arg in args {
        if arg.contains(".rs") {
          file = arg
        }
      }

      run_python(file);

      // Get the first body we can find
      let body_id = hir
        .items()
        .filter_map(|id| match hir.item(id).kind {
          ItemKind::Fn(_, _, body) => Some(body),
          _ => None,
        })
        .next()
        .unwrap();

      let def_id = hir.body_owner_def_id(body_id);
      let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);

      compute_dependencies(tcx, body_with_facts)
    });
    rustc_driver::Compilation::Stop
  }
}

fn main() {
  // Get the sysroot so rustc can find libstd
  let print_sysroot = Command::new("rustc")
    .args(&["--print", "sysroot"])
    .output()
    .unwrap()
    .stdout;
  let sysroot = String::from_utf8(print_sysroot).unwrap().trim().to_owned();

  let mut args = std::env::args().collect::<Vec<_>>();

  if args.len() < 2 {
      println!("invalid number of args, specify file to run on");
      return
  }
 
  args.extend(["--sysroot".into(), sysroot]);

  // Run rustc with the given arguments
  let mut callbacks = Callbacks;
  rustc_driver::catch_fatal_errors(|| {
    rustc_driver::RunCompiler::new(&args, &mut callbacks)
      .run()
      .unwrap()
  })
  .unwrap();
}
