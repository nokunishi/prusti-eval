use std::{f32::INFINITY, u32::MAX};

fn add(x:i32, y:i32) {
   let _ = x + y;
}

fn add_overflow() {
   let _ = 1 + i32::MAX;
}

fn sub(x:i32, y:i32) {
   let _ = x - y;
}

fn sub_underflow() {
   let _ = -1 - i32::MAX;
}

fn mul(x:i32, y:i32) {
   let _ = x * y;
}

fn mul_overflow() {
   let _ = 100 * i32::MAX;
}
