fn out_of_bounds(y: &i32) {
    let x = [2, 3, 4];
    let _ = x[9];
}

fn within_bound(y: &i32) {
    let x = [2, 3, 4];
    let _ = x[1];
}

fn panic(){
    panic!()
}

fn unreachable(){
    unreachable!()
}

fn unimplemented(){
    unimplemented!()
}

fn nested() {
    unreachable();
}

// this is erroneous
fn compile_err(x: &i32){
    x = &42i32;
}