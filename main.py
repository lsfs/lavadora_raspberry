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
led_agua = 33

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
condicao_roupa = 3

# tempo de enxague e molho em s, para teste
tempo_enxague_molho = [(20, 10), (40, 20), (60, 30)]

# None = ociosa, 0 = molho, 1 = lavagem, 2 = enxague, 3 = centrifuga
fase_atual = None

# Condicoes de tempo
inicio_enxague = 0
inicio_centrifuga = 0


def setup():
    listaPinosLeds = [led_centrifuga, led_motor_velocidade_alta, led_motor_velocidade_normal,
                      led_fase_centrifuga, led_fase_enxague, led_fase_lavagem, led_fase_molho, led_principal]

    configura_pinos_saida(listaPinosLeds)

    listaPinosBotoes = [botao_avanca_fase, botao_roupa_muito_suja,
                        botao_roupa_suja, botao_roupa_normal, botao_liga_desliga]

    configura_pinos_entrada(listaPinosBotoes)


def liga_lavadora(self):
    global ligado
    if ligado is True:
        ligado = False
        reset()

    else:
        ligado = True

    global condicao_definida

    if condicao_definida is True:
        condicao_definida = False

    GPIO.output(led_principal, ligado)


def reset():
    global condicao_definida
    condicao_definida = False

    global condicao_roupa
    condicao_roupa = 3

    global fase_atual
    fase_atual = None

    GPIO.output(led_principal, False)

    apaga_led_molho()
    apaga_led_lavagem()
    apaga_led_enxague()
    apaga_led_centrifuga()


def apaga_leds_fases(fase_atual):
    if (fase_atual == 1):
        apaga_led_lavagem()
        global inicio_enxague
        inicio_enxague = time.time()

    elif (fase_atual == 2):
        apaga_led_enxague()
        global inicio_centrifuga
        inicio_centrifuga = time.time()

    elif (fase_atual == 3):
        apaga_led_centrifuga()


def apaga_led_molho():
    GPIO.output(led_fase_molho, False)


def apaga_led_lavagem():
    GPIO.output(led_fase_lavagem, False)
    GPIO.output(led_motor_velocidade_normal, False)


def apaga_led_enxague():
    GPIO.output(led_fase_enxague, False)
    GPIO.output(led_motor_velocidade_normal, False)
    GPIO.output(led_centrifuga, False)


def apaga_led_centrifuga():
    GPIO.output(led_fase_centrifuga, False)
    GPIO.output(led_motor_velocidade_alta, False)
    GPIO.output(led_centrifuga, False)


def avanca(self):
    global fase_atual
    if fase_atual > 0:

        if fase_atual < 3:
            apaga_leds_fases(fase_atual)
            fase_atual += 1
        else:
            global ligado
            ligado = False
            reset()


def main():
    # variaveis locais
    inicio_molho = 0
    inicio_lavagem = 0

    primeiro_despejo = True
    enchimento = False
    segundo_despejo = False

    GPIO.add_event_detect(botao_liga_desliga, GPIO.RISING,
                          callback=liga_lavadora, bouncetime=300)

    GPIO.add_event_detect(botao_avanca_fase, GPIO.RISING,
                          callback=avanca, bouncetime=300)
    contador = 0
    while 1:
        while (ligado):
            # print("ligado")

            global condicao_definida

            if condicao_definida is False:

                global condicao_roupa

                if GPIO.input(botao_roupa_normal) == True:
                    condicao_roupa = 0

                    # pisca o led 3x e deixa aceso
                    for x in range(3):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)

                elif GPIO.input(botao_roupa_suja):
                    condicao_roupa = 1

                    # pisca o led 5x e deixa aceso
                    for x in range(5):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)

                elif GPIO.input(botao_roupa_muito_suja):
                    condicao_roupa = 2

                    # pisca o led 7x e deixa aceso
                    for x in range(7):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)

                if (condicao_roupa < 3):
                    condicao_definida = True

            if condicao_definida is True:
                global fase_atual

                # Maquina de lavar ociosa
                if fase_atual == None:
                    fase_atual = 0

                    inicio_molho = time.time()

                # Fase de molho
                elif fase_atual == 0:

                    GPIO.output(led_fase_molho, True)

                    fim_molho = time.time()

                    tempo_molho = tempo_enxague_molho[condicao_roupa][1]

                    if fim_molho - inicio_molho >= tempo_molho:
                        apaga_led_molho()

                        inicio_lavagem = time.time()
                        fase_atual += 1

                # Fase de lavagem
                elif fase_atual == 1:

                    tempo_lavagem = 10

                    GPIO.output(led_fase_lavagem, True)
                    GPIO.output(led_motor_velocidade_normal, True)

                    fim_lavagem = time.time()

                    if fim_lavagem - inicio_lavagem >= tempo_lavagem:
                        apaga_led_lavagem()
                        global inicio_enxague
                        inicio_enxague = time.time()
                        fase_atual += 1

                elif fase_atual == 2:

                    tempo_total_enxague = tempo_enxague_molho[condicao_roupa][0]

                    tempo_despejo = tempo_total_enxague / 3
                    tempo_enchimento = tempo_total_enxague / 3

                    GPIO.output(led_fase_enxague, True)

                    if primeiro_despejo is True:

                        GPIO.output(led_centrifuga, True)
                        GPIO.output(led_agua, False)
                        tempo_atual_despejo = time.time()

                        if tempo_atual_despejo - inicio_enxague > tempo_despejo:
                            primeiro_despejo = False
                            enchimento = True
                            GPIO.output(led_centrifuga, False)

                    if enchimento is True:
                        GPIO.output(led_motor_velocidade_normal, True)
                        GPIO.output(led_agua, True)

                        tempo_atual_enchimento = time.time()
                        if tempo_atual_enchimento - inicio_enxague > (tempo_despejo + tempo_enchimento):
                            enchimento = False
                            segundo_despejo = True
                            GPIO.output(led_motor_velocidade_normal, False)

                    if segundo_despejo is True:
                        GPIO.output(led_centrifuga, True)
                        GPIO.output(led_agua, False)
                        tempo_atual_despejo = time.time()

                        if tempo_atual_despejo - inicio_enxague > tempo_total_enxague:
                            segundo_despejo = False
                            GPIO.output(led_centrifuga, False)
                            GPIO.output(led_fase_enxague, False)

                            fase_atual += 1
                            global inicio_centrifuga
                            inicio_centrifuga = time.time()




                elif fase_atual == 3:

                    tempo_centrifuga = 10

                    GPIO.output(led_fase_centrifuga, True)
                    GPIO.output(led_centrifuga, True)
                    GPIO.output(led_motor_velocidade_alta, True)

                    fim_centrifuga = time.time()

                    if (fim_centrifuga - inicio_centrifuga >= tempo_centrifuga):
                        reset()


if __name__ == '__main__':
    setup()
    main()
