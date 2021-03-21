import time as time

print("desligado")
start = time.time()
#end = time.time()

maior = False

while (maior is False):

    end = time.time()
    if(end - start > 10):
        print(end)
        maior = True
        print(maior)
    else:
        print(end)
        


#print(start)
#print("hello")
#time.sleep(5)
#end = time.time()
#print(end - start >= 5)
