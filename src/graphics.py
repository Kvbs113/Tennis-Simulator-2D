import pygame, math, sys, os
from settings import *
from utils import project


MENU_BG_IMG = None
MENU_BG_LOADED = False

def get_menu_background():
    """
    Wczytuje oraz zwraca obraz tła menu. Gwarantuje jednorazowe załadowanie obrazka.
    """
    global MENU_BG_IMG, MENU_BG_LOADED
    if not MENU_BG_LOADED:
        MENU_BG_LOADED = True
        if os.path.exists("assets/images/menu_bg.png"):
            try:
                raw = pygame.image.load("assets/images/menu_bg.png").convert()
                MENU_BG_IMG = pygame.transform.smoothscale(raw, (WIDTH, HEIGHT))
            except Exception:
                pass
    return MENU_BG_IMG

def draw_shared_background(screen, t, anim_type="green"):
    """
    Rysuje uniwersalne tło we wszystkich menu (bądź awaryjną animację siatki w razie braku pliku).
    
    Parametry:
        screen: Powierzchnia rysowania.
        t: Czas w sekundach dla animacji.
        anim_type: Styl kolorystyczny animacji tła.
    """
    bg = get_menu_background()
    if bg:
        screen.blit(bg, (0, 0))
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))
    else:
        screen.fill((8, 14, 10))
        for row in range(8):
            wy = row / 7
            p = project(0, wy); q = project(1, wy)
            if anim_type == "green":
                a = int(12 + 8 * math.sin(t + row))
                c = (0, a * 2, a)
            elif anim_type == "gold":
                a = int(20 + 15 * math.sin(t + row * 0.7))
                c = (a * 2, int(a * 1.5), 0)
            elif anim_type == "red":
                a = int(8 + 5 * math.sin(t + row))
                c = (a * 2, 0, 0)
            else:
                c = (0, 0, 0)
            pygame.draw.line(screen, c, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), 1)

def draw_court(screen, bg_image=None):
    """
    Rysuje płaszczyznę kortu z poprawnym rzutowaniem perspektywicznym.
    """
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill((55, 120, 65))
        pt_tl = project(-0.35, -0.20)
        pt_tr = project(1.35, -0.20)
        pt_br = project(1.35, 1.20)
        pt_bl = project(-0.35, 1.20)
        pygame.draw.polygon(screen, (200, 95, 55), [pt_tl, pt_tr, pt_br, pt_bl])

    if not bg_image:
        L = (245, 245, 245)
        def dl(x1, y1, x2, y2, c=L, w=2):
            a = project(x1, y1); b = project(x2, y2)
            pygame.draw.line(screen, c, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), w)
        dl(0, 0, 0, 1, w=3)
        dl(1, 0, 1, 1, w=3)
        dl(SINGLES_XMIN, 0, SINGLES_XMIN, 1)
        dl(SINGLES_XMAX, 0, SINGLES_XMAX, 1)
        dl(0, 0, 1, 0, w=4)
        dl(0, 1, 1, 1, w=4)
        dl(.5, 0, .5, NET_WY)
        dl(.5, NET_WY, .5, 1)
        
        dl(SINGLES_XMIN, SERVICE_Y_TOP, SINGLES_XMAX, SERVICE_Y_TOP)
        dl(SINGLES_XMIN, SERVICE_Y_BOT, SINGLES_XMAX, SERVICE_Y_BOT)
        
        dl(.485, 0, .515, 0, w=4)
        dl(.485, 1, .515, 1, w=4)

