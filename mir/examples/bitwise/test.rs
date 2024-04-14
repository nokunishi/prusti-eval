fn ls(x: i32) {
   let _ = x << 5;
}

fn rs(x:i32) {
   let _ = x >> 5;
}

fn and(x: u32, y:u32){
    let _ = x & y;
}

fn or(x: u32, y:u32){
    let _ = x | y;
}

fn xor(x: u32, y:u32){
    let _ = x ^ y;
}

fn not(x: i32){
    let _ = !x;
}

fn not_overflow(){
    let _ = !i32::MIN;
}