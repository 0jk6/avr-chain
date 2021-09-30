#include "sha1.h"

void setup(){
  Serial.begin(115200);
}

void loop() {
  if(Serial.available() > 0){
    String s = Serial.readStringUntil(',');
    compute_hash(s);
    
    //read out the extra bytes
    while(Serial.available())
      Serial.read();
  }
}

//computes the has until it has found a hash that is starting with a '0' character
void compute_hash(String s){

  char *digitArray = "0123456789abcdef";

  int nonce = 0;
  char buffer[40];
  //hash the string until the starting two characters are equal to zero
  //every time we do not find the required hash, we will add a nonce to it by incrementing it
  do{
    String h=s;
    uint8_t *hash;

    //add nonce to the string
    h.concat(nonce);
    
    Sha1.init();
    Sha1.print(h);
    hash = Sha1.result();

    for(int i=0; i<40; i+=2){
      buffer[i] = digitArray[(hash[i/2] & 0xF0) >> 4];
      buffer[i+1] = digitArray[(hash[i/2] & 0x0F)];
    }
    nonce += 1;
  }while(buffer[0] != '0');

  for(int i=0; i<40; i++){
    Serial.print(buffer[i]);
  }
  Serial.print(",");
  Serial.println(nonce-1);
}
