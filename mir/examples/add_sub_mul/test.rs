use std::u32::MAX;

fn add(x:i32, y:i32) {
   let _ = x + y;
}

fn add_safe() {
   let _ = 10 + 20;
}

fn add_overflow() {
   let _ = 1 + i32::MAX;
}

fn sub(x:i32, y:i32) {
   let _ = x - y;
}

fn sub_safe() {
   let _ = 10 - 20;
}

fn sub_underflow() {
   let _ = -1 - i32::MAX;
}

fn mul(x:i32, y:i32) {
   let _ = x * y;
}

fn mul_safe() {
   let _ = 10 * 20;
}

fn mul_overflow() {
   let _ = 100 * i32::MAX;
}
