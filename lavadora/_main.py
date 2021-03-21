import RPi.GPIO as GPIO
import time
from setup import *

# leds
led_centrifuga = 29
led_motor_velocidade_alta = 31
led_motor_velocidade_normal = 7
led_fase_centrifuga = 11
led_fase_enxague = 13
led_fase_lavagem = 15
led_fase_molho = 19
led_principal = 21

# botoes
botao_liga_desliga = 18
botao_roupa_normal = 16
botao_roupa_suja = 12
botao_roupa_muito_suja = 10
botao_avanca_fase = 8

# |---------------------|
# |      variaveis      |
# |---------------------|

# estado da maquina
ligado = False

lavagem_em_curso = False


condicao_definida = False

# normal = 0, suja = 1, muito suja = 2
condicao_roupa = 0

# tempo de enxague e molho em s, para teste
tempo_enxague_molho = [(20, 10), (40, 20), (60, 30)]


# None = ociosa, 0 = molho, 1 = lavagem, 2 = enxague, 3 = centrifuga
fase_atual = 0


def setup():
    listaPinosLeds = [led_centrifuga, led_motor_velocidade_alta, led_motor_velocidade_normal,
                      led_fase_centrifuga, led_fase_enxague, led_fase_lavagem, led_fase_molho, led_principal]

    configura_pinos_saida(listaPinosLeds)

    listaPinosBotoes = [botao_avanca_fase, botao_roupa_muito_suja,
                        botao_roupa_suja, botao_roupa_normal, botao_liga_desliga]

    configura_pinos_entrada(listaPinosBotoes)


def reset():
    global condicao_roupa
    global fase_atual
    global ligado
    global lavagem_em_curso

    ligado = False
    GPIO.output(led_principal, False)
    condicao_roupa = 0
    lavagem_em_curso = False
    fase_atual = 4


def liga_lavadora(_self):

    global ligado
    global lavagem_em_curso

    if ligado is True:

        reset()
        print("desligado")

    else:
        GPIO.output(led_principal, True)
        ligado = True
        lavagem_em_curso = True
        print("ligado")


def define_condicao():

    global condicao_roupa

    global fase_atual
    fase_atual = 0


def molho(condicao_roupa):

    global fase_atual
    fase_atual = 1

    print("molho")
    print(condicao_roupa)

    tempo_molho = tempo_enxague_molho[condicao_roupa][1]
    print(tempo_molho)

    GPIO.output(led_fase_molho, True)
    time.sleep(tempo_molho)
    GPIO.output(led_fase_molho, False)


def lavagem():

    tempo_lavagem = 5      # 5 segundos de lavagem

    GPIO.output(led_fase_lavagem, True)
    GPIO.output(led_motor_velocidade_normal, True)

    time.sleep(tempo_lavagem)
    GPIO.output(led_motor_velocidade_normal, False)
    GPIO.output(led_fase_lavagem, False)

    global fase_atual
    fase_atual = 2


def enxague(condicao_roupa):

    global tempo_enxague_molho
    tempo_enxague = tempo_enxague_molho[condicao_roupa][0]
    GPIO.output(led_fase_enxague, True)
    time.sleep(tempo_enxague)
    GPIO.output(led_fase_enxague, False)

    global fase_atual
    fase_atual = 3


def centrifuga():

    GPIO.output(led_fase_centrifuga, True)
    GPIO.output(led_motor_velocidade_alta, True)
    GPIO.output(led_centrifuga, True)

    # debug
    time.sleep(3)
    print("centrifuga")
    global lavagem_em_curso
    lavagem_em_curso = False

    GPIO.output(led_fase_centrifuga, False)
    GPIO.output(led_motor_velocidade_alta, False)
    GPIO.output(led_centrifuga, False)


def inicia_processo(condicao_roupa):

    while(lavagem_em_curso == True):
        if fase_atual == 0:
            molho(condicao_roupa)

        elif fase_atual == 1:
            lavagem()

        elif fase_atual == 2:
            enxague(condicao_roupa)

        elif fase_atual == 3:
            centrifuga()


def avanca(self):
    global fase_atual
    if fase_atual > 0 and fase_atual < 4:
        fase_atual = fase_atual + 1


def main():

    try:
        GPIO.add_event_detect(botao_liga_desliga, GPIO.RISING,
                              callback=liga_lavadora, bouncetime=300)

        GPIO.add_event_detect(botao_avanca_fase, GPIO.RISING,
                              callback=avanca, bouncetime=300)

        while 1: 

            while ligado is True:
                global condicao_roupa

                while (condicao_definida is False):

                    if GPIO.input(botao_roupa_normal) == True:
                        condicao_roupa = 0
                    
                    elif GPIO.input(botao_roupa_suja) == True:
                        condicao_roupa = 1

                    elif GPIO.input(botao_roupa_muito_suja) == True:
                        condicao_roupa = 2
                    
                    if condicao_roupa < 3:
                        global condicao_definida
                        condicao_definida = True


            inicia_processo(condicao_roupa)

    except KeyboardInterrupt:
        GPIO.cleanup()


if __name__ == '__main__':
    setup()
    main()
