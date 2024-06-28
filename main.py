#IMPORTAMOS LAS LIBRERIAS A UTILIZAR
import pygame
import random
from settings import *

#DEFINE ATRIBUTOS DEL JUGADOR
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("player.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH // 2 #POSICIÓN HORIZONTAL INICIAL DEL JUGADOR (CENTRO)
        self.rect.y = 510  #POSICIÓN VERTICAL INICIAL DEL JUGADOR
        self.speed_x = 0

    def changespeed(self, x):
        self.speed_x += x

    def update(self):
        self.rect.x += self.speed_x

        #LIMITACIÓN DEL MOVIMIENTO DE JUGADOR
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("meteor.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(2, 5)

    #ACTUALIZA LA POSICIÓN DEL METEORITO
    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10:
            #REINICIAR LA POSICIÓN DEL METEORITO
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(2, 5)

class Laser(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("laser.png").convert()
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y -= 8  #VELOCIDAD CON LA QUE SE DISPARA EL LASER

#REINICIAR EL JUEGO
def reset_game():
    global all_sprites_list, meteor_list, player, score, laser_list
    all_sprites_list = pygame.sprite.Group()
    meteor_list = pygame.sprite.Group()
    laser_list = pygame.sprite.Group()

    player = Player()
    all_sprites_list.add(player)
    score = 0

    #METEORITOS
    for _ in range(10):
        meteor = Meteor()
        meteor_list.add(meteor)
        all_sprites_list.add(meteor)

def play_laser_sound():
    #REPRODUCE EL SONIDO DEL LASER
    pygame.mixer.Sound("laser5.ogg").play()

#INICIA PYGAME
pygame.init()
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT]) #CREACION DE LA VENTANA
pygame.display.set_caption("Meteor Shooter") # TITULO DE LA VENTANA
clock = pygame.time.Clock() # FPS
done = False
game_over = False
score = 0 #PUNTUACIÓN
#CREA METEOROS CADA CIERTO TIEMPO
spawn_event = pygame.USEREVENT + 1 
pygame.time.set_timer(spawn_event, 1000)

#INICIA EL JUEGO UNA VEZ HECHO CLICK
reset_game()

#LOGICA PRINCIPAL DEL JUEGO
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        #EVENTOS CON EL MOVIMIENTO, AL PRESIONAR EL TECLADO
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.changespeed(-3)
            elif event.key == pygame.K_RIGHT:
                player.changespeed(3)
            elif event.key == pygame.K_SPACE:
                #DISPARO DEL LASER AL PRESIONAR ESPACIO
                laser = Laser()
                laser.rect.centerx = player.rect.centerx
                laser.rect.bottom = player.rect.top  #LASER ENCIMA DE LA NAVE
                all_sprites_list.add(laser)
                laser_list.add(laser)
                play_laser_sound() #REPRODUCE EL SONIDO DEL LASER

        #EVENTOS CON EL MOVIMIENTO, AL PRESIONAR EL TECLADO
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and player.speed_x < 0:
                player.changespeed(3)
            elif event.key == pygame.K_RIGHT and player.speed_x > 0:
                player.changespeed(-3)

        #APARICIÓN DE METEORITOS
        if event.type == spawn_event and not game_over:
            meteor = Meteor()
            meteor_list.add(meteor)
            all_sprites_list.add(meteor)

        #REINICIAR JUEGO
        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            reset_game()
            game_over = False

    if not game_over:
        all_sprites_list.update()

        for meteor in meteor_list:
            if meteor.rect.colliderect(player.rect):
                game_over = True

            if meteor.rect.top > SCREEN_HEIGHT:
                #POSICION ALEATORIZADA DE METEORITO AL SALIR DE LA PANTALLA
                meteor.rect.x = random.randrange(SCREEN_WIDTH - meteor.rect.width)
                meteor.rect.y = random.randrange(-100, -40)
                meteor.speed_y = random.randrange(1, 8)

        #LÓGICA DE LASERES Y COLISIONES CON METEORITOS
        for laser in laser_list:
            meteor_hit_list = pygame.sprite.spritecollide(laser, meteor_list, True)
            for meteor in meteor_hit_list:
                score += 1  #SUMA UN PUNTO AL DESTRUIR UN METEORITO
                all_sprites_list.remove(laser)
                laser_list.remove(laser)
                all_sprites_list.remove(meteor)
                meteor_list.remove(meteor)

            if laser.rect.bottom < 0:
                #ELIMINAR LASER AL SALIR DEL MARGEN
                all_sprites_list.remove(laser)
                laser_list.remove(laser)

    #RENDERIZA LA PANTALLA
    screen.fill(BG_COLOR)
    all_sprites_list.draw(screen)

    if game_over:
        #PANTALLA DE JUEGO TERMINADO
        font = pygame.font.SysFont("Impact", 72)
        text = font.render("Juego Terminado", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 72))
        screen.blit(text, text_rect)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Click para reiniciar", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
        screen.blit(text, text_rect)
    else:
        #MUESTRA LA PUNTUACIÓN EN PANTALLA
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"PUNTOS: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
