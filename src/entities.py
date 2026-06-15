import pygame, math, os
from settings import GRAVITY, NET_WY, SINGLES_XMIN, SINGLES_XMAX, WHITE
from utils import project, depth_scale

# =====================================================================
# SYSTEM DŹWIĘKU
# =====================================================================
pygame.mixer.init()
BOUNCE_SOUND = None
HIT_SOUND = None # <-- REZERWACJA ZMIENNEJ

if os.path.exists("bounce.wav"):
    try:
        BOUNCE_SOUND = pygame.mixer.Sound("bounce.wav")
        BOUNCE_SOUND.set_volume(0.6)
    except Exception: pass

# WCZYTANIE DŹWIĘKU RAKIETY (Zmień "racket_hit.wav" na swoją nazwę pliku!)
if os.path.exists("racket_hit.wav"):
    try:
        HIT_SOUND = pygame.mixer.Sound("racket_hit.wav")
        HIT_SOUND.set_volume(0.5) # Głośność na 50%
    except Exception: pass

# =====================================================================
# ANIMACJA RAKIETY
# =====================================================================
class RacketAnim:
    """
    Obsługuje animację rakiety tenisowej w czasie.
    Wyświetla wyłącznie poprawnie załadowane tekstury graficzne.
    """

    _HIT = [          
        (-35, 0.00),
        (-78, 0.16),  
        (105, 0.42),  
        (150, 0.70),  
        (-35, 1.00),  
    ]
    _SERVE_TROPHY = [ 
        (-35, 0.00),
        (-95, 0.55),  
        (-95, 1.00),
    ]
    _SERVE_SWING = [  
        (-95, 0.00),
        (-160, 0.30), 
        ( 25, 0.58),  
        (-35, 1.00),  
    ]
    _IDLE_ANGLE = -35

    def __init__(self, is_ai: bool = False, image_path: str = None):
        """
        Inicjuje parametry animacji rakiety.
        
        Parametry:
            is_ai: Czy rakieta należy do bota?
            image_path: Ścieżka do grafiki spritowej rakiety.
        """
        self.is_ai = is_ai
        self.state  = 'idle'
        self.t      = 0.0
        self.speed  = 0.062     
        self.angle  = self._flip(-35)
        self.image_orig = None

        if image_path and os.path.exists(image_path):
            try:
                raw = pygame.image.load(image_path).convert_alpha()
                self.image_orig = pygame.transform.scale(raw, (36, 84))
            except Exception:
                pass

    def _flip(self, angle):
        """Koryguje kąt rakiety dla perspektywy AI (z drugiej strony siatki)."""
        return (angle + 180) % 360 if self.is_ai else angle

    def trigger_hit(self):
        """Zaczyna animację zwykłego odbicia."""
        self.state = 'hit'; self.t = 0.0

    def trigger_serve_toss(self):
        """Zaczyna animację podrzutu przy serwie."""
        self.state = 'serve_trophy'; self.t = 0.0

    def trigger_serve_swing(self):
        """Zaczyna wymach i uderzenie po podrzucie do serwu."""
        if self.state == 'serve_trophy':
            self.state = 'serve_swing'; self.t = 0.0

    def update(self):
        """
        Oblicza upływ czasu i przypisuje nowy stan rotacji dla rakiety.
        Wywoływane w każdej klatce przed rysowaniem.
        """
        if self.state == 'idle':
            target = self._flip(self._IDLE_ANGLE)
            diff = (target - self.angle + 540) % 360 - 180  
            self.angle += diff * 0.10
            return

        self.t = min(1.0, self.t + self.speed)

        frames = {'hit': self._HIT,
                  'serve_trophy': self._SERVE_TROPHY,
                  'serve_swing':  self._SERVE_SWING}.get(self.state)
        if frames:
            self.angle = self._flip(self._interp(frames, self.t))

        if self.t >= 1.0 and self.state != 'serve_trophy':
            self.state = 'idle'

    def _interp(self, frames, t):
        """Funkcja pomocnicza – interpoluje kąt w zależności od progresu w czasie t."""
        if t <= frames[0][1]:  return frames[0][0]
        if t >= frames[-1][1]: return frames[-1][0]
        for i in range(len(frames)-1):
            a0,t0 = frames[i]; a1,t1 = frames[i+1]
            if t0 <= t <= t1:
                f = (t-t0)/(t1-t0) if t1 != t0 else 0
                return a0 + (a1-a0)*f
        return frames[-1][0]

    def draw(self, screen, hand_x: int, hand_y: int, scale: float):
        """
        Wyświetla model na ekranie. 
        Jeśli plik PNG z obrazkiem rakiety nie załadował się poprawnie, funkcja nie robi nic.
        """
        self.update()
        if self.image_orig:
            self._draw_image(screen, hand_x, hand_y, scale)

    def _draw_image(self, screen, hx, hy, sc):
        """Prywatna funkcja renderująca teksturę graficzną rakiety."""
        # Mnożnik bazowy wielkości rakiet (1.5 = o 50% większa)
        racket_scale = sc * 1.5
        
        iw = max(1, int(36 * racket_scale))
        ih = max(1, int(84 * racket_scale))
        
        img_s   = pygame.transform.smoothscale(self.image_orig, (iw, ih))
        rotated = pygame.transform.rotate(img_s, -self.angle + 90)
        rw, rh  = rotated.get_size()
        rad   = math.radians(self.angle)
        
        # Poprawiony pivot obrotu dłoni uwzględniający nowe wymiary
        off_x = int( math.cos(rad) * ih * 0.30)
        off_y = int(-math.sin(rad) * ih * 0.30)
        
        screen.blit(rotated, (hx + off_x - rw//2, hy + off_y - rh//2))


class Ball:
    def __init__(self): self.reset()

    def reset(self):
        self.wx=0.5; self.wy=0.85
        self.vx=0.0; self.vy=0.0
        self.height=0.0; self.vheight=0.0; self.active=False
        self.phase='idle'
        self.last_hitter=None       
        self.ai_bounces=0           
        self.player_bounces=0       
        self.just_bounced=False

    def start_toss(self, wx, wy):
        self.wx=wx; self.wy=wy
        self.height=0.0; self.vheight=0.068
        self.vx=0.0; self.vy=0.0; self.active=True
        self.phase='toss'
        self.ai_bounces=0; self.player_bounces=0
        self.last_hitter=None; self.just_bounced=False

    def execute_serve(self, server_is_player, target_box, spin, base_power):
        if HIT_SOUND:
            HIT_SOUND.play()

        xmin,xmax,ymin,ymax = target_box
        cx = (xmin+xmax)/2 + spin*(xmax-xmin)*0.35
        cx = max(xmin+0.03, min(xmax-0.03, cx))
        cy = (ymin+ymax)/2  

        MAX_H    = 0.068**2 / (2*GRAVITY)        
        t_ratio  = min(1.0, self.height / (MAX_H*0.5))
        srv_power= 0.32 + 0.68 * t_ratio * base_power   

        VY_MAX = 0.018; VY_MIN = 0.007
        avg_vy = VY_MIN + (VY_MAX-VY_MIN) * (srv_power-0.32)/0.68

        dist_cy = abs(cy - self.wy)
        t_total = dist_cy / max(avg_vy, 0.001)
        
        # OPÓR POWIETRZA (Kompensacja przy uderzeniu)
        d = 0.99 
        sum_drag = (1 - d**t_total) / (1 - d)
        
        self.vy = (cy - self.wy) / sum_drag
        self.vx = (cx - self.wx) / sum_drag

        if dist_cy > 0.02:
            self.vheight = dist_cy * GRAVITY / (2*avg_vy)
        else:
            self.vheight = 0.026

        dist_net = abs(NET_WY - self.wy)
        t_net    = t_total * (dist_net / max(dist_cy, 0.001))
        h_net    = self.height + self.vheight*t_net - 0.5*GRAVITY*t_net*t_net
        
        if h_net < 0.045:
            needed = (0.045 + 0.5*GRAVITY*t_net*t_net - self.height) / max(t_net, 0.01)
            self.vheight = max(self.vheight, needed+0.003)

        self.phase='serve_flight'
        self.last_hitter='player' if server_is_player else 'ai'
        self.ai_bounces=0; self.player_bounces=0
        self._clamp()

    def hit(self, hitter_wx, hitter_wy, hitter_is_player, spin, power):
        d = 0.99 # Opór powietrza
        # ---- ODTWORZENIE DŹWIĘKU UDERZENIA RAKIETĄ ----
        if HIT_SOUND:
            HIT_SOUND.play()

        if hitter_is_player:
            if spin == 0:
                target_wx = max(0.15, min(0.85, hitter_wx)) 
            elif spin == -1:
                target_wx = -0.05 if hitter_wx < 0.4 else 0.15
            elif spin == 1:
                target_wx = 1.05 if hitter_wx > 0.6 else 0.85

            target_wy = 0.05 
            avg_vy = 0.013 * max(0.8, power)
            self.vheight = 0.032 * max(0.85, power)
            self.last_hitter = 'player'
        else:
            if spin == 0:
                target_wx = max(0.15, min(0.85, hitter_wx)) 
            elif spin == -1:
                target_wx = -0.05 if hitter_wx < 0.4 else 0.15
            elif spin == 1:
                target_wx = 1.05 if hitter_wx > 0.6 else 0.85

            target_wy = 0.95 
            avg_vy = 0.012
            self.vheight = 0.030
            self.last_hitter = 'ai'

        # Obliczanie uderzenia z uwzględnieniem oporu powietrza
        dist_y = abs(target_wy - self.wy)
        t_total = dist_y / max(avg_vy, 0.001)
        sum_drag = (1 - d**t_total) / (1 - d)
        
        self.vy = (target_wy - self.wy) / sum_drag
        self.vx = (target_wx - self.wx) / sum_drag

        self.ai_bounces = 0
        self.player_bounces = 0
        self.phase = 'rally'
        
        # Przelot nad siatką
        dist_net = abs(NET_WY - self.wy)
        t_net    = t_total * (dist_net / max(dist_y, 0.001))
        h_net    = self.height + self.vheight*t_net - 0.5*GRAVITY*t_net*t_net
        
        if h_net < 0.038:
            needed   = (0.038 + 0.5*GRAVITY*t_net*t_net - self.height) / max(t_net, 0.01)
            self.vheight = max(self.vheight, needed+0.003)
            
        self._clamp()

    def _clamp(self):
        spd=math.hypot(self.vx,self.vy)
        MAX=0.035
        if spd>MAX: self.vx*=MAX/spd; self.vy*=MAX/spd

    def update(self):
        if not self.active: return None
        prev_h = self.height
        self.wx += self.vx
        self.wy += self.vy
        self.height += self.vheight
        self.vheight -= GRAVITY
        
        # Opor powietrza traci na szybkosci
        self.vx *= 0.99
        self.vy *= 0.99
        
        self.just_bounced = False

        if prev_h > 0.002 and self.height <= 0:
            self.height = 0
            self.just_bounced = True
            self.vheight = abs(self.vheight) * 0.58
            if self.vheight < 0.003: self.vheight = 0

            if BOUNCE_SOUND:
                BOUNCE_SOUND.play()
            if self.phase == 'toss':
                self.active = False; return ('toss_fault',)

            if self.phase == 'serve_flight':
                return ('serve_bounce', self.wx, self.wy)

            if self.phase == 'rally':
                if self.wy < NET_WY:   
                    if self.last_hitter == 'ai' and self.ai_bounces == 0:
                        self.active = False; return ('out', 'ai')
                        
                    self.ai_bounces += 1
                    if self.ai_bounces == 1:
                        if self.wx < SINGLES_XMIN or self.wx > SINGLES_XMAX or self.wy < 0.0:
                            self.active = False
                            return ('out', self.last_hitter) 
                    else:
                        self.active = False
                        return ('double_bounce', 'ai') 
                else:                  
                    if self.last_hitter == 'player' and self.player_bounces == 0:
                        self.active = False; return ('out', 'player')

                    self.player_bounces += 1
                    if self.player_bounces == 1:
                        if self.wx < SINGLES_XMIN or self.wx > SINGLES_XMAX or self.wy > 1.0:
                            self.active = False
                            return ('out', self.last_hitter)
                    else:
                        self.active = False
                        return ('double_bounce', 'player')

        if self.wy < -0.05 or self.wy > 1.05 or self.wx < -0.15 or self.wx > 1.15:
            self.active = False
            if self.wy < NET_WY: 
                return ('baseline_out', 'ai') if self.ai_bounces > 0 else ('hit_out', self.last_hitter)
            else: 
                return ('baseline_out', 'player') if self.player_bounces > 0 else ('hit_out', self.last_hitter)

        return None

    def draw_shadow(self, screen):
        if not self.active: return
        sc = depth_scale(self.wy)
        sx, sy = project(self.wx, self.wy)
        
        # Obliczanie wielkości cienia
        hf = max(0.0, 1.0 - self.height * 1.5)
        sw = max(3, int(20 * sc * hf))
        sh = max(2, int(9 * sc * hf))
        
        # BEZPIECZNA PRZEZROCZYSTOŚĆ: wymuszamy wartość od 0 do 255
        sa = max(0, min(255, int(200 * hf))) 
        
        if sw > 2 and sa > 8:
            surf = pygame.Surface((sw * 2 + 2, sh * 2 + 2), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (0, 0, 0, sa), (0, 0, sw * 2, sh * 2))
            screen.blit(surf, (int(sx) - sw, int(sy) - sh))
            
        # Celownik, gdy piłka jest wysoko
        if self.height > 0.10:
            rr = max(5, int(14 * sc))
            # Zabezpieczenie przezroczystości również dla celownika
            ra = max(0, min(190, int(self.height * 360))) 
            rs = pygame.Surface((rr * 2 + 4, rr * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(rs, (255, 255, 100, ra), (rr + 2, rr + 2), rr, 2)
            screen.blit(rs, (int(sx) - rr - 2, int(sy) - rr - 2))
    def draw_ball(self, screen):
        if not self.active: return
        sc=depth_scale(self.wy); sx,sy=project(self.wx,self.wy)
        br=max(4,int(7*sc))
        bx=int(sx); by=int(sy-self.height*62)   
        if self.height>0.04:
            steps=int(self.height*50)
            for i in range(0,steps,5):
                a=int(120*(1-i/max(steps,1)))
                ds=pygame.Surface((3,3),pygame.SRCALPHA)
                ds.fill((200,255,100,a)); screen.blit(ds,(bx-1,int(sy)-i))
        pygame.draw.circle(screen,(20,70,0),(bx+1,by+1),br)
        pygame.draw.circle(screen,(200,255,35),(bx,by),br)
        pygame.draw.circle(screen,(230,255,130),(bx-br//3,by-br//3),max(1,br//3))


class Player:
    """
    Logiczna klasa przetrzymująca stan i statystyki podmiotu gracza. 
    Zarządza m.in. aktywowaniem buffów, prędkością, renderingiem ciała i rakietą.
    """
    def __init__(self, wx, wy, char=None, image_path=None, racket_image_path=None, is_ai=False, ai_speed=0.009):
        """
        Tworzy nowego awatara na korcie.
        
        Parametry:
            wx: Współrzędna logiczna punktu startu osi X.
            wy: Współrzędna logiczna punktu startu osi Y.
            char: Struktura opisująca dane wybranej postaci.
            image_path: Ścieżka do grafiki gracza.
            racket_image_path: Ścieżka do przypisanej rakiety postaci.
            is_ai: Flaga określająca bota.
            ai_speed: Mnożnik limitujący prędkość bota.
        """
        self.wx=wx; self.wy=wy; self.is_ai=is_ai; self.ai_speed=ai_speed
        
        self.base_speed = 0.012
        self.base_range = 0.070
        
        self.ult_name = ""
        self.ult_type = ""
        self.ult_dur = 0
        self.ult_active = False
        self.ult_timer = 0
        self.ult_cooldown = 0
        
        if char:
            self.speed=char['speed']; self.hit_power=char['hit_power']
            self.hit_range=char['hit_range']
            self.base_speed = self.speed
            self.base_range = self.hit_range
            self.color=char['color']; self.shirt=char['shirt']
            
            self.ult_name = char.get('ult_name', "")
            self.ult_type = char.get('ult_type', "")
            self.ult_dur = char.get('ult_dur', 0)
            
            self.ult_sound = None
            ult_file = char.get('ult_sound', "")
            if ult_file and os.path.exists(ult_file):
                try:
                    self.ult_sound = pygame.mixer.Sound(ult_file)
                    self.ult_sound.set_volume(0.7) 
                except Exception: pass
        else:
            self.speed=self.base_speed; self.hit_power=1.0; self.hit_range=self.base_range
            self.color=(200,80,80) if is_ai else (80,140,220)
            self.shirt=(230,110,110) if is_ai else (110,170,240)
            self.ult_sound = None 
            
        self.image=None
        if image_path and os.path.exists(image_path):
            try:
                img=pygame.image.load(image_path).convert_alpha()
                self.image=pygame.transform.smoothscale(img,(50,50))
            except: pass
            
        self.racket = RacketAnim(is_ai=self.is_ai, image_path=racket_image_path)

    def activate_ult(self):
        """
        Sprawdza stan gotowości i aktywuje unikatową umiejętność gracza. 
        """
        if not self.is_ai and not self.ult_active and self.ult_cooldown <= 0:
            self.ult_active = True
            self.ult_timer = self.ult_dur

            if self.ult_sound:
                self.ult_sound.play()

            if self.ult_type == "speed":
                self.speed = self.base_speed * 1.8  
            elif self.ult_type == "range":
                self.hit_range = self.base_range * 3.0  

    def update_ult(self, dt):
        """
        Przelicza licznik czasu trwania ultów oraz czas odnowienia po użyciu.
        """
        if self.ult_active:
            self.ult_timer -= dt
            if self.ult_timer <= 0:
                self.ult_active = False
                self.ult_cooldown = 15000  
                self.speed = self.base_speed
                self.hit_range = self.base_range
        elif self.ult_cooldown > 0:
            self.ult_cooldown -= dt

    def move(self, dx, dy, scale=1.0):
        """Przemieszcza gracza na podstawie wejścia."""
        nx=self.wx+dx*self.speed*scale
        ny=self.wy+dy*self.speed*scale
        if self.is_ai: ny=max(0.03,min(NET_WY-0.03,ny))
        else:          ny=max(NET_WY+0.03,min(0.97,ny))
        self.wx=max(0.02,min(0.98,nx)); self.wy=ny

    def move_ai(self, ddx, ddy):
        """Przemieszcza AI na podstawie wejścia z logiki bota."""
        nx=self.wx+ddx*self.ai_speed
        ny=self.wy+ddy*self.ai_speed
        ny=max(0.03,min(NET_WY-0.03,ny))
        self.wx=max(0.02,min(0.98,nx)); self.wy=ny

    def draw(self, screen):
        """
        Renderuje postać, cień i zarządza rysowaniem przypisanej animacji rakiety.
        """
        ai_scale_mod = 1.6 if self.is_ai else 1.0
        sc = depth_scale(self.wy) * ai_scale_mod
        
        sx,sy=int(project(self.wx,self.wy)[0]),int(project(self.wx,self.wy)[1])
        
        # Cień gracza
        pygame.draw.ellipse(screen,(0,50,0),(sx-int(14*sc),sy-int(4*sc),int(28*sc),int(8*sc)))
        
        if self.image:
            # Obrazek (sprite)
            iw,ih=int(50*sc),int(50*sc)
            screen.blit(pygame.transform.smoothscale(self.image,(iw,ih)),(sx-iw//2,sy-ih))
        else:
            # Rysowanie proceduralne ciała (gdy brak obrazka)
            pygame.draw.rect(screen,(240,240,240),(sx-int(7*sc),sy-int(5*sc),int(5*sc),int(14*sc)))
            pygame.draw.rect(screen,(240,240,240),(sx+int(2*sc),sy-int(5*sc),int(5*sc),int(14*sc)))
            pygame.draw.rect(screen,self.shirt,(sx-int(9*sc),sy-int(22*sc),int(18*sc),int(18*sc)),border_radius=3)
            pygame.draw.circle(screen,(245,200,160),(sx,sy-int(28*sc)),int(8*sc))
            pygame.draw.arc(screen,self.color,(sx-int(8*sc),sy-int(36*sc),int(16*sc),int(16*sc)),0,math.pi,max(1,int(3*sc)))
            
        # Tuta usunąłem 6 linii kodu, które rysowały starą zbugowaną statyczną rakietę!
        
        # Etykieta nad graczem (P1 / AI)
        lf=pygame.font.SysFont("Arial",max(10,int(11*sc)),bold=True)
        lb=lf.render("AI" if self.is_ai else "P1",True,WHITE)
        
        y_offset = int(48 * sc) if self.is_ai else int(42 * sc)
        screen.blit(lb,(sx-lb.get_width()//2,sy-y_offset))
        
        # Rysowanie właściwej animowanej rakiety
        hx = sx + int(15 * sc) if not self.is_ai else sx - int(15 * sc)
        hy = sy - int(15 * sc)
        self.racket.draw(screen, hx, hy, sc)