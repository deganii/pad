//#define SSD1306_128_32
#include <DMAChannel.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "kinetis.h"


#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET    20 // A6 // Reset pin # (or -1 if sharing Arduino reset pin)
//Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_SSD1306 display(OLED_RESET);


// Multiple input & output objects use the Programmable Delay Block
// to set their sample rate.  They must all configure the same
// period to avoid chaos.
#define PDB_CONFIG (PDB_SC_TRGSEL(15) | PDB_SC_PDBEN | PDB_SC_CONT | PDB_SC_PDBIE | PDB_SC_DMAEN)

// idegani: Modified/Improved DMA DAC Generation. Initial low-res version here:
// https://forum.pjrc.com/threads/28101-Using-the-DAC-with-DMA-on-Teensy-3-1
DMAChannel dma(false);

// idegani: generated from 
// https://daycounter.com/Calculators/Sine-Generator-Calculator.phtml
// points: 1023 (LUT SIZE)
// max amplitude: 4095
// numbers per row: 8
static volatile uint16_t sinetable[] = {
2048,2060,2073,2085,2098,2110,2123,2136,
2148,2161,2173,2186,2198,2211,2223,2236,
2248,2261,2273,2286,2298,2311,2323,2336,
2348,2361,2373,2385,2398,2410,2423,2435,
2447,2460,2472,2484,2497,2509,2521,2533,
2545,2558,2570,2582,2594,2606,2618,2630,
2642,2654,2666,2678,2690,2702,2714,2726,
2738,2750,2762,2773,2785,2797,2808,2820,
2832,2843,2855,2866,2878,2889,2901,2912,
2924,2935,2946,2958,2969,2980,2991,3002,
3014,3025,3036,3047,3058,3069,3079,3090,
3101,3112,3123,3133,3144,3154,3165,3176,
3186,3196,3207,3217,3227,3238,3248,3258,
3268,3278,3288,3298,3308,3318,3328,3338,
3347,3357,3367,3376,3386,3395,3405,3414,
3424,3433,3442,3451,3460,3470,3479,3487,
3496,3505,3514,3523,3532,3540,3549,3557,
3566,3574,3582,3591,3599,3607,3615,3623,
3631,3639,3647,3655,3663,3670,3678,3686,
3693,3701,3708,3715,3723,3730,3737,3744,
3751,3758,3765,3772,3778,3785,3792,3798,
3805,3811,3818,3824,3830,3836,3842,3848,
3854,3860,3866,3872,3877,3883,3889,3894,
3899,3905,3910,3915,3920,3925,3930,3935,
3940,3945,3949,3954,3959,3963,3968,3972,
3976,3980,3984,3988,3992,3996,4000,4004,
4008,4011,4015,4018,4022,4025,4028,4031,
4034,4037,4040,4043,4046,4049,4051,4054,
4056,4059,4061,4063,4065,4067,4069,4071,
4073,4075,4077,4078,4080,4081,4083,4084,
4085,4087,4088,4089,4090,4091,4091,4092,
4093,4093,4094,4094,4094,4095,4095,4095,
4095,4095,4095,4095,4094,4094,4093,4093,
4092,4092,4091,4090,4089,4088,4087,4086,
4085,4084,4082,4081,4079,4078,4076,4074,
4072,4070,4068,4066,4064,4062,4060,4057,
4055,4052,4050,4047,4044,4042,4039,4036,
4033,4030,4026,4023,4020,4016,4013,4009,
4006,4002,3998,3994,3990,3986,3982,3978,
3974,3970,3965,3961,3956,3952,3947,3942,
3938,3933,3928,3923,3918,3913,3907,3902,
3897,3891,3886,3880,3875,3869,3863,3857,
3851,3845,3839,3833,3827,3821,3814,3808,
3802,3795,3788,3782,3775,3768,3761,3755,
3748,3740,3733,3726,3719,3712,3704,3697,
3689,3682,3674,3667,3659,3651,3643,3635,
3627,3619,3611,3603,3595,3587,3578,3570,
3561,3553,3544,3536,3527,3518,3510,3501,
3492,3483,3474,3465,3456,3447,3438,3428,
3419,3410,3400,3391,3381,3372,3362,3352,
3343,3333,3323,3313,3303,3293,3283,3273,
3263,3253,3243,3233,3222,3212,3202,3191,
3181,3170,3160,3149,3139,3128,3117,3106,
3096,3085,3074,3063,3052,3041,3030,3019,
3008,2997,2986,2975,2963,2952,2941,2929,
2918,2907,2895,2884,2872,2861,2849,2838,
2826,2814,2803,2791,2779,2767,2756,2744,
2732,2720,2708,2696,2684,2672,2660,2648,
2636,2624,2612,2600,2588,2576,2564,2552,
2539,2527,2515,2503,2490,2478,2466,2453,
2441,2429,2416,2404,2392,2379,2367,2354,
2342,2330,2317,2305,2292,2280,2267,2255,
2242,2230,2217,2205,2192,2179,2167,2154,
2142,2129,2117,2104,2092,2079,2066,2054,
2041,2029,2016,2003,1991,1978,1966,1953,
1941,1928,1916,1903,1890,1878,1865,1853,
1840,1828,1815,1803,1790,1778,1765,1753,
1741,1728,1716,1703,1691,1679,1666,1654,
1642,1629,1617,1605,1592,1580,1568,1556,
1543,1531,1519,1507,1495,1483,1471,1459,
1447,1435,1423,1411,1399,1387,1375,1363,
1351,1339,1328,1316,1304,1292,1281,1269,
1257,1246,1234,1223,1211,1200,1188,1177,
1166,1154,1143,1132,1120,1109,1098,1087,
1076,1065,1054,1043,1032,1021,1010,999,
989,978,967,956,946,935,925,914,
904,893,883,873,862,852,842,832,
822,812,802,792,782,772,762,752,
743,733,723,714,704,695,685,676,
667,657,648,639,630,621,612,603,
594,585,577,568,559,551,542,534,
525,517,508,500,492,484,476,468,
460,452,444,436,428,421,413,406,
398,391,383,376,369,362,355,347,
340,334,327,320,313,307,300,293,
287,281,274,268,262,256,250,244,
238,232,226,220,215,209,204,198,
193,188,182,177,172,167,162,157,
153,148,143,139,134,130,125,121,
117,113,109,105,101,97,93,89,
86,82,79,75,72,69,65,62,
59,56,53,51,48,45,43,40,
38,35,33,31,29,27,25,23,
21,19,17,16,14,13,11,10,
9,8,7,6,5,4,3,3,
2,2,1,1,0,0,0,0,
0,0,0,1,1,1,2,2,
3,4,4,5,6,7,8,10,
11,12,14,15,17,18,20,22,
24,26,28,30,32,34,36,39,
41,44,46,49,52,55,58,61,
64,67,70,73,77,80,84,87,
91,95,99,103,107,111,115,119,
123,127,132,136,141,146,150,155,
160,165,170,175,180,185,190,196,
201,206,212,218,223,229,235,241,
247,253,259,265,271,277,284,290,
297,303,310,317,323,330,337,344,
351,358,365,372,380,387,394,402,
409,417,425,432,440,448,456,464,
472,480,488,496,504,513,521,529,
538,546,555,563,572,581,590,599,
608,616,625,635,644,653,662,671,
681,690,700,709,719,728,738,748,
757,767,777,787,797,807,817,827,
837,847,857,868,878,888,899,909,
919,930,941,951,962,972,983,994,
1005,1016,1026,1037,1048,1059,1070,1081,
1093,1104,1115,1126,1137,1149,1160,1171,
1183,1194,1206,1217,1229,1240,1252,1263,
1275,1287,1298,1310,1322,1333,1345,1357,
1369,1381,1393,1405,1417,1429,1441,1453,
1465,1477,1489,1501,1513,1525,1537,1550,
1562,1574,1586,1598,1611,1623,1635,1648,
1660,1672,1685,1697,1710,1722,1734,1747,
1759,1772,1784,1797,1809,1822,1834,1847,
1859,1872,1884,1897,1909,1922,1934,1947,
1959,1972,1985,1997,2010,2022,2035,2048,
};




