pub fn div_zero(){
    9 / 0;
}

pub fn div_overflow(){
    i32::MIN / -1;
}

pub fn div(){
    9 / 10;
}

pub fn mod_overflow() {
    i32::MIN % -1;
}


pub fn mod_zero() {
    8 % 0;
}

pub fn modulus() {
    8 % 9;
}
