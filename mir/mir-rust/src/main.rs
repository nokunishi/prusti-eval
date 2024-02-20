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


// avoid panicking
fn raise_exception(file: String) {
  let cwd = env::current_dir().expect("failed to fetch cwd");
  let mut path = PathBuf::new();
  path.push(cwd);
  let parent =  path.parent().expect("failed to fetch parent dir");

  let script_dir = Path::new(parent).join("script");
  env::set_current_dir(&script_dir);
  env::current_dir().expect("failed to fetch cwd");
  
  let x = Command::new("python3")
        .arg("run.py")
        .arg("--rustc_e")           // TODO: count number of failed fns
        .arg(file)
        .output()
        .expect("failed to execute process");
}

/* 
----
For most codes below, modifications were made to:
Crichton, W(2021) flowistry(v0.5.41)[https://github.com/willcrichton/flowistry/tree/master?tab=License-1-ov-file]
---
Modified so that it will extract mir for every function, not just for the first
*/

fn compute_dependencies<'tcx>(
  tcx: TyCtxt<'tcx>,
  body_with_facts: &BodyWithBorrowckFacts<'tcx>,
  i: usize
) {
  let args = std::env::args().collect::<Vec<_>>();
  let name = &args[1].replace(".rs", "");
  let file_name = format!("{name}-{i}.txt");
  let mut f = File::create(file_name).unwrap();
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
      let mut i = 0;

        // NOTE: hir.items()... has to be called everytime 
        // for the mir to be proudced correctly
        while hir.items().filter_map(|id| match hir.item(id).kind {
            ItemKind::Fn(_, _, body) => Some(body),
            _ => None,
        }).nth(i).is_some() {
          
          let body_id =  hir.items().filter_map(|id| match hir.item(id).kind {
              ItemKind::Fn(_, _, body) => Some(body),
               _ => None,
          }).nth(i).unwrap();

          let def_id = hir.body_owner_def_id(body_id);
          let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);

          compute_dependencies(tcx, body_with_facts, i);
          i += 1;
        }
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

  let mut file = String::new();

  for arg in args.clone() {
    if arg.contains(".rs") {
      file = arg;
    }
  }

  // Run rustc with the given arguments
  let mut callbacks = Callbacks;
  rustc_driver::catch_fatal_errors(|| {
    rustc_driver::RunCompiler::new(&args, &mut callbacks)
      .run()
      .unwrap_or_else(|_| {})
  })
  .unwrap_or_else(|_| {});
}
