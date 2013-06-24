#include <stdint.h>

const byte r1_control = 3;
const byte g1_control = 5;
const byte b1_control = 6;

const byte r2_control = 9;
const byte g2_control = 10;
const byte b2_control = 11;

unsigned int buf = 0;
byte bufPos = 0;
unsigned int dly = 5;
unsigned int random_mode = 0;
// F = light 1, C = seCond light, A = all lights
char mode = 'a';

enum _colorStates { STATE_NONE, STATE_RED, STATE_GREEN, STATE_BLUE, STATE_SPEED, SEQNO,SEQCOL,SEQDELAY, PLAYNO };
byte states = 0;
byte current[6] = {0};
byte goal[6] = {255, 200, 180, 255, 200, 180};
byte pins[6] = {0};

uint16_t numsequences = 0;
uint16_t seqIndexes[10];
uint32_t seqData[64];

void setup() {
  Serial.begin(19200);
  Serial.println("setup begin\n");
  analogWrite(r1_control, 0);
  analogWrite(g1_control, 0);
  analogWrite(b1_control, 0);
  
  pinMode(r1_control, OUTPUT);
  pinMode(g1_control, OUTPUT);
  pinMode(b1_control, OUTPUT);
  
  pins[0] = r1_control;
  pins[1] = g1_control;
  pins[2] = b1_control;

  analogWrite(r2_control, 0);
  analogWrite(g2_control, 0);
  analogWrite(b2_control, 0);
  
  pinMode(r2_control, OUTPUT);
  pinMode(g2_control, OUTPUT);
  pinMode(b2_control, OUTPUT);
  
  pins[3] = r2_control;
  pins[4] = g2_control;
  pins[5] = b2_control;
    Serial.println("setup complete\n");
}

void loop() {
  if (Serial.available()) {
    byte b = Serial.read();
    byte handled = 0;
    while (handled == 0) {
      switch(states) {
        case STATE_RED:
        case STATE_GREEN:
        case STATE_BLUE:
        case STATE_SPEED:
        case PLAYNO:
          handled = handleNumber(b);
          break;
        case SEQNO:
          handled = handleNumber(b);
          if (!handled) {
            states = SEQCOL;
            handled = 1;
          }
          break;
        case SEQCOL:
          handled = handleNumber(b);
          if (!handled) {
            if (b == ',') {
              states = SEQDELAY;
            }
            handled = 1;
          }
          break;
        case SEQDELAY:
          handled = handleNumber(b);
          if (!handled) {
            if (b == ',') {
              states = SEQCOL;
            }
            handled = 1;
          }
          break;
        default:
          handleDefault(b);
          handled = 1;
          break;
      }
    }
  }
  uint8_t bgoal = 1;
  for (int j=0; j < 6; ++j) {
    if (goal[j] != current[j]) {
      bgoal = 0;
      int dir = goal[j] - current[j];
      dir /= abs(dir);
      //Serial.print("dir "); Serial.println((short)dir);
      current[j] += dir;
      analogWrite(pins[j], current[j]);
    }
  }
  if (random_mode && bgoal) {
    for (int j=0; j < 6; ++j) {
      goal[j] = random() & 0xff;
    }
  }
  delay(dly);
}

void handleDefault(byte d) {
  switch(d) {
    case 'r': case 'R':
      states = STATE_RED;
      return;
    case 'b': case 'B':
      states = STATE_BLUE;
      return;
    case 'g': case 'G':
      states = STATE_GREEN;
      return;
    case 's': case 'S':
      states = STATE_SPEED;
      return;
    case 'n': case 'N':
      random_mode = !random_mode;
      break;
    case 'f': case 'F':  // color settings apply to first light only
    case 'c': case 'C':  // color settings apply to second light only
    case 'a': case 'A':  // color settings apply to both lights
      mode = tolower(d);
      break;
    case 'q': case 'Q': {
      Serial.print("Qr");
      Serial.print(goal[0]);
      Serial.print("g");
      Serial.print(goal[1]);
      Serial.print("b");
      Serial.print(goal[2]);
      Serial.print("s");
      Serial.println(dly);
      Serial.print("2r");
      Serial.print(goal[3]);
      Serial.print("g");
      Serial.print(goal[4]);
      Serial.print("b");
      Serial.println(goal[5]);
      break;
    }
    case 'm': case 'M':
      states = SEQNO;
      break;
    case 'p': case 'P':
      states = PLAYNO;
      break;
    case 'h': case 'H':
      Serial.println("HELP");
      Serial.println("----");
      Serial.println("rxxx - set red to xxx");
      Serial.println("gxxx - set green to xxx");      
      Serial.println("bxxx - set blue to xxx");
      Serial.println("q - Query");
      Serial.println("f=first, c=seCond,a=all lights");
      Serial.println("mx,aaa,bbbb,ccc,dddd,... - define sequence x as color aaa, delay bbbb ms, color ccc, delay dddd ms, ...");
      Serial.println("px - play sequence x.  X ranges from 0 to 9");
      break;
    default:
      return;
  }
}

byte handleNumber(byte r) {
  if (!isdigit(r)) {
    setColor();
    return 0;
  }
  buf = buf * 10 + (r-'0');
  return 1;
}

void setColor() {
  switch (states) {
    case STATE_RED:
      Serial.print("setting red to "); Serial.println(buf);
      random_mode = 0;
      if (mode == 'f' || mode == 'a') {
        goal[0] = buf;
      }
      if (mode == 'c' || mode == 'a') {
        goal[3] = buf;
      }
      break;
    case STATE_GREEN:
      Serial.print("setting green to "); Serial.println(buf);
      if (mode == 'f' || mode == 'a') {
        goal[1] = buf;
      }
      if (mode == 'c' || mode == 'a') {
        goal[4] = buf;
      }
      random_mode = 0;
      break;
    case STATE_BLUE:
      Serial.print("setting blue to "); Serial.println(buf);
      if (mode == 'f' || mode == 'a') {
        goal[2] = buf;
      }
      if (mode == 'c' || mode == 'a') {
        goal[5] = buf;
      }
      random_mode = 0;
      break;
    case STATE_SPEED:
      Serial.print("setting speed to "); Serial.println(buf);
      dly = buf;
      break;
    case SEQNO:
    case SEQCOL:
    case SEQDELAY:
    case PLAYNO:
    default:
      break;
  }
  buf = 0;
  states = STATE_NONE;
}


