'''
Máquina de lavar simplificada

    a.  Este projeto deverá utilizar leds para mostrar os sinais de saída do controlador e
        botões de pressão (Push buttons) ou liga/desliga para enviar comandos ao
        controlador;

    b.  Um botão será utilizado para ligar/desligar a máquina;

    c.  Neste projeto, o equipamento conterá 3 opções de escolha quanto às condições da
        roupa a ser lavada: normal, suja e muito suja;

    d.  Haverá também leds com indicação da fase em que o processo de lavagem se
        encontra:

        i.Molho;
        ii.Lavagem;
        iii.Enxágue;
        iv.Centrifugação;

    e.  Uma vez que a máquina comece a lavagem é possível adiantar a fase em que ela
        esteja. Para isso deverá haver um botão do tipo push button;

    f.  Essa máquina simplificada possui dois motores, um para rodar o seu eixo principal
        e outro para jogar água fora, na fase de Enxágue. O acionamento desses motores
        deverá ser indicado por leds;

    g.  Há ainda um sensor de água para informar o sistema de controle que a máquina
        está com água, pois as fases de Molho e Lavagem só funcionam se houver água
        dentro da máquina;

    h.  O funcionamento da máquina
        i.  Começa pela fase de Molho, em que a máquina é abastecida com
            água até atingir o nível mínimo aceitável. Para ligar a entrada de água
            há um válvula elétrica que deve ser acionada. O sabão é adicionado
             manualmente;
        ii. Na fase de Lavagem, a máquina aciona o seu motor principal. Nesta
            fase a roupa dentro da máquina é agitada de um lado para outro
            continuamente;
        iii.Na fase de Enxágue, a máquina joga toda a água fora e em seguida
            reabastece a máquina com água, liga o motor principal por uns
            instantes e em seguida joga toda a água fora novamente;
        iv. Na centrifugação, o motor da bomba que joga água fora é acionado,
            bem como o motor principal, em alta velocidade. Portanto, o motor
            principal tem duas velocidades: normal e alta, o que requer duas
            saídas que devem ser sinalizadas em leds.
        v.  A duração das fases de Molho e de Enxágue variam de acordo com a
            opção escolhida para as condições da roupa:

            |===================================================|
            | Fase        |                                     |
            |             |         Condições da roupa          |
            |             | ------------------------------------|
            |             |  Normal |    Suja    | Muito Sujo   |
            |             |   (min) |   (min)    |   (min)      |
            |---------------------------------------------------|
            |   Enxágue   |   2     |     4      |     6        |
            |---------------------------------------------------|
            |     Molho   |   1     |     2      |     3        |
            |===================================================|

'''

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
    # criação da lista  para inicialização dos leds como saída
    listaPinosLeds = [led_centrifuga, led_motor_velocidade_alta, led_motor_velocidade_normal,
                      led_fase_centrifuga, led_fase_enxague, led_fase_lavagem, led_fase_molho, led_principal]

    configura_pinos_saida(listaPinosLeds)

    # criação da lista  para inicialização dos botoes como entrada
    listaPinosBotoes = [botao_avanca_fase, botao_roupa_muito_suja,
                        botao_roupa_suja, botao_roupa_normal, botao_liga_desliga]

    configura_pinos_entrada(listaPinosBotoes)


# função que verifica se a máquina está ou não ligada
# caso esteja ligada, ela é desligada e vice-versa
def liga_lavadora(self):
    global ligado
    # caso esteja ligada
    if ligado is True:
        ligado = False
        reset()
    # caso esteja desligada
    else:
        ligado = True

    global condicao_definida

    # reseta condição da roupa
    if condicao_definida is True:
        condicao_definida = False

    # altera estado led
    GPIO.output(led_principal, ligado)


# funçao que reseta as variaveis e apaga os leds

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


# funçao para apagar os leds das respectivas fases quando elas encerrarem
# e iniciar a contagem do tempo da próxima fase

def apaga_leds_fases(fase_atual):
    # fase da lavagem
    if (fase_atual == 1):
        apaga_led_lavagem()
        global inicio_enxague
        inicio_enxague = time.time()

    # fase do enxague
    elif (fase_atual == 2):
        apaga_led_enxague()
        global inicio_centrifuga
        inicio_centrifuga = time.time()

    # fase da centrifuga
    elif (fase_atual == 3):
        apaga_led_centrifuga()


#funçao para apagar o led da fase molho
def apaga_led_molho():
    GPIO.output(led_fase_molho, False)

#funçao para apagar o led da fase lavagem
def apaga_led_lavagem():
    GPIO.output(led_fase_lavagem, False)
    GPIO.output(led_motor_velocidade_normal, False)

#funçao para apagar o led da fase  enxague
def apaga_led_enxague():
    GPIO.output(led_fase_enxague, False)
    GPIO.output(led_motor_velocidade_normal, False)
    GPIO.output(led_centrifuga, False)

#funçao para apagar o led da fase centrifuga
def apaga_led_centrifuga():
    GPIO.output(led_fase_centrifuga, False)
    GPIO.output(led_motor_velocidade_alta, False)
    GPIO.output(led_centrifuga, False)

