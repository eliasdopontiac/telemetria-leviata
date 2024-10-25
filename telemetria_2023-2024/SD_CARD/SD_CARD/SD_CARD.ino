#include "FS.h"
#include "SD.h"
#include "SPI.h"

#define SD_CS       4

File myFile;
unsigned long previousMillis = 0;
const long interval = 1000;
int counter = 1;

int getNextFileNumber(String baseFilename) {
  int nextFileNumber = 1;
  while (SD.exists(baseFilename + String(nextFileNumber) + ".txt")) {
    nextFileNumber++;
  }
  return nextFileNumber;
}

void setup()
{
  Serial.begin(115200);
  SPI.begin();
  if (SD.begin(SD_CS)) 
  {
    // Encontra o próximo número disponível para o nome do arquivo
    int nextFileNumber = getNextFileNumber("leitura");
    
    // Cria o nome do próximo arquivo "leitura"
    String filename = "leitura
