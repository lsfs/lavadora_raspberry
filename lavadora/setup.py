import RPi.GPIO as GPIO


def configura_pinos_saida(listaPinos):

    GPIO.setmode(GPIO.BOARD)

    # configura os pinos como saida e desliga leds
    for pino in listaPinos:
        GPIO.setup(pino, GPIO.OUT)
        GPIO.output(pino,0)
  
def configura_pinos_entrada(listaPinos):
    for pino in listaPinos:
        GPIO.setup(pino, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
