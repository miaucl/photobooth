#include <FastLED.h>
#include <FlashAsEEPROM.h>

#define ONBOARD_DATA_PIN 7
#define ONBOARD_CLOCK_PIN 8

#define NUM_LEDS 47
#define DATA_PIN 1
#define LED_TYPE WS2812B
#define BRIGHTNESS 255
#define SATURATION 255


#define BUTTON 3
#define BUTTON_ALT 4
#define BUTTON_LED 13

#define LIGHT_ON 2

#define WARM_WHITE CRGB(0xE1A024)

#define MASTER_INIT_UNDEFINED_BOOT_TIME 30000

CRGB onboard_dotstar[1];
CRGB leds[NUM_LEDS];

enum RGBMODE {
  ROLLING_RAINBOW, 
  RAINBOW, 
  MAROON_COLOR, 
  SALMON_COLOR, 
  HOT_CINNAMON_COLOR, 
  GOLDEN_TAINOI_COLOR, 
  VERDUN_GREEN_COLOR,
  PASTEL_GREEN_COLOR,
  MALIBU_COLOR,
  CONGRESS_BLUE_COLOR,
  CORNFLOWER_BLUE_COLOR,
  LAVENDER_COLOR,
  FLIRT_COLOR,
  WHITE, 
  BLACK
};
int mode = BLACK;

bool master_initializing = true;
bool first_press = true;
bool next_mode = false;
bool light_on = false;


void setup() 
{
  Serial.begin(9600);

  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(BUTTON_ALT, INPUT_PULLUP);
  pinMode(BUTTON_LED, OUTPUT);
  pinMode(LIGHT_ON, INPUT_PULLDOWN);


  FastLED.addLeds<APA102, ONBOARD_DATA_PIN, ONBOARD_CLOCK_PIN, GBR>(onboard_dotstar, 1);
  onboard_dotstar[0] = CRGB::Black;

  FastLED.addLeds<LED_TYPE, DATA_PIN, GRB>(leds, NUM_LEDS);
  fill_solid(leds, NUM_LEDS, CRGB::Black);

  // Remove for AVR (required for SAMD)
  if (EEPROM.isValid()) mode = EEPROM.read(0x00);

  FastLED.show();

  while (millis() < MASTER_INIT_UNDEFINED_BOOT_TIME) 
  {
    master_init();
    FastLED.show();
  }
}

void loop() 
{
  // button pressed
  next_mode = !(digitalRead(BUTTON) && digitalRead(BUTTON_ALT));

  // light overwrite
  light_on = digitalRead(LIGHT_ON);

  if (next_mode)
  {
    if (first_press)
    {
      Serial.println("Next mode");
      onboard_dotstar[0] = CRGB::White;
      if (++mode > BLACK) mode = ROLLING_RAINBOW;
      EEPROM.write(0x00, mode);

       // Remove for AVR (required for SAMD)
      EEPROM.commit(); // Careful, not too often!

      first_press = false;
    }
  } 
  else 
  {
    // reset button
    first_press = true;
    // reset onboard led
    onboard_dotstar[0] = CRGB::Black;
  }

  
  if (light_on) 
  {
    if (master_initializing) master_init();
    else
    {
      digitalWrite(BUTTON_LED, HIGH);
      fill_solid(leds, NUM_LEDS, WARM_WHITE);
    }
  }
  else
  {
    master_initializing = false;
    digitalWrite(BUTTON_LED, LOW);
    switch (mode)
    {
      case ROLLING_RAINBOW: rolling_rainbow(); break;
      case RAINBOW: rainbow(); break;
      case MAROON_COLOR: color(3); break;
      case SALMON_COLOR: color(11); break;
      case HOT_CINNAMON_COLOR: color(21); break;
      case GOLDEN_TAINOI_COLOR: color(42); break;
      case VERDUN_GREEN_COLOR: color(72); break;
      case PASTEL_GREEN_COLOR: color(110); break;
      case MALIBU_COLOR: color(211); break;
      case CONGRESS_BLUE_COLOR: color(214); break;
      case CORNFLOWER_BLUE_COLOR: color(231); break;
      case LAVENDER_COLOR: color(197); break;
      case FLIRT_COLOR: color(313); break;
      case WHITE: fill_solid(leds, NUM_LEDS, WARM_WHITE); break;
      default: fill_solid(leds, NUM_LEDS, CRGB::Black); break;
    }
  }

  FastLED.show();
}

#define INIT_STEP 5
#define INIT_MIN_BRIGHTNESS_FADE 220
int init_i = 0;
bool init_dir = true;
long init_millis = 0;

void master_init()
{
  if (millis() - init_millis < INIT_STEP) return;
  init_millis = millis();

  CRGB w = WARM_WHITE;
  w = w.fadeLightBy(init_i);
  for (int i = 0; i < NUM_LEDS; i++) leds[i] = w;
  if (init_dir) init_i++;
  if (!init_dir) init_i--;
  if (init_i == INIT_MIN_BRIGHTNESS_FADE) init_dir = false;
  if (init_i == 0) init_dir = true;
}

