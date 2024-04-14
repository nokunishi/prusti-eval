pub fn div1(x: i32, y:i32){
    x / y;
}

pub fn div2(x: i32){
    x / 9;
}

pub fn div3(x: i32){
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

pub fn mod1(x: u32, y:u32) {
    x % y;
}

pub fn mod2(x:u32) {
    8 % x;
}

pub fn mod3(x:u32) {
    x % 2;
}


pub fn mod_safe() {
    8 % 9;
}


pub fn mod_overflow() {
    i32::MIN % -1;
}


pub fn mod_zero() {
    8 % 0;
}