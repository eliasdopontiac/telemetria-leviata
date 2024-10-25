//Creamos una variable de tipo entero
int lectura = 0;

void setup() {
  //Iniciamos la comunicación serial
  Serial.begin(9600);
}

void loop() {
  //Tomamos la lectura analógica del pin al cual conectamos
  //la señal de nuestro pot y la guadamos en una variable
  lectura = analogRead(0);

  //Imprimimos por monitor serie el valor 
  Serial.println(lectura);

  delay(500);
}
