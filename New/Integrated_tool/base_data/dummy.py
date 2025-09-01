import json

# inicio
año = 2024
mes = 8
dia = 10
hora = 5
minuto = 48

index = 0
while index < 288:

    with open(f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json', 'r') as fp:
        meas = json.load(fp)
        
    meas['P_LV0102'] = meas['P_LV0102']*2
    
    
    with open(f'dummy_2/{año}_{mes}_{dia}_{hora}_{minuto}.json', 'w', encoding='utf-8') as f:
        json.dump(meas, f, ensure_ascii=False, indent=2)    
    
    minuto += 5
    if minuto >= 60:
        minuto -= 60
        hora += 1
        if hora >= 24:
            hora = 0
            dia += 1
    
    index += 1