void setup() {
  Serial.begin(9600); 
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  //display.clearDisplay();
  display.display();

  dma.begin(true); // allocate the DMA channel first
  
  SIM_SCGC2 |= SIM_SCGC2_DAC0; // enable DAC clock
  DAC0_C0 = DAC_C0_DACEN | DAC_C0_DACRFS; // enable the DAC module, 3.3V reference
  // slowly ramp up to DC voltage, approx 1/4 second
  for (int16_t i=0; i<2048; i+=8) {
    *(int16_t *)&(DAC0_DAT0L) = i;
    delay(1);
  }
  
  // set the programmable delay block to trigger DMA requests
  SIM_SCGC6 |= SIM_SCGC6_PDB; // enable PDB clock
  PDB0_IDLY = 0; // interrupt delay register
  
  
  // PDB_PERIOD has to be calculated depending on 
  // (1) desired output frequency
  // (2) selected cpu clock frequency 
  // For example: frequency = 1kHz and the LUT has 4096 entries 
  // (1)  4096 x 1000 = 4096000 triggers per second. 
  // (2) Teensy 3.2 at 96MHz = internal bus clock to 48MHz. 
  // Divide these 48MHz by 4096000 and you get 11.718 as the divider. 
  // Subtract 1 because the PDB includes also a full cycle for a 0 value
  PDB0_MOD = 47-1; // modulus register, sets period to 1Khz
  //PDB0_MOD = 32768-1; // modulus register, sets period to 1hz (for debugging)
  
  
  PDB0_SC = PDB_CONFIG | PDB_SC_LDOK; // load registers from buffers
  PDB0_SC = PDB_CONFIG | PDB_SC_SWTRIG; // reset and restart
  PDB0_CH0C1 = 0x0101; // channel n control register?

  // alter the buffer to 0.4-2.4V as per LDD-1000L specification
  static volatile uint16_t adjusted_sinetable[ sizeof(sinetable)/sizeof(uint16_t)]; // malloc(sizeof(sinetable), sizeof(uint16_t));
  //float factor =  2048.0 / 3.3; // 2048 == 3.3v
  float amplitude_scale = (2.2 - 0.6) / (3.3 - 0.0);  // (add an extra 200mV to avoid any clipping)
  uint16_t shift = (uint16_t)(1.15 * 2048.0 / 3.3);

  int lut_length = sizeof(sinetable)/sizeof(uint16_t);
  for (uint16_t i=0; i < lut_length; i++) {
    adjusted_sinetable[i] = (int16_t)(sinetable[i]*amplitude_scale) + shift;
  }
  
  dma.sourceBuffer(adjusted_sinetable, sizeof(sinetable));
  dma.destination(*(volatile uint16_t *)&(DAC0_DAT0L));
  dma.triggerAtHardwareEvent(DMAMUX_SOURCE_PDB);
  dma.enable();
  pinMode(A0, INPUT);

  display.cp437(true);         // Use full 256 char 'Code Page 437' font

  /*display.clearDisplay();
  display.drawBitmap(64,16, logo_bmp, 128, 32, 1);*/
  delay(2000);
}

