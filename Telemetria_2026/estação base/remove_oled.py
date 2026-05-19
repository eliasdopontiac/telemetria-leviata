
import os, re

file_path = r'Telemetria_2026\estação base\LoRa Base\Firmware_Base_LoRa.ino'

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

code = re.sub(r'#include <Wire\.h>\n#include <Adafruit_GFX\.h>\n#include <Adafruit_SSD1306\.h>', '', code)
code = re.sub(r'// --- PINOS OLED.*?Adafruit_SSD1306 display\(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RST\);', '', code, flags=re.DOTALL)
code = re.sub(r'    // Inicializa o OLED.*?display\.display\(\);\n    \}', '', code, flags=re.DOTALL)
code = re.sub(r'        display\.clearDisplay\(\); display\.setCursor\(0,0\);\n        display\.println\("FALHA LORA"\); display\.display\(\);', '', code)
code = re.sub(r'    display\.clearDisplay\(\);\n    display\.setCursor\(0, 0\);\n    display\.println\("BASE LORA PRONTA"\);\n    display\.println\("Aguardando barco\.\.\."\);\n    display\.display\(\);', '', code)
code = re.sub(r'                // Atualiza OLED.*?display\.display\(\);', '', code, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

