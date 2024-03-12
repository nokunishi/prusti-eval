pub fn div_zero(out: &u8){
    9 / 0;
}

pub fn div_overflow(out: &u8){
    i32::MIN / -1;
}

pub fn div(out: &u8){
    9 / 10;
}

pub fn mod_overflow(out: &u8) {
    i32::MIN % -1;
}


pub fn mod_zero(out: &u8) {
    8 % 0;
}

pub fn mod(out: &u8) {
    8 % 9;
}

pub fn no_ref_arg(out: u8) {
    8 % 9;
}

fn main() {}