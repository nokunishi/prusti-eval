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

/* 
----
Credit is given to
Crichton, W(2021) flowistry(v0.5.41)[https://github.com/willcrichton/flowistry/tree/master?tab=License-1-ov-file]
__
in which the following code is based on with modifications
*/

fn compute_dependencies<'tcx>(
  tcx: TyCtxt<'tcx>,
  body_with_facts: &BodyWithBorrowckFacts<'tcx>,
  span: rustc_span::Span
) -> Result<(), io::Error>{
  let args = std::env::args().collect::<Vec<_>>();
  let name = &args[1].replace(".rs", "");

  let content = body_with_facts.body.to_string(tcx).unwrap();
  let mut fn_name = content.split("->").collect::<Vec<&str>>()[0];
  fn_name = fn_name.split("(").collect::<Vec<&str>>()[0];
  if fn_name.contains(">::") {
      if fn_name.contains("::fmt") {
        return Ok(())
      } else {
        fn_name = fn_name.split(">::").collect::<Vec<&str>>()[1];
      }
  }
  else {
      fn_name = fn_name.split("fn").collect::<Vec<&str>>()[1];
  }
  let fn_string = fn_name.to_string().replace(" ", "");


  let file_name = format!("{name}-{fn_string}.txt");
  let mut f = File::create(file_name.clone()).unwrap();
  f.write_all(body_with_facts.body.to_string(tcx).unwrap().as_bytes()); 
  let path = format!("path: {:#?}", span);
  
  let mut file = OpenOptions::new().append(true).create(true).open(file_name).unwrap();
  file.write(path.as_bytes());
  return Ok(())
}

struct Callbacks;
impl rustc_driver::Callbacks for Callbacks {
  fn config(&mut self, config: &mut rustc_interface::Config) {
    borrowck_facts::enable_mir_simplification();
    config.override_queries = Some(borrowck_facts::override_queries);
  }

  // modify so that it will extract mir for every function, not just for the first
  fn after_crate_root_parsing<'tcx>(
    &mut self,
    _compiler: &rustc_interface::interface::Compiler,
    queries: &'tcx rustc_interface::Queries<'tcx>
  ) -> rustc_driver::Compilation {
    queries.global_ctxt().unwrap().enter(|tcx| {
    
      let hir = tcx.hir();
      let mut i = 0;

      hir.items().for_each(|id| 
        {
          // {println!("{:#?}", hir.item(id).kind);
          
          match hir.item(id).kind {
            ItemKind::Fn(_, x, body) => {
              println!("{:#?}", x);
              let def_id = hir.body_owner_def_id(body);
              let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);
    
              compute_dependencies(tcx, body_with_facts,  x.where_clause_span);
            },
             _ => (),
          }

          match hir.item(id).kind {
            ItemKind::Impl(body) => {
              for item in body.items {
                let def_id =  item.id.owner_id.def_id;
                let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);
                compute_dependencies(tcx, body_with_facts, item.span);
              }
            }
               _ => (),
          }
        }
      );
        

      // NOTE: hir.items()... has to be called everytime 
      // for the mir to be proudced correctly
     /*  while hir.items().filter_map(|id| match hir.item(id).kind {
            ItemKind::Fn(_, _, body) => Some(body),
            _ => None,
      }).nth(i).is_some() {
        
        let (x, body_id) =  hir.items().filter_map(|id| match hir.item(id).kind {
          ItemKind::Fn(_, x, body) => Some((x, body)),
          _ => None,
        }).nth(i).unwrap();
        
        let mut seen = false;
        for param in x.params {

          if !seen {
            let def_id = hir.body_owner_def_id(body_id);
            let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);
    
            compute_dependencies(tcx, body_with_facts,  param.span);
            seen = true 
          }
        }

        i += 1;
      }

      let hir = tcx.hir();
      let mut j = 0;
        // have to separate while loops or else 
        // the mir does not get produced for all fns 
      while hir.items().filter_map(|id| match hir.item(id).kind {
            ItemKind::Impl(body) => Some(body),
            _ => None,
      }).nth(j).is_some() {
        
        let impl_items =  hir.items().filter_map(|id| match hir.item(id).kind {
              ItemKind::Impl(body) => Some(body),
               _ => None,
        }).nth(j).unwrap();

          for item in impl_items.items {
            let def_id =  item.id.owner_id.def_id;
            let body_with_facts = borrowck_facts::get_body_with_borrowck_facts(tcx, def_id);
            compute_dependencies(tcx, body_with_facts, item.span);
          }

      j += 1;
      }*/
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
      .unwrap_or_else(|_| {})
  })
  .unwrap_or_else(|_| {});
}