def draw_net(screen):
    """
    Oblicza fizykę materiału i renderuje wielowarstwową siatkę tenisową, słupki oraz detale.
    """
    N = 40; POST_H = 30; TOP_H = 22
    bot = []; top = []
    
    for i in range(N + 1):
        t = i / N
        bx, by = project(t, NET_WY)
        sag = 1 - 4 * (t - 0.5)**2
        nh = POST_H - sag * (POST_H - TOP_H)
        bot.append((int(bx), int(by)))
        top.append((int(bx), int(by) - int(nh)))
        
    for i in range(len(bot) - 1):
        pygame.draw.line(screen, (50, 30, 20), (bot[i][0] + 2, bot[i][1] + 3), (bot[i+1][0] + 2, bot[i+1][1] + 3), 4)

    poly = bot + list(reversed(top))
    net_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(net_surf, (15, 15, 15, 140), poly)
    screen.blit(net_surf, (0, 0))

    MESH = (40, 40, 40)
    for tp, bp in zip(top, bot):
        pygame.draw.line(screen, MESH, tp, bp, 1)
        
    for row in range(7):
        f = row / 6
        pts = [(bp[0], bp[1] - int((bp[1] - tp[1]) * f)) for tp, bp in zip(top, bot)]
        for j in range(len(pts) - 1): 
            pygame.draw.line(screen, MESH, pts[j], pts[j+1], 1)

    pygame.draw.line(screen, (80, 80, 80), bot[0], top[0], 6)
    pygame.draw.line(screen, (40, 40, 40), bot[0], top[0], 2)
    
    pygame.draw.line(screen, (80, 80, 80), bot[-1], top[-1], 6)
    pygame.draw.line(screen, (40, 40, 40), bot[-1], top[-1], 2) 
    
    pygame.draw.circle(screen, (60, 60, 60), top[0], 5)
    pygame.draw.circle(screen, (60, 60, 60), top[-1], 5)

    pygame.draw.lines(screen, (150, 150, 150), False, bot, 2)

    mid_idx = N // 2
    pygame.draw.line(screen, (245, 245, 245), top[mid_idx], bot[mid_idx], 4)
    pygame.draw.line(screen, (180, 180, 180), top[mid_idx], bot[mid_idx], 1) 

    pygame.draw.lines(screen, (255, 255, 255), False, top, 4)

def draw_service_box(screen, box):
    """
    Podświetla wizualnie strefę serwisu za pomocą przezroczystego koloru.
    
    Parametry:
        box: Krotka przechowująca granice docelowego pola.
    """
    xmin,xmax,ymin,ymax=box
    pts=[project(xmin,ymin),project(xmax,ymin),project(xmax,ymax),project(xmin,ymax)]
    pts=[(int(x),int(y)) for x,y in pts]
    t=pygame.time.get_ticks()/1000
    a=int(32+22*math.sin(t*3.5))
    surf=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    pygame.draw.polygon(surf,(100,255,100,a),pts)
    pygame.draw.polygon(surf,(150,255,150,110),pts,2)
    screen.blit(surf,(0,0))

