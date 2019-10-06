float phase = 0.0;
float pi = 3.1415927;
float twopi = pi * 2.0;
float frequency = 1000.0; // 1 kHz
float period_usec = 1000000.0 * 1.0 / frequency; // in micro-seconds
float phase_step_usec = period_usec / 1000.0;

// special variable: automatically updates every usec
elapsedMicros usec = 0;

void setup() {
  analogWriteResolution(12);
}

void loop() {
  // voltage between 0.4 and 2.4V as per LDD-1000L Specification
  // https://www.meanwell.com/Upload/PDF/LDD-L/LDD-L-SPEC.PDF 
  float val = sin(phase) * 1000.0 + 1550.0; 
  analogWrite(A14, (int)val);
  phase = phase + phase_step_usec;
  if (phase >= twopi) phase = phase - twopi;
  while (usec < phase_step_usec) ; // wait until  
  usec = usec - 1; 
}
