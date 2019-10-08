// Simple Mixer to generate a Dialtone  
 #include <Audio.h>  
 #include <Wire.h>  
 #include <SPI.h>  
 #include <SD.h>  
 // GUItool: begin automatically generated code  
 AudioSynthWaveformSine  sine1;     //xy=183,181  
 //AudioSynthWaveformSine  sine2;     //xy=192,251  
 //AudioMixer4       mixer1;     //xy=392,207  
 AudioOutputAnalog    dac;      //xy=591,178  
 AudioConnection     patchCord1(sine1,dac);  
 //AudioConnection     patchCord2(sine2, 0, mixer1, 1);  
 //AudioConnection     patchCord3(mixer1, dac);  
 // GUItool: end automatically generated code  
 void setup() {  
  // Audio connections require memory to work. For more  
  // detailed information, see the MemoryAndCpuUsage example  
  AudioMemory(3);  
  }  
  void loop() {  
  sine1.frequency(1000); //350  
  sine1.amplitude(0.9);  
  //sine2.frequency(440);//440  
  //sine2.amplitude(0.1);  
  //delay(100);  
  //sine1.amplitude(0);  
  //sine2.amplitude(0);  
  //delay(100);  
  }
  