#define RAINBOW_STEP 50
int rainbow_i = 0;
long rainbow_millis = 0;

void rainbow()
{
  if (millis() - rainbow_millis < RAINBOW_STEP) return;
  rainbow_millis = millis();

  for (int i = 0; i < NUM_LEDS; i++) leds[i] = CHSV(rainbow_i * 255 / NUM_LEDS, SATURATION, BRIGHTNESS);
  rainbow_i++;
  if (rainbow_i == NUM_LEDS) rainbow_i = 0;
}

#define ROLLING_RAINBOW_STEP 100
int rolling_rainbow_i = 0;
long rolling_rainbow_millis = 0;

void rolling_rainbow()
{
  if (millis() - rolling_rainbow_millis < ROLLING_RAINBOW_STEP) return;
  rolling_rainbow_millis = millis();

  for (int i = 0; i < NUM_LEDS; i++) leds[i] = CHSV((i - rolling_rainbow_i) * 255 / NUM_LEDS, SATURATION, BRIGHTNESS);
  if (++rolling_rainbow_i == NUM_LEDS) rolling_rainbow_i = 0;
}

#define COLOR_STEP 100
#define COLOR_WIDTH 3
#define COLOR_THRESHOLD ((COLOR_WIDTH + 1) / 2)

int color_i = 0;
long color_millis = 0;
int color_mode = 0;

void color(int color)
{
  fill_solid(leds, NUM_LEDS, CRGB::Black);

  long m = millis();
  if (m - color_millis < 10) return;
  if (m - color_millis >= COLOR_STEP) 
  {
    color_millis = m;
    if (++color_i >= NUM_LEDS) 
    {
      color_i = 0;
      color_mode++;
    }
  }

  int millis_delta = color_millis - m;

  switch (color_mode)
  {
    case 0:
    case 1:
      single_color(color, color_i, millis_delta);
      break;
    case 2:
    case 3:
      rev_single_color(color, color_i, millis_delta);
      break;
    case 4:
    case 5:
      single_color(color, color_i, millis_delta);
      rev_single_color(color, color_i, millis_delta);
      break;
    case 6:
    case 7:
      single_color(color, color_i, millis_delta);
      single_color(color, color_i + NUM_LEDS / 2, millis_delta);
      break;
    case 8:
    case 9:
      rev_single_color(color, color_i, millis_delta);
      rev_single_color(color, color_i + NUM_LEDS / 2, millis_delta);
      break;
    case 10:
    case 11:
      single_color(color, color_i, millis_delta);
      single_color(color, color_i + NUM_LEDS / 4, millis_delta);
      single_color(color, color_i + NUM_LEDS / 2, millis_delta);
      single_color(color, color_i + NUM_LEDS / 4 * 3, millis_delta);
      break;
    case 12:
    case 13:
      rev_single_color(color, color_i, millis_delta);
      rev_single_color(color, color_i + NUM_LEDS / 4, millis_delta);
      rev_single_color(color, color_i + NUM_LEDS / 2, millis_delta);
      rev_single_color(color, color_i + NUM_LEDS / 4 * 3, millis_delta);
      break;
    // Reset
    default: color_mode = 0;
  }
}

void single_color(int color, int color_i, float millis_delta)
{
  for (int i = 0; i < NUM_LEDS; i++) 
  {
    // Inter step delta
    float interstep_delta = millis_delta/COLOR_STEP;
    // Position diff wrap around
    float position_delta = i - color_i + interstep_delta;
    if (position_delta > NUM_LEDS/2) position_delta -= NUM_LEDS;
    if (position_delta < -NUM_LEDS/2) position_delta += NUM_LEDS;
    position_delta = fabs(position_delta);
    // Normalized capped peak diff
    float peak_delta = max((COLOR_THRESHOLD - position_delta) / COLOR_THRESHOLD, 0.f);

    // Set color
    leds[i] += CHSV(color, SATURATION, peak_delta * BRIGHTNESS / COLOR_THRESHOLD);
  }
}

void rev_single_color(int color, int color_i, float millis_delta)
{
  for (int i = 0; i < NUM_LEDS; i++) 
  {
    // Inter step delta
    float interstep_delta = -millis_delta/COLOR_STEP;
    // Position diff wrap around
    float position_delta = i - (NUM_LEDS - 1 - color_i) + interstep_delta;
    if (position_delta > NUM_LEDS/2) position_delta -= NUM_LEDS;
    if (position_delta < -NUM_LEDS/2) position_delta += NUM_LEDS;
    position_delta = fabs(position_delta);
    // Normalized capped peak diff
    float peak_delta = max((COLOR_THRESHOLD - position_delta) / COLOR_THRESHOLD, 0.f);

    // Set color
    leds[i] += CHSV(color, SATURATION, peak_delta * BRIGHTNESS / COLOR_THRESHOLD);
  }
}