# função que avança a fase da máquina
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

    # adição do evento para detecção do acionamento do botao liga-desliga
    GPIO.add_event_detect(botao_liga_desliga, GPIO.RISING,
                          callback=liga_lavadora, bouncetime=300)

    # adição do evento para detecção do acionamento do botao de avançar a fase
    GPIO.add_event_detect(botao_avanca_fase, GPIO.RISING,
                          callback=avanca, bouncetime=300)

    # loop principal
    while 1:

        while (ligado):

            global condicao_definida

            # condicional que verifica se o usuário
            # definiu ou não a condição da roupa a ser lavada
            if condicao_definida is False:

                global condicao_roupa

                # caso o usuário insira a condição de roupa normal
                if GPIO.input(botao_roupa_normal) == True:
                    condicao_roupa = 0

                    # pisca o led de água 3x e deixa aceso
                    for x in range(3):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)

                # caso o usuário insira a condição de roupa normal
                elif GPIO.input(botao_roupa_suja):
                    condicao_roupa = 1

                    # pisca o led de água 5x e deixa aceso
                    for x in range(5):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)

                # caso o usuário insira a condição
                elif GPIO.input(botao_roupa_muito_suja):
                    condicao_roupa = 2

                    # pisca o led 7x e deixa aceso
                    for x in range(7):
                        GPIO.output(led_agua, True)
                        time.sleep(1)
                        GPIO.output(led_agua, False)
                        time.sleep(1)
                    GPIO.output(led_agua, True)
                # caso a variavel possua algum valor, altera a variável
                if (condicao_roupa < 3):
                    condicao_definida = True

            # caso a condição ja esteja definida
            if condicao_definida is True:
                global fase_atual

                # Maquina de lavar ociosa
                if fase_atual == None:
                    fase_atual = 0

                    # registra o tempo de inicio da fase do molho
                    inicio_molho = time.time()

                # Fase de molho
                elif fase_atual == 0:

                    GPIO.output(led_fase_molho, True)

                    # registra o tempo de fim quando entra no loop
                    fim_molho = time.time()


                    # verifica o tempo do molho de acordo com a condição da roupa
                    tempo_molho = tempo_enxague_molho[condicao_roupa][1]

                    # checa se o tempo decorrido já é igual ao do predefinido
                    if fim_molho - inicio_molho >= tempo_molho:
                        apaga_led_molho()

                        inicio_lavagem = time.time()
                        fase_atual += 1

                # Fase de lavagem
                elif fase_atual == 1:

                    #define o tempo da lavagem
                    tempo_lavagem = 10

                    GPIO.output(led_fase_lavagem, True)
                    GPIO.output(led_motor_velocidade_normal, True)

                    # registra o tempo quando entra no loop
                    fim_lavagem = time.time()

                    # verifica se o tempo decorrido ja é igual ao definido
                    if fim_lavagem - inicio_lavagem >= tempo_lavagem:
                        apaga_led_lavagem()
                        global inicio_enxague
                        inicio_enxague = time.time()
                        fase_atual += 1

                elif fase_atual == 2:

                    # verifica o tempo do enxague de acordo com a condição da roupa
                    tempo_total_enxague = tempo_enxague_molho[condicao_roupa][0]

                    # define o tempo do despejo dagua
                    tempo_despejo = tempo_total_enxague / 3
                    # define o tempo do enchimento da máquina
                    tempo_enchimento = tempo_total_enxague / 3

                    GPIO.output(led_fase_enxague, True)

                    # entra no primeiro despejo
                    if primeiro_despejo is True:

                        GPIO.output(led_centrifuga, True)
                        GPIO.output(led_agua, False)
                        tempo_atual_despejo = time.time()

                        # checa se o tempo ja foi atingido
                        if tempo_atual_despejo - inicio_enxague > tempo_despejo:
                            primeiro_despejo = False
                            enchimento = True
                            GPIO.output(led_centrifuga, False)

                    # Começa a fase de enchimento no enxágue
                    if enchimento is True:
                        GPIO.output(led_motor_velocidade_normal, True)
                        GPIO.output(led_agua, True)

                        # checa se o tempo do enchimento ja foi atingido
                        tempo_atual_enchimento = time.time()
                        if tempo_atual_enchimento - inicio_enxague > (tempo_despejo + tempo_enchimento):
                            enchimento = False
                            segundo_despejo = True
                            GPIO.output(led_motor_velocidade_normal, False)

                    # entra no segundo despejo
                    if segundo_despejo is True:
                        GPIO.output(led_centrifuga, True)
                        GPIO.output(led_agua, False)
                        tempo_atual_despejo = time.time()

                        # checa se o tempo decorrido já atingiu o definido
                        if tempo_atual_despejo - inicio_enxague > tempo_total_enxague:
                            segundo_despejo = False
                            GPIO.output(led_centrifuga, False)
                            GPIO.output(led_fase_enxague, False)

                            fase_atual += 1
                            global inicio_centrifuga
                            inicio_centrifuga = time.time()



                # entra na fase de centrifugação
                elif fase_atual == 3:

                    # define o tempo da
                    tempo_centrifuga = 10

                    # liga os leds da centrifugação
                    GPIO.output(led_fase_centrifuga, True)
                    GPIO.output(led_centrifuga, True)
                    GPIO.output(led_motor_velocidade_alta, True)

                    fim_centrifuga = time.time()

                    # verifica se o tempo decorrido já atingiu o definido
                    if (fim_centrifuga - inicio_centrifuga >= tempo_centrifuga):
                        reset()


if __name__ == '__main__':
    setup()
    main()
