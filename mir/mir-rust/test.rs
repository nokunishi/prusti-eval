use std::{f32::INFINITY, u32::MAX};

fn add(x:u32) {
   let _ = x + u32::MAX;
}

fn main() {
    add(2);
}