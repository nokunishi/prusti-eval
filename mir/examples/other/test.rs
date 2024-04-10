use std::option::Option;

fn panic_free() {
    let x = Option::Some(10);
    x.unwrap();
}

// panics
fn nest_panic() {
   let x: Option<u32> = Option::None;
   x.unwrap();
}

// this gives compilation error
fn compile_err(x: &i32){
    x = &42i32;
}