/*
Crichton, W(2021) flowistry(v0.5.41)[https://github.com/willcrichton/flowistry/tree/master?tab=License-1-ov-file]
*/

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

// This is the core analysis. Everything below this function is plumbing to
// call into rustc's API.
fn compute_dependencies<'tcx>(
  tcx: TyCtxt<'tcx>,
  body_with_facts: &BodyWithBorrowckFacts<'tcx>,
) {
  println!("Body:\n{}", body_with_facts.body.to_string(tcx).unwrap());
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
    queries: &'tcx rustc_interface::Queries<'tcx>,
  ) -> rustc_driver::Compilation {
    queries.global_ctxt().unwrap().enter(|tcx| {
      let hir = tcx.hir();

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
