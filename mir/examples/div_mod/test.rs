pub fn div(x: i32, y:i32){
    x / y;
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

pub fn modulus(x: u32, y:u32) {
    x % y;
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