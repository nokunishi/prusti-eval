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

fn assert_true() {
    assert!(true)
}

fn assert_false() {
    assert!(false);
}

fn assert_eq_true() {
    assert_eq!(3, 3)
}

fn assert_eq_false() {
    assert_eq!(3, 4)
}


fn assert_ne_true() {
    assert_ne!(3, 4)
}

fn assert_ne_false() {
    assert_ne!(3, 3)
}