void loop() {
  
  /*Serial.print("sizeof(sinetable): " );
  Serial.println(sizeof(sinetable));
  Serial.print("bias: " );
  Serial.println((0.5*2048.0 / 3.5));
  
  delay(1000);*/
  
  draw_status();
  delay(2000);
}




void draw_status(void) {
  // read temperature
  int adcTempValue = analogRead(A0);
  int signalA = analogRead(A1);

  // voltage divider with 3k resistor 1st
  //float thermistorR = 3000.0 * adcTempValue / (1023.0 - adcTempValue);
  
  float fixedR = 3000.0;
  float thermistorR = fixedR*1023.0/adcTempValue - fixedR;
  
  float b_coeff = 3455.0;
  // thermistor resistance @25C is 10k
  float steinhart = (1.0/b_coeff) * log(thermistorR / 10000.0);     //  1/B * ln(R/Ro)
  steinhart += 1.0 / (25.0 + 273.15); // + (1/To)
  float temp = 1.0 / steinhart - 273.15;   // Invert and convert to Celsius
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0,0);
  display.setTextColor(WHITE);
  display.print("Temp: ");
  display.print(temp);
  display.println("\xF8 C");
  display.print("ADC: ");
  display.println(adcTempValue);
  display.print("Intensity Ix: ");
  display.println(signalA);



  
  //display.print((char)248);
  display.display();
  
  /*display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(WHITE);        // Draw white text
  display.setCursor(0,0);             // Start at top-left corner
  display.println(F("Hello, world!"));

  display.setTextColor(BLACK, WHITE); // Draw 'inverse' text
  display.println(3.141592);

  display.setTextSize(2);             // Draw 2X-scale text
  display.setTextColor(WHITE);
  display.print(F("0x")); display.println(0xDEADBEEF, HEX);*

  display.display();*/
}
