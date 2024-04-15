use std::u32::MAX;

fn add_i(x:i32, y:i32) {
   let _ = x + y;
}

fn add_u(x:u32, y:u32) {
   let _ = x + y;
}

fn add_safe() {
   let _ = 10 + 20;
}

fn add_overflow() {
   let _ = 1 + i32::MAX;
}

fn sub_i(x:i32, y:i32) {
   let _ = x - y;
}

fn sub_u(x:u32, y:u32) {
   let _ = x - y;
}

fn sub_safe() {
   let _ = 10 - 20;
}

fn sub_underflow() {
   let _ = -1 - i32::MAX;
}

fn mul_i(x:i32, y:i32) {
   let _ = x * y;
}

fn mul_u(x:u32, y:u32) {
   let _ = x * y;
}

fn mul_safe() {
   let _ = 10 * 20;
}

fn mul_overflow() {
   let _ = 100 * i32::MAX;
}
