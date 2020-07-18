print("[INFO] Loading LAC")
from LAC import LAC
lac = LAC(mode = 'seg')
lac.load_customization('../my_dict.txt', sep = '\n')
print("[INFO] LAC Loaded")
import pkuseg
tokenizer = pkuseg.pkuseg(model_name = 'medicine', user_dict= '../my_dict.txt')
print("[INFO] pkuseg Loaded")
while True:
    s = input()
    a1 = lac.run(s)
    a2 = tokenizer.cut(s)
    print(a1)
    print(a2)