def draw_serve_indicator(screen, ball):
    """
    Rysuje animowany, kolorowy wskaźnik optymalnego momentu na serwis.
    
    Parametry:
        ball: Obiekt piłki potrzebny do odczytania aktualnej wysokości.
    """
    MAX_H = 0.068**2 / (2*GRAVITY)
    BX, BY = WIDTH-32, HEIGHT//2
    BH = 200
    pygame.draw.rect(screen,(20,45,25),(BX,BY-BH//2,16,BH),border_radius=4)
    hn  = min(1.0, ball.height / (MAX_H*0.85))
    fh  = int(BH * hn)
    t_ratio = min(1.0, ball.height / (MAX_H*0.5))
    power   = 0.32 + 0.68 * t_ratio
    if power >= 0.85:    fc = (60, 230, 80)
    elif power >= 0.55:  fc = (230, 210, 40)
    else:                fc = (220, 100, 40)
    if fh > 0:
        pygame.draw.rect(screen, fc, (BX, BY+BH//2-fh, 16, fh), border_radius=3)
    z_green_y1 = BY+BH//2 - int(BH*0.98)
    z_green_y2 = BY+BH//2 - int(BH*0.55)
    pygame.draw.rect(screen,(0,200,60),(BX,z_green_y1,16,z_green_y2-z_green_y1),2)
    z_yel_y1 = z_green_y2
    z_yel_y2 = BY+BH//2 - int(BH*0.22)
    pygame.draw.rect(screen,(210,200,30),(BX,z_yel_y1,16,z_yel_y2-z_yel_y1),2)
    z_or_y1 = z_yel_y2
    z_or_y2 = BY+BH//2
    pygame.draw.rect(screen,(200,90,30),(BX,z_or_y1,16,z_or_y2-z_or_y1),2)
    sf = pygame.font.SysFont("Arial",10,bold=True)
    screen.blit(sf.render("MOC",True,(180,220,180)),(BX-2,BY-BH//2-14))
    pct = int(power*100)
    pf  = pygame.font.SysFont("Arial",11,bold=True)
    screen.blit(pf.render(f"{pct}%",True,fc),(BX-4,BY+BH//2+4))
    sl  = sf.render("MAX",True,(60,230,80))
    sl2 = sf.render("MED",True,(210,200,30))
    sl3 = sf.render("MIN",True,(200,90,30))
    screen.blit(sl, (BX-18, z_green_y1+2))
    screen.blit(sl2,(BX-18, z_yel_y1+2))
    screen.blit(sl3,(BX-18, z_or_y1+2))

def draw_stat_bar(screen, x, y, label, val, mxv, col, font):
    """
    Rysuje poziomy pasek statystyk postaci.
    """
    W=115; H=10
    ls=font.render(label,True,(130,190,130)); screen.blit(ls,(x,y))
    pygame.draw.rect(screen,(28,52,32),(x+62,y+2,W,H),border_radius=4)
    fw=int(W*val/mxv)
    if fw>0: pygame.draw.rect(screen,col,(x+62,y+2,fw,H),border_radius=4)


def draw_mode_select(screen, clock):
    """
    Renderuje i obsługuje pętlę menu wyboru trybu głównego (Turniej / Szybka gra).
    
    Zwraca:
        Klucz wybranego trybu jako string.
    """
    FT = pygame.font.SysFont("Arial", 50, bold=True)
    FM = pygame.font.SysFont("Arial", 28, bold=True)
    FS = pygame.font.SysFont("Arial", 17)
    FH = pygame.font.SysFont("Arial", 15)

    options = [
        {"key": "TOURNAMENT", "label": "TURNIEJ WIMBLEDON", "desc": "4 mecze | każdy do 2 wygranych setów", "color": (220, 180, 60)},
        {"key": "QUICK", "label": "SZYBKA GRA", "desc": "Pojedynczy mecz z wybranym poziomem AI", "color": (80, 200, 120)},
    ]
    si = 0

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w, pygame.K_LEFT, pygame.K_a): si = (si - 1) % len(options)
                if ev.key in (pygame.K_DOWN, pygame.K_s, pygame.K_RIGHT, pygame.K_d): si = (si + 1) % len(options)
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE): return options[si]["key"]
                if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                for i in range(len(options)):
                    if WIDTH//2-220 <= mx <= WIDTH//2+220 and 240+i*130 <= my <= 240+i*130+100: si = i
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, opt in enumerate(options):
                    if WIDTH//2-220 <= mx <= WIDTH//2+220 and 240+i*130 <= my <= 240+i*130+100:
                        if si == i: return opt["key"]
                        else: si = i

        t = pygame.time.get_ticks() / 1000
        draw_shared_background(screen, t, "green")

        curr_opt = options[si]
        sel_text = FS.render(f"WYBIERASZ: {curr_opt['label']} ", True, curr_opt["color"])
        screen.blit(sel_text, (WIDTH // 2 - sel_text.get_width() // 2, 140))

        pygame.draw.line(screen, (50, 90, 60), (WIDTH // 2 - 265, 170), (WIDTH // 2 + 265, 170), 2)

        for i, opt in enumerate(options):
            bx = WIDTH // 2 - 220; by = 240 + i * 130; isel = (i == si)
            
            bg_color = (22, 54, 26, 210) if isel else (12, 25, 15, 180)
            btn_surf = pygame.Surface((440, 100), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg_color, (0, 0, 440, 100), border_radius=10)
            pygame.draw.rect(btn_surf, opt["color"] if isel else (28, 55, 32), (0, 0, 440, 100), 3 if isel else 1, border_radius=10)
            screen.blit(btn_surf, (bx, by))

            ls = FM.render(opt["label"], True, opt["color"] if isel else (110, 160, 110))
            screen.blit(ls, (bx + 22, by + 18))
            ds = FS.render(opt["desc"], True, (155, 200, 155) if isel else (55, 95, 55))
            screen.blit(ds, (bx + 22, by + 60))
            if isel:
                ar = FM.render("▶", True, opt["color"])
                screen.blit(ar, (bx + 410 - ar.get_width(), by + 36))

        pygame.display.flip()


def draw_menu(screen, clock, sel_diff):
    """
    Renderuje menu wyboru stopnia trudności gry.
    
    Zwraca:
        Wybrany poziom jako string (klucz słownika).
    """
    FT=pygame.font.SysFont("Arial",50,bold=True)
    FS=pygame.font.SysFont("Arial",17)
    FD=pygame.font.SysFont("Arial",24,bold=True)
    FX=pygame.font.SysFont("Arial",14)
    FH=pygame.font.SysFont("Arial",15)
    si=DIFF_KEYS.index(sel_diff); res=None
    
    while res is None:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key in(pygame.K_UP,pygame.K_w): si=(si-1)%len(DIFF_KEYS)
                if ev.key in(pygame.K_DOWN,pygame.K_s): si=(si+1)%len(DIFF_KEYS)
                if ev.key in(pygame.K_RETURN,pygame.K_SPACE): res=DIFF_KEYS[si]
                if ev.key==pygame.K_ESCAPE: pygame.quit();sys.exit()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                for i in range(len(DIFF_KEYS)):
                    if WIDTH//2-200 <= mx <= WIDTH//2+200 and 190+i*82 <= my <= 190+i*82+68:
                        if si==i: res=DIFF_KEYS[i]
                        else: si=i
            if ev.type==pygame.MOUSEMOTION:
                mx,my=pygame.mouse.get_pos()
                for i in range(len(DIFF_KEYS)):
                    if WIDTH//2-200 <= mx <= WIDTH//2+200 and 190+i*82 <= my <= 190+i*82+68: si=i
                    
        t=pygame.time.get_ticks()/1000
        draw_shared_background(screen, t, "green")
        
        curr_opt = DIFFICULTIES[DIFF_KEYS[si]]
        sel_text = FS.render(f"WYBIERASZ: POZIOM {curr_opt['label']} ", True, curr_opt["color"])
        screen.blit(sel_text, (WIDTH // 2 - sel_text.get_width() // 2, 140))

        pygame.draw.line(screen,(50,90,60),(WIDTH//2-265,170),(WIDTH//2+265,170),2)
        
        for i,k in enumerate(DIFF_KEYS):
            d=DIFFICULTIES[k]; bx=WIDTH//2-200; by=190+i*82; isel=(i==si)
            
            bg_color = (20,50,25,210) if isel else (12,25,15,180)
            btn_surf = pygame.Surface((400, 68), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg_color, (0,0,400,68), border_radius=8)
            pygame.draw.rect(btn_surf, d["color"] if isel else (28,55,32), (0,0,400,68), 3 if isel else 1, border_radius=8)
            screen.blit(btn_surf, (bx, by))

            ls=FD.render(f"{d['emoji']}  {d['label']}",True,d["color"] if isel else (110,160,110))
            screen.blit(ls,(bx+20,by+10))
            ds=FX.render(d["desc"],True,(155,200,155) if isel else (55,95,55))
            screen.blit(ds,(bx+20,by+43))
            if isel:
                ar=FD.render("▶",True,d["color"]); screen.blit(ar,(bx+368-ar.get_width(),by+20))
                
        pygame.display.flip()
    return DIFF_KEYS[si]


def draw_char_select(screen, clock, sel_char):
    """
    Renderuje pętlę menu wyboru postaci i obsługuje wejście.
    
    Zwraca:
        Wybraną postać jako string lub 'BACK' jeśli wciśnięto ESC.
    """
    FT=pygame.font.SysFont("Arial",44,bold=True)
    FS=pygame.font.SysFont("Arial",17)
    FC=pygame.font.SysFont("Arial",22,bold=True)
    FX=pygame.font.SysFont("Arial",13)
    FH=pygame.font.SysFont("Arial",15)
    si=CHAR_KEYS.index(sel_char); res=None
    
    CW=140; CH=210; CY=220 
    TX=(WIDTH//2-((CW*4+12*3)//2))
    
    char_images = {}
    for k in CHAR_KEYS:
        img_path = CHARACTERS[k].get("image")
        if img_path and os.path.exists(img_path):
            try:
                raw = pygame.image.load(img_path).convert_alpha()
                char_images[k] = pygame.transform.smoothscale(raw, (90, 90))
            except Exception:
                char_images[k] = None
        else:
            char_images[k] = None
    
    while res is None:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit();sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key in(pygame.K_LEFT,pygame.K_a):  si=(si-1)%len(CHAR_KEYS)
                if ev.key in(pygame.K_RIGHT,pygame.K_d): si=(si+1)%len(CHAR_KEYS)
                if ev.key in(pygame.K_RETURN,pygame.K_SPACE): res=CHAR_KEYS[si]
                if ev.key==pygame.K_ESCAPE: res="BACK"
            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                for i in range(len(CHAR_KEYS)):
                    if TX+i*(CW+12) <= mx <= TX+i*(CW+12)+CW and CY <= my <= CY+CH:
                        if si==i: res=CHAR_KEYS[i]
                        else: si=i
            if ev.type==pygame.MOUSEMOTION:
                mx,my=pygame.mouse.get_pos()
                for i in range(len(CHAR_KEYS)):
                    if TX+i*(CW+12) <= mx <= TX+i*(CW+12)+CW and CY <= my <= CY+CH: si=i
                    
        t=pygame.time.get_ticks()/1000
        draw_shared_background(screen, t, "green")
        
        curr_opt = CHARACTERS[CHAR_KEYS[si]]
        sel_text = FS.render(f"WYBIERASZ: {curr_opt['label']}", True, curr_opt["color"])
        screen.blit(sel_text, (WIDTH // 2 - sel_text.get_width() // 2, 140))

        pygame.draw.line(screen,(50,90,60),(WIDTH//2-265,170),(WIDTH//2+265,170),2)
        
        for i,k in enumerate(CHAR_KEYS):
            ch=CHARACTERS[k]; cx=TX+i*(CW+12); cy=CY; isel=(i==si)
            
            bg_color = (20,50,24,210) if isel else (12,24,15,180)
            btn_surf = pygame.Surface((CW, CH), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg_color, (0,0,CW,CH), border_radius=8)
            pygame.draw.rect(btn_surf, ch["color"] if isel else (28,54,32), (0,0,CW,CH), 3 if isel else 1, border_radius=8)
            screen.blit(btn_surf, (cx, cy))
            
            img = char_images[k]
            if img:
                screen.blit(img, (cx + CW//2 - img.get_width()//2, cy + 15))
            else:
                fx=cx+CW//2; fy=cy+70
                pygame.draw.rect(screen,(235,235,235),(fx-8,fy-3,5,12))
                pygame.draw.rect(screen,(235,235,235),(fx+3,fy-3,5,12))
                pygame.draw.rect(screen,ch["shirt"],(fx-10,fy-18,20,16),border_radius=3)
                pygame.draw.circle(screen,(245,200,160),(fx,fy-24),9)
                pygame.draw.arc(screen,ch["color"],(fx-9,fy-33,18,18),0,math.pi,3)
                pygame.draw.line(screen,(80,80,80),(fx,fy-10),(fx,fy+6),3)
                pygame.draw.ellipse(screen,ch["color"],(fx-8,fy+1,16,9),2)
            
            nc=ch["color"] if isel else (100,150,100)
            ns=FC.render(ch["label"],True,nc); screen.blit(ns,(cx+CW//2-ns.get_width()//2,cy+115))
            
            bc=ch["color"] if isel else (45,105,55)
            bx2=cx+8; by2=cy+145
            draw_stat_bar(screen,bx2,by2,"SPD",ch["stat_spd"],4,bc,FX)
            draw_stat_bar(screen,bx2,by2+18,"POW",ch["stat_pow"],4,bc,FX)
            draw_stat_bar(screen,bx2,by2+36,"RNG",ch["stat_rng"],4,bc,FX)
            
            if isel:
                ar=FC.render("▼",True,ch["color"]); screen.blit(ar,(cx+CW//2-ar.get_width()//2,cy+CH+5))
                
        dsc=CHARACTERS[CHAR_KEYS[si]]["desc"]
        ds2=FS.render(dsc,True,(140,200,140)); screen.blit(ds2,(WIDTH//2-ds2.get_width()//2,CY+CH+36))
        pygame.display.flip()
    return res


def draw_tournament_bracket(screen, clock, char_key, results, current_round_idx):
    """
    Rysuje wizualizację drabinki turniejowej przed każdym meczem.
    
    Parametry:
        results: Lista zawierająca historię dotychczasowych wyników rund w turnieju.
        current_round_idx: Liczba reprezentująca indeks obecnej rundy turniejowej.
        
    Zwraca:
        String akcji ('PLAY' lub 'MENU').
    """
    FT  = pygame.font.SysFont("Arial", 38, bold=True)
    FM  = pygame.font.SysFont("Arial", 20, bold=True)
    FS  = pygame.font.SysFont("Arial", 16)
    FX  = pygame.font.SysFont("Arial", 13)
    FH  = pygame.font.SysFont("Arial", 14)
    FXB = pygame.font.SysFont("Arial", 13, bold=True)

    ch = CHARACTERS[char_key]
    START_Y = 120

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE): return "PLAY"
                if ev.key == pygame.K_ESCAPE:                   return "MENU"

        t = pygame.time.get_ticks() / 1000
        draw_shared_background(screen, t, "green")

        ts = FT.render(" WIMBLEDON ", True, (220, 180, 60))
        screen.blit(ts, (WIDTH // 2 - ts.get_width() // 2, START_Y))

        cs = FS.render(f"Twoja postać:  {ch['emoji']}  {ch['label']}", True, ch["color"])
        screen.blit(cs, (WIDTH // 2 - cs.get_width() // 2, START_Y + 46))

        pygame.draw.line(screen, (50, 80, 40), (WIDTH // 2 - 270, START_Y + 72), (WIDTH // 2 + 270, START_Y + 72), 2)

        lb = FM.render("DRABINKA TURNIEJU", True, (100, 170, 90))
        screen.blit(lb, (WIDTH // 2 - lb.get_width() // 2, START_Y + 80))

        BX = WIDTH // 2 - 268; BW = 536; BH = 68; GAP = 8
        START_BRACKET_Y = START_Y + 110
        
        for i, rd in enumerate(TOURNAMENT_ROUNDS):
            by = START_BRACKET_Y + i * (BH + GAP)
            d  = DIFFICULTIES[rd["diff_key"]]

            if i < len(results): status = results[i][0]
            elif i == current_round_idx: status = "NOW"
            else: status = "TBD"

            if status == "NOW":
                bg = (22, 55, 28, 220);  border = (220, 180, 60); bw = 3
            elif status == "W":
                bg = (14, 44, 20, 200);  border = (60,  185, 80); bw = 2
            elif status == "L":
                bg = (48, 14, 14, 200);  border = (185, 60,  60); bw = 2
            else:
                bg = (11, 20, 13, 180);  border = (28,  50,  30); bw = 1

            btn_surf = pygame.Surface((BW, BH), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, bg, (0, 0, BW, BH), border_radius=7)
            pygame.draw.rect(btn_surf, border, (0, 0, BW, BH), bw, border_radius=7)
            screen.blit(btn_surf, (BX, by))

            rname_col = {"NOW": (220, 180, 60), "W": (130, 220, 110), "L": (220, 100, 100), "TBD": (70, 110, 70)}[status]
            rn = FM.render(rd["name"], True, rname_col)
            screen.blit(rn, (BX + 12, by + 8))
            sl = FX.render(rd["sublabel"], True, (100, 150, 100))
            screen.blit(sl, (BX + 12, by + 38))

            op_col = d["color"] if status == "NOW" else (85, 135, 85)
            op = FS.render(f"vs  {d['emoji']}  {d['label']}  AI", True, op_col)
            screen.blit(op, (BX + 248, by + 22))

            if status == "W":
                bv = FXB.render("WYGRANA", True, (70, 230, 70))
                screen.blit(bv, (BX + BW - bv.get_width() - 10, by + 26))
            elif status == "L":
                bv = FXB.render("PORAŻKA", True, (230, 70, 70))
                screen.blit(bv, (BX + BW - bv.get_width() - 10, by + 26))
            elif status == "NOW":
                pulse = (math.sin(t * 3.0) + 1) / 2
                pcol  = (int(180 * pulse + 75), int(155 * pulse + 60), 30)
                bv = FM.render(">> TERAZ <<", True, pcol)
                screen.blit(bv, (BX + BW - bv.get_width() - 10, by + 24))
            else:
                bv = FX.render("...", True, (50, 80, 50))
                screen.blit(bv, (BX + BW - bv.get_width() - 10, by + 28))
    
        pygame.display.flip()


def draw_tournament_champion(screen, clock, char_key, results):
    """
    Rysuje specjalny ekran końcowy wyświetlający złote trofeum i gratulacje po wygraniu mistrzostw.
    """
    FT = pygame.font.SysFont("Arial", 50, bold=True)
    FM = pygame.font.SysFont("Arial", 24, bold=True)
    FS = pygame.font.SysFont("Arial", 17)
    FH = pygame.font.SysFont("Arial", 15)

    ch = CHARACTERS[char_key]

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_r): return

        t = pygame.time.get_ticks() / 1000
        draw_shared_background(screen, t, "gold")

        pulse = (math.sin(t * 2.0) + 1) / 2
        gold  = (int(200 + 55 * pulse), int(155 + 60 * pulse), int(15 + 35 * pulse))
        ts = FT.render("MISTRZ WIMBLEDONU!", True, gold)
        screen.blit(ts, (WIDTH // 2 - ts.get_width() // 2, 32))

        sep = FM.render("* * * * * * * * * *", True, (160, 130, 30))
        screen.blit(sep, (WIDTH // 2 - sep.get_width() // 2, 92))

        ch_s = FM.render(f"{ch['emoji']}  {ch['label']}", True, ch["color"])
        screen.blit(ch_s, (WIDTH // 2 - ch_s.get_width() // 2, 118))

        sub = FS.render("Gratulacje! Pokonałeś wszystkich 4 przeciwników!", True, (140, 220, 130))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 152))

        pygame.draw.line(screen, (100, 120, 60), (WIDTH // 2 - 265, 180), (WIDTH // 2 + 265, 180), 2)

        lbl = FM.render("WYNIKI:", True, (140, 200, 100))
        screen.blit(lbl, (WIDTH // 2 - 230, 194))

        for i, (status, round_name, diff_key) in enumerate(results):
            d    = DIFFICULTIES[diff_key]
            line = FS.render(f"  {round_name:<20}  vs  {d['label']:<8}  -->  WYGRANA", True, (100, 255, 100))
            screen.blit(line, (WIDTH // 2 - 230, 222 + i * 28))

        pygame.draw.line(screen, (100, 120, 60), (WIDTH // 2 - 265, HEIGHT - 52), (WIDTH // 2 + 265, HEIGHT - 52), 2)
        ht = FH.render("ENTER / R – Powrót do menu", True, (150, 180, 100))
        screen.blit(ht, (WIDTH // 2 - ht.get_width() // 2, HEIGHT - 34))

        pygame.display.flip()


def draw_tournament_eliminated(screen, clock, char_key, results, eliminated_round_idx):
    """
    Rysuje specjalny ekran zakończenia po wyeliminowaniu gracza z drabinki.
    """
    FT = pygame.font.SysFont("Arial", 46, bold=True)
    FM = pygame.font.SysFont("Arial", 22, bold=True)
    FS = pygame.font.SysFont("Arial", 17)
    FH = pygame.font.SysFont("Arial", 15)

    ch      = CHARACTERS[char_key]
    lost_rd = TOURNAMENT_ROUNDS[eliminated_round_idx]
    d_lost  = DIFFICULTIES[lost_rd["diff_key"]]

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE, pygame.K_r): return

        t = pygame.time.get_ticks() / 1000
        draw_shared_background(screen, t, "red")

        ts = FT.render("ODPADŁEŚ Z TURNIEJU", True, (255, 100, 100))
        screen.blit(ts, (WIDTH // 2 - ts.get_width() // 2, 32))

        ch_s = FM.render(f"{ch['emoji']}  {ch['label']}", True, ch["color"])
        screen.blit(ch_s, (WIDTH // 2 - ch_s.get_width() // 2, 90))

        sub = FS.render(f"Wyeliminowany w:  {lost_rd['name']}  vs  {d_lost['label']}  AI", True, (220, 150, 150))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 124))

        pygame.draw.line(screen, (120, 50, 50), (WIDTH // 2 - 265, 154), (WIDTH // 2 + 265, 154), 2)

        lbl = FM.render("TWOJE WYNIKI:", True, (200, 120, 100))
        screen.blit(lbl, (WIDTH // 2 - 250, 168))

        for i, rd in enumerate(TOURNAMENT_ROUNDS):
            d = DIFFICULTIES[rd["diff_key"]]
            if i < eliminated_round_idx:
                col  = (100, 220, 100); mark = "WYGRANA"
            elif i == eliminated_round_idx:
                col  = (255, 90, 90); mark = "PORAŻKA"
            else:
                col  = (100, 120, 100); mark = "---"
            line = FS.render(f"  {rd['name']:<20}  vs  {d['label']:<8}  -->  {mark}", True, col)
            screen.blit(line, (WIDTH // 2 - 250, 196 + i * 28))

        pygame.draw.line(screen, (120, 50, 50), (WIDTH // 2 - 265, HEIGHT - 52), (WIDTH // 2 + 265, HEIGHT - 52), 2)
        ht = FH.render("ENTER / R – Powrót do menu", True, (200, 120, 100))
        screen.blit(ht, (WIDTH // 2 - ht.get_width() // 2, HEIGHT - 34))

        pygame.display.flip()

def draw_match_end(screen, match, diff_key, char_key, tournament=False, round_label=""):
    """
    Wyświetla panel punktowy nałożony na kort (overlay) po skończonym meczu. Pokazuje sumaryczny wynik setów.
    """
    ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,215))
    screen.blit(ov,(0,0))
    pw=match.match_winner==0
    d=DIFFICULTIES[diff_key]; ch=CHARACTERS[char_key]
    FB=pygame.font.SysFont("Arial",48,bold=True)
    FM=pygame.font.SysFont("Arial",26,bold=True)
    FS=pygame.font.SysFont("Arial",20)
    FH=pygame.font.SysFont("Arial",15)
    FX=pygame.font.SysFont("Arial",16,bold=True)

    if tournament:
        tl = FX.render(f"[ WIMBLEDON  –  {round_label} ]", True, (220, 180, 60))
        screen.blit(tl, (WIDTH//2 - tl.get_width()//2, 10))

    ts=FB.render("ZWYCIĘSTWO!" if pw else "PORAŻKA!",True,(180,255,100) if pw else (255,100,100))
    screen.blit(ts,(WIDTH//2-ts.get_width()//2,64))
    inf=FS.render(f"{ch['label']}  vs  AI [{d['label']}]",True,(130,190,130))
    screen.blit(inf,(WIDTH//2-inf.get_width()//2,128))
    tx=WIDTH//2-225; ty=192; cw=130; rh=38
    for i,h in enumerate(["","SET 1","SET 2","SET 3"]):
        hs=FS.render(h,True,(110,185,110)); screen.blit(hs,(tx+i*cw+cw//2-hs.get_width()//2,ty))
    ty+=rh
    sp=match.set_history+[None]*(3-len(match.set_history))
    for idx,lbl in enumerate(["GRACZ","KOMPUTER"]):
        lb=FS.render(lbl,True,(180,255,100) if idx==0 else (255,140,140))
        screen.blit(lb,(tx+5,ty))
        for ci,p in enumerate(sp):
            if p is None: vt,col="-",(65,85,65)
            else: v=p[idx]; o=p[1-idx]; vt=str(v); col=(180,255,100) if v>o else (255,140,140)
            vs=FM.render(vt,True,col); screen.blit(vs,(tx+(ci+1)*cw+cw//2-vs.get_width()//2,ty))
        ty+=rh
    pygame.draw.line(screen,(50,90,60),(tx,ty),(tx+4*cw,ty),1); ty+=12
    ss=FM.render(f"Wynik setów:  {match.sets[0]}  –  {match.sets[1]}",True,(200,255,150))
    screen.blit(ss,(WIDTH//2-ss.get_width()//2,ty)); ty+=55

    if tournament: hint = "ENTER / R – kontynuuj turniej      ESC – opuść turniej"
    else: hint = "ENTER / R – menu główne     ESC – wyjście"
    ht=FH.render(hint,True,(100,150,100))
    screen.blit(ht,(WIDTH//2-ht.get_width()//2,ty))
