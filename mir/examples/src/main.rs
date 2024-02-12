use std::{f32::INFINITY, u32::MAX};

fn add(x:u32) {
   let _ = x + u32::MAX;
}

fn add1(x:u32, y:u32) {
   let _ = x + y;
}

fn sub(x:u32, y:u32) {
   let _ = x - y;
}

fn mul(x:u32, y:u32) {
   let _ = x * y;
}

fn div(x:u32, y:u32) {
   let _ = x * y;
}

fn div_by_zero2(x:u32, y:u32) {
   let _ = x / y;
}

fn rs(x:u32) {
   let _ = x >> 5;
}

fn ls(x:u32) {
   let _ = x << 5;
}


fn div_by_zero(x:u32) {
   let _ = x / 0;
}


fn remainder(x:u32, y:u32) {
   let _ = x % y;
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

fn inf(){
    let _ = INFINITY;
}

fn and(x: u32, y:u32){
    let _ = x & y;
}

macro_rules! foo { () => {add(4)}}

fn foo() {
    foo!();
}

fn xor(x: u32, y:u32){
    let _ = x ^ y;
}

fn or(x: u32, y:u32){
    let _ = x | y;
}

fn err(){
    let x = 20;
    x = 4;
}

fn nest() {
    add1(3, 4);
}

fn nest1() {
    add(3);
}

fn bound() {
    let x = [2, 3, 4];
    let _ = x[9];
}

fn bound2() {
    let x = [2, 3, 4];
    let _ = x[1];
}

fn main() {
    println!("Hello, world!");
    add(2);
    add1(2, 3);
    mul(2, 3);
    div(2, 3);
    div_by_zero(2);
    div_by_zero2(2, 0);
    sub(2, 3);
    remainder(2, 3);
    and(MAX, 4);
    xor(MAX, 4);
    or(MAX, MAX);
    rs(2);
    ls(2);
    err();
    panic();
    inf();
    nest();
    nest1();
    unimplemented();
    unreachable();
    // ce();
}
