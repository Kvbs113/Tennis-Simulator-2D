"""
Plik konfiguracyjny przechowujący globalne stałe, limity i bazę statystyk gry
wymagane do stabilnego zachowania we wszystkich podsystemach symulatora tenisa.
"""

WIDTH, HEIGHT = 700, 600
FPS     = 60
WHITE   = (255, 255, 255)
GRAVITY = 0.0020  

COURT_BL = (40,        HEIGHT - 50)
COURT_BR = (WIDTH - 40,  HEIGHT - 50)
COURT_TL = (155,       20)
COURT_TR = (WIDTH - 155, 20)
NET_WY       = 0.5

SINGLES_XMIN = 0.08 
SINGLES_XMAX = 0.92 
SERVICE_Y_TOP = 0.29 
SERVICE_Y_BOT = 0.75

SETS_TO_WIN   = 2      
POINT_NAMES   = ["0", "15", "30", "40"]


DIFFICULTIES = {
    "LATWY":  {"label":"ŁATWY",   "emoji":"I","color":(80,200,100),
               "desc":"Wolne AI • Dużo błędów • Dla początkujących",
               "ai_speed":0.006,"error":0.28,"deadzone":0.09,
               "aggression":0.08,"shot_scatter":0.022, "image": "assets/images/ai_latwy.png", "racket_image": "assets/images/racket_ai_latwy.png"},
    "SREDNI": {"label":"ŚREDNI",  "emoji":"II","color":(220,200,60),
               "desc":"Normalne tempo • Okazjonalne błędy • Wyzwanie",
               "ai_speed":0.009,"error":0.10,"deadzone":0.04,
               "aggression":0.13,"shot_scatter":0.010, "image": "assets/images/ai_sredni.png", "racket_image": "assets/images/racket_ai_sredni.png"},
    "TRUDNY": {"label":"TRUDNY",  "emoji":"III","color":(230,140,40),
               "desc":"Szybkie AI • Rzadkie błędy • Dla zaawansowanych",
               "ai_speed":0.013,"error":0.03,"deadzone":0.02,
               "aggression":0.17,"shot_scatter":0.005, "image": "assets/images/ai_trudny.png", "racket_image": "assets/images/racket_ai_trudny.png"},
    "EKSPERT":{"label":"EKSPERT", "emoji":"IIII","color":(220,60,60),
               "desc":"Bezbłędne AI • Agresywna gra • Nieludzkie tempo",
               "ai_speed":0.018,"error":0.00,"deadzone":0.008,
               "aggression":0.22,"shot_scatter":0.001, "image": "assets/images/ai_ekspert.png", "racket_image": "assets/images/racket_ai_ekspert.png"},
}
DIFF_KEYS = ["LATWY", "SREDNI", "TRUDNY", "EKSPERT"]


CHARACTERS = {
    "NOWICJUSZ":{"label":"NOWICJUSZ","emoji":"I","desc":"Wolny • Słabe uderzenia • Mały zasięg",
                 "color":(100,150,240),"shirt":(140,185,255),
                 "speed":0.009,"hit_power":0.85,"hit_range":0.115,
                 "stat_spd":1,"stat_pow":1,"stat_rng":1, "image": "assets/images/nowicjusz.png", "racket_image": "assets/images/racket_nowicjusz.png",
                 "ult_name": "Nietykalność", "ult_type": "invincible", "ult_dur": 5000,
                 "ult_sound": "assets/sounds/ult_nowicjusz.wav"}, 
                 
    "AMATOR":   {"label":"AMATOR","emoji":"II","desc":"Przeciętna prędkość • Normalne uderzenia",
                 "color":(70,200,110),"shirt":(100,235,145),
                 "speed":0.011,"hit_power":0.97,"hit_range":0.135,
                 "stat_spd":2,"stat_pow":2,"stat_rng":2, "image": "assets/images/amator.png", "racket_image": "assets/images/racket_amator.png",
                 "ult_name": "Nitro", "ult_type": "speed", "ult_dur": 3000,
                 "ult_sound": "assets/sounds/ult_amator.wav"}, 
                 
    "PRO":      {"label":"PRO","emoji":"III","desc":"Szybki • Mocne uderzenia • Dobry zasięg",
                 "color":(230,160,30),"shirt":(255,195,70),
                 "speed":0.013,"hit_power":1.10,"hit_range":0.155,
                 "stat_spd":3,"stat_pow":3,"stat_rng":3, "image": "assets/images/pro.png", "racket_image": "assets/images/racket_pro.png",
                 "ult_name": "Dotlenienie", "ult_type": "speed", "ult_dur": 5000,
                 "ult_sound": "assets/sounds/ult_pro.wav"}, 
                 
    "MISTRZ":   {"label":"MISTRZ","emoji":"IIII","desc":"Błyskawiczny • Potężne uderzenia • Ogromny zasięg",
                 "color":(210,55,55),"shirt":(255,100,100),
                 "speed":0.016,"hit_power":1.22,"hit_range":0.175,
                 "stat_spd":4,"stat_pow":4,"stat_rng":4, "image": "assets/images/mistrz.png", "racket_image": "assets/images/racket_mistrz.png",
                 "ult_name": "Polska gurom", "ult_type": "range", "ult_dur": 5000,
                 "ult_sound": "assets/sounds/ult_mistrz.wav"}, 
}
CHAR_KEYS = ["NOWICJUSZ", "AMATOR", "PRO", "MISTRZ"]


TOURNAMENT_ROUNDS = [
    {"name": "PIERWSZE KOŁO",    "diff_key": "LATWY",   "sublabel": "Runda 1 / 4"},
    {"name": "DRUGIE KOŁO",      "diff_key": "SREDNI",  "sublabel": "Runda 2 / 4"},
    {"name": "PÓŁFINAŁ",         "diff_key": "TRUDNY",  "sublabel": "Runda 3 / 4"},
    {"name": "FINAŁ WIMBLEDONU", "diff_key": "EKSPERT", "sublabel": "Runda 4 / 4  [FINAŁ]"},
]
