import pygame
import sys
import random
import cv2
import numpy as np
from PoseDetector import PoseDetector


wCam, hCam = 1200, 720

def play_flappy_bird():
    # --- CAMERA & POSE ---
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = PoseDetector()

    dir = 0
    trigger_fly = False
    flap_count = 0

    # ------------ FLAPPY BIRD CORE ------------
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    screen = pygame.display.set_mode((432, 768)) #screen game
    clock = pygame.time.Clock()
    game_font = pygame.font.Font('assets/font/04B_19.TTF', 35)


    gravity = 0.45
    bird_movement = 0
    game_active = True
    score = 0
    high_score = 0

    bg = pygame.image.load('assets/background-night.png').convert()
    bg = pygame.transform.scale2x(bg)

    floor = pygame.image.load('assets/floor.png').convert()
    floor = pygame.transform.scale2x(floor)
    floor_x_pos = 0

    bird_down = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-downflap.png').convert_alpha())
    bird_mid = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-midflap.png').convert_alpha())
    bird_up = pygame.transform.scale2x(pygame.image.load(
        'assets/yellowbird-upflap.png').convert_alpha())

    bird_list = [bird_down, bird_mid, bird_up]
    bird_index = 0
    bird = bird_list[bird_index]
    bird_rect = bird.get_rect(center=(100, 384))

    birdflap = pygame.USEREVENT + 1
    pygame.time.set_timer(birdflap, 200)

    pipe_surface = pygame.image.load('assets/pipe-green.png').convert()
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    pipe_list = []

    spawnpipe = pygame.USEREVENT
    pygame.time.set_timer(spawnpipe, 2500)
    pipe_height = range(250, 500)

    game_over_surface = pygame.transform.scale2x(
        pygame.image.load('assets/messagetemp.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(216, 384))

    flap_sound = pygame.mixer.Sound('assets/sound/sfx_wing.wav')
    hit_sound = pygame.mixer.Sound('assets/sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('assets/sound/sfx_point.wav')
    score_sound_countdown = 100

    # ------------ GAME FUNCTIONS ------------
    def draw_floor():
        screen.blit(floor, (floor_x_pos, 650))
        screen.blit(floor, (floor_x_pos + 432, 650))

    def create_pipe():
        random_pipe_pos = random.choice(pipe_height)
        bottom_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos))
        top_pipe = pipe_surface.get_rect(midtop=(500, random_pipe_pos - 750))
        return bottom_pipe, top_pipe

    def move_pipe(pipes):
        for pipe in pipes:
            pipe.centerx -= 5 
        return pipes

    def draw_pipe(pipes):
        for pipe in pipes:
            if pipe.bottom >= 600:
                screen.blit(pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(pipe_surface, False, True)
                screen.blit(flip_pipe, pipe)

    def check_collision(pipes):
        for pipe in pipes:
            if bird_rect.colliderect(pipe):
                hit_sound.play()
                return False
        if bird_rect.top <= -75 or bird_rect.bottom >= 650:
            return False
        return True

    def rotate_bird(bird1):
        return pygame.transform.rotozoom(bird1, -bird_movement * 3, 1)

    def bird_animation():
        new_bird = bird_list[bird_index]
        new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
        return new_bird, new_bird_rect

    def score_display(game_state):
        if game_state == 'main game':
            score_surface = game_font.render(str(int(score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(216, 100))
            screen.blit(score_surface, score_rect)
        if game_state == 'game_over':
            score_surface = game_font.render(f'Score: {int(score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(216, 100))
            screen.blit(score_surface, score_rect)
            high_score_surface = game_font.render(
                f'High Score: {int(high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(216, 630))
            screen.blit(high_score_surface, high_score_rect)

    def update_score(score, high_score):
        return score if score > high_score else high_score

    # ------------ MAIN LOOP ------------
    try:
        while True:
            success, img = cap.read()
            img = cv2.flip(img, 1)
            if not success:
                break
            img = detector.findPose(img, draw=True)
            lmList = detector.findPosition(img, draw=False)


            if len(lmList) != 0:
                hand_ids = [11, 12, 13, 14] # shoulder, elbow, wrist
                for fid in hand_ids:
                    _, x, y = lmList[fid]
                    cv2.circle(img, (x, y), 8, (0, 128, 255), cv2.FILLED)  # màu cam
                    cv2.putText(img, str(fid), (x - 10, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                # Nối xương tay trái & phải
                cv2.line(img, lmList[11][1:], lmList[13][1:], (0, 128, 255), 2)
                cv2.line(img, lmList[12][1:], lmList[14][1:], (0, 128, 255), 2)

                # --- HAND CONTROL ---
                angleRight = detector.findAngle(img, 14, 12, 24)
                angleLeft = detector.findAngle(img, 13, 11, 23)
                perRight = np.interp(angleRight, (30, 80), (0, 100))
                perLeft = np.interp(angleLeft, (30, 80), (0, 100))

                if perRight > 20 and perLeft > 20:
                    if dir == 0:
                        dir = 1
                elif perRight < 5 and perLeft < 5:
                    if dir == 1:
                        trigger_fly = True
                        dir = 0
                
                cv2.putText(img, f"L:{int(perLeft)} R:{int(perRight)}", 
                (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

                status = "FLAP!" if trigger_fly else "UP" if dir == 1 else "READY"
                cv2.rectangle(img, (30, 150), (260, 25), (255, 255, 255), cv2.FILLED)
                cv2.putText(img, status, (40, 100),
                            cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 0, 0), 2)

            cv2.imshow("hehe", img)
            if cv2.waitKey(1) == ord("q"):
                break

            # --- PYGAME EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if trigger_fly:
                    flap_count += 1
                    if game_active:
                        bird_movement = 0
                        bird_movement = -10
                        flap_sound.play()
                    else:
                        game_active = True
                        pipe_list.clear()
                        bird_rect.center = (100, 384)
                        bird_movement = 0
                        score = 0
                    trigger_fly = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and game_active:
                        bird_movement = 0
                        bird_movement = -10 
                        flap_sound.play()
                    if event.key == pygame.K_SPACE and not game_active:
                        game_active = True
                        pipe_list.clear()
                        bird_rect.center = (100, 384)
                        bird_movement = 0
                        score = 0

                if event.type == spawnpipe:
                    pipe_list.extend(create_pipe())

                if event.type == birdflap:
                    bird_index = (bird_index + 1) % 3
                    bird, bird_rect = bird_animation()

            # --- GAME LOGIC ---
            screen.blit(bg, (0, 0))

            if game_active:
                bird_movement += gravity  
                rotated_bird = rotate_bird(bird)
                bird_rect.centery += bird_movement
                screen.blit(rotated_bird, bird_rect)

                game_active = check_collision(pipe_list)
                pipe_list = move_pipe(pipe_list)
                draw_pipe(pipe_list)

                score += 0.01
                score_display('main game')

                score_sound_countdown -= 1
                if score_sound_countdown <= 0:
                    score_sound.play()
                    score_sound_countdown = 100
            else:
                screen.blit(game_over_surface, game_over_rect)
                high_score = update_score(score, high_score)
                score_display('game_over')

            floor_x_pos -= 1
            draw_floor()
            if floor_x_pos <= -432:
                floor_x_pos = 0

            pygame.display.update()
            clock.tick(120)  

    finally:
        cap.release()
        cv2.destroyAllWindows()
        pygame.quit()


# if __name__ == "__main__":
#     play_flappy_bird()
