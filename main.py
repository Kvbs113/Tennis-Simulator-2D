import pygame, sys, random, math, os

os.environ['SDL_HINT_RENDER_SCALE_QUALITY'] = '0'
pygame.init()

from settings import *
from entities import Ball, Player
from match import MatchScore
from graphics import (
    draw_court, draw_service_box, draw_net, draw_serve_indicator,
    draw_menu, draw_char_select, draw_match_end,
    draw_mode_select,
    draw_tournament_bracket, draw_tournament_champion, draw_tournament_eliminated,
)


def run_game(screen, clock, diff_key, char_key, sets_to_win=None, tournament=False, round_label=""):
    """
    Główna pętla odpowiedzialna za rozgrywkę pojedynczego meczu.
    Inicjalizuje obiekty kortu, zawodników i piłki, a następnie zarządza stanem punktowym oraz wejściem użytkownika.
    
    Parametry:
        screen: Powierzchnia Pygame, na której rysowana jest gra.
        clock: Obiekt zegara kontrolujący FPS.
        diff_key: Klucz poziomu trudności dla AI.
        char_key: Klucz wybranej przez gracza postaci.
        sets_to_win: Liczba setów potrzebna do wygranej (domyślnie pobierana z settings).
        tournament: Flaga określająca, czy mecz odbywa się w trybie turniejowym.
        round_label: Etykieta obecnej rundy (używana tylko w turnieju).
        
    Zwraca:
        "WIN" lub "LOSE" w trybie turniejowym, albo "MENU" po wyjściu klawiszem ESC.
    """
    diff = DIFFICULTIES[diff_key]
    char = CHARACTERS[char_key]
    FB = pygame.font.SysFont("Arial", 30, bold=True)
    FM = pygame.font.SysFont("Arial", 20, bold=True)
    FS = pygame.font.SysFont("Arial", 15)
    FX = pygame.font.SysFont("Arial", 13)

    match = MatchScore(sets_to_win=sets_to_win)
    ball  = Ball()

    player_img       = char.get("image")
    ai_img           = diff.get("image")
    player_racket_img = char.get("racket_image")
    ai_racket_img    = diff.get("racket_image")

    player = Player(0.5, 0.88, char=char,
                    image_path=player_img, racket_image_path=player_racket_img)
    ai_pl  = Player(0.5, 0.12, is_ai=True, ai_speed=diff["ai_speed"],
                    image_path=ai_img, racket_image_path=ai_racket_img)

    bg_image = None
    if os.path.exists("court.png"):
        try:
            raw_bg   = pygame.image.load("court.png").convert()
            bg_image = pygame.transform.smoothscale(raw_bg, (WIDTH, HEIGHT))
        except Exception:
            pass

    phase        = "SERVE_WAIT"
    serve_box    = match.get_service_box()
    point_msg    = ""; point_msg_t = 0
    POINT_DUR    = 1700; GAME_DUR = 2400
    ai_serve_ms  = 0; AI_SERVE_DELAY = 1800
    hit_frame    = -100; HIT_CD = 8; frame = 0

    def reset_serve():
        """Przywraca pozycję graczy i piłki do domyślnych miejsc serwisowych."""
        nonlocal serve_box, ai_serve_ms
        ball.reset()
        serve_box   = match.get_service_box()
        ai_serve_ms = 0
        box_center_x = (serve_box[0] + serve_box[1]) / 2.0

        if match.server == 0:
            player.wx = 0.5;         player.wy = 0.97
            ai_pl.wx  = box_center_x; ai_pl.wy  = 0.03
            ball.wx = player.wx;     ball.wy = player.wy - 0.02
        else:
            ai_pl.wx  = 0.5;         ai_pl.wy  = 0.03
            player.wx = box_center_x; player.wy = 0.97
            ball.wx = ai_pl.wx;      ball.wy = ai_pl.wy + 0.02

    def show_msg(msg, dur):
        """Ustawia tekst i czas trwania powiadomienia po zdobyciu punktu."""
        nonlocal point_msg, point_msg_t
        point_msg = msg; point_msg_t = pygame.time.get_ticks(); return dur

    def award(winner, reason=""):
        """Przydziela punkt zwycięzcy i decyduje o zmianie fazy meczu."""
        nonlocal phase, point_msg, point_msg_t
        if winner == 1 and player.ult_type == "invincible" and player.ult_active:
            winner = 0
            reason = "NIETYKALNOŚĆ! (Błąd zignorowany)"
        result = match.add_point(winner)
        wl = "GRACZ" if winner == 0 else "KOMPUTER"
        pt = match.get_point_display()
        msg = f"{wl} zdobywa punkt!  [{reason}]  ({pt})"
        point_msg = msg; point_msg_t = pygame.time.get_ticks()
        if result == 'match':            phase = "MATCH_END"
        elif result in ('game', 'set'): phase = "GAME_END"
        else:                            phase = "POINT_END"

    def handle_fault():
        """Obsługuje błąd w trakcie wymiany lub serwisu."""
        nonlocal phase
        server_was      = match.server
        is_double_fault = match.fault()
        if not is_double_fault:
            phase = "SERVE_WAIT"; reset_serve()
        else:
            w = 1 if server_was == 0 else 0
            award(w, "PODWÓJNY BŁĄD SERWISU")

    def handle_ball_event(ev):
        """Zarządza logiką w oparciu o zdarzenie zwrócone przez silnik piłki."""
        nonlocal phase
        if ev is None: return
        et = ev[0]
        if phase in ("SERVE_FLIGHT", "AI_SERVE") and et != 'serve_bounce':
            handle_fault(); return
        if et == 'toss_fault':
            handle_fault()
        elif et == 'serve_bounce':
            bwx, bwy = ev[1], ev[2]
            if match.server == 1:
                ball.phase = 'rally'; ball.ai_bounces = 0; ball.player_bounces = 1
                phase = "RALLY"
            else:
                xmin, xmax, ymin, ymax = serve_box
                good = (xmin <= bwx <= xmax and ymin <= bwy <= ymax)
                if good:
                    ball.phase = 'rally'; ball.ai_bounces = 1; ball.player_bounces = 0
                    phase = "RALLY"
                else:
                    ball.active = False; handle_fault()
        elif et == 'out':
            loser = ev[1]; winner = 0 if loser == 'ai' else 1
            award(winner, "AUT BOCZNY")
        elif et == 'hit_out':
            loser = ev[1]; winner = 0 if loser == 'ai' else 1
            award(winner, "AUT (za daleko)")
        elif et == 'double_bounce':
            side = ev[1]; winner = 0 if side == 'ai' else 1
            award(winner, "PODWÓJNE ODBICIE")
        elif et == 'baseline_out':
            side = ev[1]; winner = 0 if side == 'ai' else 1
            award(winner, "NIEODEBRANE")

    reset_serve()

    while True:
        dt = clock.tick(FPS); frame += 1
        keys = pygame.key.get_pressed()
        player.update_ult(dt)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "MENU"

                if ev.key in (pygame.K_r, pygame.K_RETURN) and phase == "MATCH_END":
                    if tournament:
                        return "WIN" if match.match_winner == 0 else "LOSE"
                    return "MENU"

                if ev.key == pygame.K_q:
                    player.activate_ult()

                if ev.key == pygame.K_SPACE:
                    if phase == "SERVE_WAIT" and match.server == 0:
                        ball.start_toss(player.wx, player.wy)
                        player.racket.trigger_serve_toss()
                        phase = "SERVE_TOSS"
                    elif phase == "SERVE_TOSS" and match.server == 0:
                        if ball.height > 0.015:
                            spin = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d]
                                    else -1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
                            ball.execute_serve(True, serve_box, spin, char["hit_power"])
                            player.racket.trigger_serve_swing()
                            phase = "SERVE_FLIGHT"

        if phase in ("SERVE_FLIGHT", "AI_SERVE", "RALLY"):
            dx = dy = 0
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx =  1
            if keys[pygame.K_UP]    or keys[pygame.K_w]: dy = -1
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy =  1
            player.move(dx, dy, 1.0)

        if phase in ("RALLY", "SERVE_FLIGHT", "AI_SERVE"):
            tgt = ball.wx; dz = diff["deadzone"]; err = diff["error"]
            ddx = (1 if random.random() > err else -1) if ai_pl.wx < tgt - dz else \
                  (-1 if random.random() > err else 1) if ai_pl.wx > tgt + dz else 0
            agg = diff["aggression"]
            ddy = -1 if ball.wy < NET_WY and ai_pl.wy > agg + 0.05 else \
                   1 if ai_pl.wy < agg else 0
            ai_pl.move_ai(ddx, ddy)

        if phase == "SERVE_WAIT" and match.server == 1:
            ai_serve_ms += dt
            if ai_serve_ms >= AI_SERVE_DELAY:
                ball.start_toss(ai_pl.wx, ai_pl.wy)
                spin = random.uniform(-0.35, 0.35)
                ball.execute_serve(False, serve_box, spin, 1.0)
                ai_pl.racket.trigger_serve_swing()
                phase = "AI_SERVE"

        if phase in ("SERVE_TOSS", "SERVE_FLIGHT", "AI_SERVE", "RALLY"):
            ev = ball.update()
            if ev: handle_ball_event(ev)

        if phase == "RALLY" and frame - hit_frame > HIT_CD:
            if ball.wy < NET_WY + 0.05 and ball.height < 0.28:
                da = math.hypot(ball.wx - ai_pl.wx, ball.wy - ai_pl.wy)
                if da < 0.135:
                    if ai_pl.wx < 0.4:
                        best_spin = 1
                    elif ai_pl.wx > 0.6:
                        best_spin = -1
                    else:
                        best_spin = random.choice([-1, 1])
                    if random.random() < diff["error"]:
                        best_spin = -1 if ai_pl.wx < 0.5 else 1
                    ball.hit(ai_pl.wx, ai_pl.wy, False, best_spin, 1.0)
                    ai_pl.racket.trigger_hit()
                    hit_frame = frame

            if ball.wy > NET_WY - 0.05 and ball.height < 0.28:
                dp = math.hypot(ball.wx - player.wx, ball.wy - player.wy)
                if dp < char["hit_range"] and keys[pygame.K_SPACE]:
                    spin = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d]
                            else -1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
                    ball.hit(player.wx, player.wy, True, spin, char["hit_power"])
                    player.racket.trigger_hit()
                    hit_frame = frame

        if phase == "POINT_END":
            if pygame.time.get_ticks() - point_msg_t > POINT_DUR:
                reset_serve(); phase = "SERVE_WAIT"
        if phase == "GAME_END":
            if pygame.time.get_ticks() - point_msg_t > GAME_DUR:
                reset_serve(); phase = "SERVE_WAIT"

        draw_court(screen, bg_image)
        if phase in ("SERVE_WAIT", "SERVE_TOSS", "AI_SERVE"):
            draw_service_box(screen, serve_box)

        ball.draw_shadow(screen)
        ai_pl.draw(screen)
        if ball.wy < NET_WY: ball.draw_ball(screen)
        draw_net(screen)
        if ball.wy >= NET_WY: ball.draw_ball(screen)
        player.draw(screen)

        if phase == "SERVE_TOSS": draw_serve_indicator(screen, ball)

        pt_s = FB.render(match.get_point_display(), True, WHITE)
        screen.blit(pt_s, (WIDTH // 2 - pt_s.get_width() // 2, 8))

        gs = FS.render(match.get_score_line(), True, (160, 220, 160))
        screen.blit(gs, (WIDTH // 2 - gs.get_width() // 2, 46))

        srv_txt = ("➤ TWÓJ SERWIS" if match.server == 0 else "➤ SERWIS AI") + (
                  "  (2. serwis)" if match.serve_attempt == 2 else "")
        srv_c = (180, 255, 120) if match.server == 0 else (255, 160, 160)
        svs = FX.render(srv_txt, True, srv_c)
        screen.blit(svs, (WIDTH // 2 - svs.get_width() // 2, 68))

        d_l = FX.render(f"{diff['emoji']} {diff['label']}", True, diff["color"])
        c_l = FX.render(f"{char['emoji']} {char['label']}", True, char["color"])
        screen.blit(d_l, (5, 5)); screen.blit(c_l, (5, 20))

        if tournament:
            tl = FX.render(f"[W] {round_label}", True, (220, 180, 60))
            screen.blit(tl, (5, 38))

        if phase == "SERVE_WAIT" and match.server == 0:
            hm = FM.render("SPACJA – Rzut piłki do góry", True, (200, 255, 120))
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                screen.blit(hm, (WIDTH // 2 - hm.get_width() // 2, HEIGHT - 44))
        if phase == "SERVE_TOSS":
            hm = FM.render("SPACJA – Uderz w odpowiednim momencie!", True, (255, 230, 80))
            if (pygame.time.get_ticks() // 300) % 2 == 0:
                screen.blit(hm, (WIDTH // 2 - hm.get_width() // 2, HEIGHT - 44))
        if phase == "SERVE_WAIT" and match.server == 1:
            pct = min(100, int(ai_serve_ms / AI_SERVE_DELAY * 100))
            hm = FX.render(f"AI przygotowuje serwis... {pct}%", True, (200, 170, 170))
            screen.blit(hm, (WIDTH // 2 - hm.get_width() // 2, HEIGHT - 38))

        if point_msg and phase in ("POINT_END", "GAME_END", "MATCH_END"):
            pm = FM.render(point_msg, True, (255, 230, 70))
            bg = pygame.Surface((pm.get_width() + 24, pm.get_height() + 14), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, HEIGHT // 2 - bg.get_height() // 2))
            screen.blit(pm, (WIDTH // 2 - pm.get_width() // 2, HEIGHT // 2 - pm.get_height() // 2 + 4))

        if phase == "MATCH_END":
            draw_match_end(screen, match, diff_key, char_key, tournament, round_label)
    
        BAR_W = 300; BAR_H = 16
        BAR_X = WIDTH // 2 - BAR_W // 2
        BAR_Y = HEIGHT - 55
        pygame.draw.rect(screen, (30, 40, 30), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=8)

        if player.ult_active:
            pct    = max(0.0, player.ult_timer / player.ult_dur)
            fill_w = int(BAR_W * pct)
            color  = (255, 80, 80) if player.ult_type != "speed" else (255, 180, 50)
            txt    = f"{player.ult_name} AKTYWNY! ({player.ult_timer/1000:.1f}s)"
        elif player.ult_cooldown > 0:
            pct    = 1.0 - (player.ult_cooldown / 15000)
            fill_w = int(BAR_W * pct)
            color  = (80, 140, 220)
            txt    = f"Ładowanie... ({player.ult_cooldown/1000:.1f}s)"
        else:
            fill_w = BAR_W
            color  = (80, 230, 80)
            txt    = f"ULT GOTOWY: {player.ult_name} [Wciśnij Q]"

        if fill_w > 0:
            pygame.draw.rect(screen, color, (BAR_X, BAR_Y, fill_w, BAR_H), border_radius=8)
        pygame.draw.rect(screen, (180, 200, 180), (BAR_X, BAR_Y, BAR_W, BAR_H), 2, border_radius=8)
        ut = FX.render(txt, True, WHITE)
        screen.blit(ut, (WIDTH // 2 - ut.get_width() // 2, BAR_Y - 20))

        ct = FX.render("WASD/↑↓←→-ruch  SPACJA-serwis  ←→-spin  ESC-menu", True, (42, 80, 42))
        screen.blit(ct, (WIDTH // 2 - ct.get_width() // 2, HEIGHT - 18))

        pygame.display.flip()


def run_tournament(screen, clock, char_key):
    """
    Prowadzi gracza przez drabinkę turniejową. Przegrana skutkuje natychmiastową eliminacją.
    
    Parametry:
        screen: Powierzchnia Pygame.
        clock: Obiekt zegara.
        char_key: Wybrana postać gracza.
    """
    results = []

    for i, rd in enumerate(TOURNAMENT_ROUNDS):
        action = draw_tournament_bracket(screen, clock, char_key, results, i)
        if action != "PLAY":
            return

        game_result = run_game(
            screen, clock,
            diff_key    = rd["diff_key"],
            char_key    = char_key,
            sets_to_win = 2,
            tournament  = True,
            round_label = rd["name"],
        )

        if game_result == "WIN":
            results.append(("W", rd["name"], rd["diff_key"]))
        elif game_result == "LOSE":
            results.append(("L", rd["name"], rd["diff_key"]))
            draw_tournament_eliminated(screen, clock, char_key, results, i)
            return
        else:
            return

    draw_tournament_champion(screen, clock, char_key, results)


def main():
    """
    Punkt wejścia aplikacji. Inicjalizuje okno i zarządza nawigacją pomiędzy trybami gry.
    """
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("Tennis Simulator")
    clock    = pygame.time.Clock()
    sel_diff = "SREDNI"
    sel_char = "AMATOR"

    while True:
        mode = draw_mode_select(screen, clock)

        if mode == "TOURNAMENT":
            res = draw_char_select(screen, clock, sel_char)
            if res == "BACK":
                continue
            sel_char = res
            run_tournament(screen, clock, sel_char)
        else:
            sel_diff = draw_menu(screen, clock, sel_diff)
            res = draw_char_select(screen, clock, sel_char)
            if res == "BACK":
                continue
            sel_char = res
            run_game(screen, clock, sel_diff, sel_char)


if __name__ == "__main__":
    main()
