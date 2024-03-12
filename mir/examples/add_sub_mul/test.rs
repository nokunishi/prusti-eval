use std::{f32::INFINITY, u32::MAX};

// arg needs to be ref, not x:i32, to produce mir
fn add(x:&i32, y:&i32) {
   let _ = x + y;
}

fn add_overflow(x:&i32) {
   let _ = x + i32::MAX;
}

fn sub(x:&i32, y:&i32) {
   let _ = x - y;
}

fn sub_overflow(x:&i32, y:&i32) {
   let _ = x - i32::MAX;
}

fn mul(x:&i32, y:&i32) {
   let _ = x * y;
}

fn mul_overflow(x:&i32) {
   let _ = 100 * i32::MAX;
}

// without main fn, it does not produce mir
fn main() {}