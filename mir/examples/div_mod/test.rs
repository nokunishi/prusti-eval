pub fn div_u1(x: u32, y:u32){
    x / y;
}

pub fn div_u2(x: u32){
    x / 9;
}

pub fn div_u3(x: u32){
    3 / x;
}


pub fn div_i1(x: i32, y:i32){
    x / y;
}

pub fn div_i2(x: i32){
    x / 9;
}

pub fn div_i3(x: i32){
    3 / x;
}

pub fn div_safe(){
    8 / 9;
}

pub fn div_zero(){
    9 / 0;
}

pub fn div_overflow(){
    i32::MIN / -1;
}

pub fn mod_u1(x: u32, y:u32) {
    x % y;
}

pub fn mod_u2(x:u32) {
    8 % x;
}

pub fn mod_u3(x:u32) {
    x % 2;
}

pub fn mod_i1(x: i32, y:i32) {
    x % y;
}

pub fn mod_i2(x:i32) {
    8 % x;
}

pub fn mod_i3(x:i32) {
    x % 2;
}


pub fn mod_safe() {
    8 % 9;
}


pub fn mod_overflow() {
    i32::MIN % -1;
}