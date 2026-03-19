import pyautogui
import time

# 1. Gera a lista com os 48 horários
horarios = []
for periodo in ['AM', 'PM']:
    for hora in [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        for minuto in ['00', '30']:
            horarios.append((str(hora), minuto, periodo))

print("O script vai começar em 5 segundos. Clique na ÚNICA caixa de 'Hora' disponível!")
time.sleep(5)

# 2. Loop de preenchimento e criação de novas linhas
for i, (h, m, p) in enumerate(horarios):
    
    # --- CONTORNO PARA O NÚMERO 1 ---
    if h == '1':
        pyautogui.write('2')      
        time.sleep(0.1)           
        pyautogui.press('up')     
    else:
        pyautogui.write(h)        
        
    time.sleep(0.1) 
    pyautogui.press('tab')    
    
    pyautogui.write(m)        
    time.sleep(0.1)
    pyautogui.press('tab')    
    
    pyautogui.write(p)        
    time.sleep(0.1)
    
    # Se NÃO for o último horário, cria a nova linha
    if i < len(horarios) - 1:
        
        pyautogui.press('tab') # Pula pro X
        pyautogui.press('tab') # Pula pro Adicionar
        
        pyautogui.press('enter')
        time.sleep(0.5) 
        
        # --- A CORREÇÃO DO ÚLTIMO HORÁRIO ---
        # len(horarios) é 48. Quando i == 46, estamos criando a 48ª e última linha.
        # Aqui o botão de adicionar SOME. O foco do navegador costuma cair no 'X' da nova linha.
        if i == len(horarios) - 2: 
            # Damos UM passo a menos para trás para não pular para a linha de cima!
            pyautogui.hotkey('shift', 'tab') # Do X, volta pro AM/PM
            pyautogui.hotkey('shift', 'tab') # Volta pro Minuto
            pyautogui.hotkey('shift', 'tab') # Volta pra Hora
        else:
            # Caminho reverso normal quando o botão "Adicionar" ainda existe
            pyautogui.hotkey('shift', 'tab') # Do Adicionar, volta pro X
            pyautogui.hotkey('shift', 'tab') # Volta pro AM/PM
            pyautogui.hotkey('shift', 'tab') # Volta pro Minuto
            pyautogui.hotkey('shift', 'tab') # Volta pra Hora
        
        time.sleep(0.1)

print("Todos os 48 horários foram configurados com sucesso!")