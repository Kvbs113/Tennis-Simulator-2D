from settings import COURT_BL, COURT_BR, COURT_TL, COURT_TR

def project(wx, wy):
    """
    Rzutuje wektor pozycji absolutnej boiska z wymiarów logicznych (0.0 - 1.0) 
    na wymiar powierzchni ekranowej zachowując perspektywiczny zbieg (efekt 3D).
    
    Parametry:
        wx: Logiczna wartość X (poziom) w zakresie 0-1.
        wy: Logiczna wartość Y (pion) w zakresie 0-1.
    
    Zwraca:
        Krotka dwuelementowa ze współrzędnymi X i Y na ekranie.
    """
    lx = COURT_BL[0] + (COURT_TL[0] - COURT_BL[0]) * (1 - wy)
    rx = COURT_BR[0] + (COURT_TR[0] - COURT_BR[0]) * (1 - wy)
    ly = COURT_BL[1] + (COURT_TL[1] - COURT_BL[1]) * (1 - wy)
    ry = COURT_BR[1] + (COURT_TR[1] - COURT_BR[1]) * (1 - wy)
    return (lx + (rx - lx) * wx, ly + (ry - ly) * wx)

def depth_scale(wy): 
    """
    Kalkuluje modyfikator skali (rozmiaru na ekranie) obiektu na podstawie jego odległości w głąb mapy.
    Im wyższa wartość logiczna wy (bliżej horyzontu/krawędzi przeciwnika), tym mniejsza będzie zwrócona skala.
    
    Parametry:
        wy: Współrzędna Y obiektu na korcie.
        
    Zwraca:
        Mnożnik zmiennoprzecinkowy (float).
    """
    return 0.45 + 0.55 * wy