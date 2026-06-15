from settings import SINGLES_XMIN, SINGLES_XMAX, SETS_TO_WIN, POINT_NAMES, SERVICE_Y_TOP, SERVICE_Y_BOT

class MatchScore:
    """
    Klasa przechowująca stan obecnego spotkania i logikę punktacji (punkty, gemy, sety).
    """
    def __init__(self, sets_to_win=None):
        """
        Inicjuje nowy system punktacji dla meczu.
        
        Parametry:
            sets_to_win: Liczba wygranych setów potrzebnych do wygrania meczu.
        """
        self._sets_to_win = sets_to_win if sets_to_win is not None else SETS_TO_WIN

        self.points       = [0, 0]   
        self.games        = [0, 0]   
        self.sets         = [0, 0]   
        self.set_history  = []       
        self.tiebreak     = False
        self.tb_pts       = [0, 0]
        self.server       = 0        
        self.serve_attempt= 1        
        self.match_over   = False
        self.match_winner = None
        self.game_pt_idx  = 0        

    def get_service_box(self):
        """
        Oblicza współrzędne poprawnego pola serwisowego bazując na stronie serwującej.
        
        Zwraca:
            Krotkę współrzędnych pola: (xmin, xmax, ymin, ymax)
        """
        deuce = (self.game_pt_idx % 2 == 0)
        
        if self.server == 0:
            xmin, xmax = 0.125, 0.875
            return (xmin, 0.5, 0.16, 0.50) if deuce else (0.5, xmax, 0.16, 0.50)
        else:
            xmin, xmax = 0.11, 0.89
            ymax = 0.72
            return (xmin, 0.5, 0.50, ymax) if deuce else (0.5, xmax, 0.50, ymax)

    def get_point_display(self):
        """
        Konwertuje tablicę numeryczną punktów na reprezentację tenisową.
        
        Zwraca:
            Łańcuch znaków z wartościami punktów (np. '15-0', 'DEUCE', 'ADW').
        """
        p, a = self.points
        if self.tiebreak:
            return f"{self.tb_pts[0]}–{self.tb_pts[1]}"
        if p >= 3 and a >= 3:
            if p == a: return "DEUCE"
            return "ADW. GRACZ" if p > a else "ADW. KOMP."
        return f"{POINT_NAMES[min(p, 3)]}–{POINT_NAMES[min(a, 3)]}"

    def get_score_line(self):
        """
        Zwraca linię tekstową ze stanem gemów i setów w meczu.
        """
        return (f"Gemy: {self.games[0]}–{self.games[1]}  |  "
                f"Sety: {self.sets[0]}–{self.sets[1]}"
                + ("  [TIE-BREAK]" if self.tiebreak else ""))

    def add_point(self, winner):
        """
        Dodaje punkt wskazanemu graczowi i aktualizuje stan rozgrywki.
        
        Parametry:
            winner: Indeks wygrywającego gracza (0 = gracz, 1 = AI).
        Zwraca:
            Zwraca string wskazujący typ zakończonej fazy: 'game', 'set', 'match', lub None.
        """
        self.game_pt_idx += 1
        if self.tiebreak:
            self.tb_pts[winner] += 1
            tot = sum(self.tb_pts)
            if tot == 1 or (tot > 1 and tot % 2 == 1):
                self.server = 1 - self.server
            p, a = self.tb_pts
            if max(p, a) >= 7 and abs(p - a) >= 2:
                return self._end_game(winner)
        else:
            self.points[winner] += 1
            p, a = self.points
            if max(p, a) >= 4 and abs(p - a) >= 2:
                return self._end_game(winner)
        self.serve_attempt = 1
        return None

    def fault(self):
        """
        Rejestruje błąd serwisu.
        
        Zwraca:
            True jeśli wystąpił błąd podwójny, False w innym przypadku.
        """
        if self.serve_attempt == 1:
            self.serve_attempt = 2
            return False
        self.serve_attempt = 1
        return True

    def _end_game(self, winner):
        """
        Prywatna funkcja obsługująca logikę zamknięcia gema i przyznania go zwycięzcy.
        """
        self.games[winner] += 1
        self.points = [0, 0]; self.tb_pts = [0, 0]
        was_tb = self.tiebreak; self.tiebreak = False
        self.server = 1 - self.server; self.serve_attempt = 1; self.game_pt_idx = 0
        p, a = self.games
        if p == 3 and a == 3 and not was_tb:
            self.tiebreak = True; return 'game'
        if max(p, a) >= 3 and abs(p - a) >= 2:
            return self._end_set(winner)
        return 'game'

    def _end_set(self, winner):
        """
        Prywatna funkcja obsługująca zapis setów i weryfikująca wygraną w całym meczu.
        """
        self.set_history.append(list(self.games))
        self.sets[winner] += 1; self.games = [0, 0]
        if self.sets[winner] >= self._sets_to_win:  
            self.match_over = True; self.match_winner = winner; return 'match'
        return 'set'