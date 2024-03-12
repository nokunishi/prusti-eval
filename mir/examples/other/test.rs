fn index(y: &i32) {
    let x = [2, 3, 4];
    let _ = x[9];
}

fn out_of_bounds(y: &i32) {
    let x = [2, 3, 4];
    let _ = x[1];
}

// this is erroneous
fn immutable(x: &i32){
    x = &42i32;
}

fn panic(y:&i32){
    panic!()
}

fn unreachable(y:&i32){
    unreachable!()
}

fn unimplemented(y:&i32){
    unimplemented!()
}


fn nested() {
    unreachable(3);
}
