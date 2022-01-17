"""
Очень простенькая и незамысловатая игра - Coblin Slayer
Мочи гоблинов и наслаждайся жизнью!

Что пытался реализовать в этой игре:
* Возростание уровня персонажа, а всместе с ним и увеличение как его характеристик, так и кол-ва
противников
* Отображение информации о уровне, скорости, кол-ве жизней, счёте
* Стрельба пулями
* Рандомный респавн противников и поинтов жизни
* Коллизия и hit-box
* Анимация моделек и звуки
"""
#Импорт модулей
import pygame as py
import sys
import random

#Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_FRAME_LIMIT = 27
ENEMY_FRAME_LIMIT = 33
BULLETS_LIMIT = 5
BULLETS_COLOR = BLACK
JUMP_LIMIT = 8
ENEMY_HEALTH = 10
PLAYER_SPEED = 5
ENEMY_SPEED = 3
SPRITE_SIZE = 64
LIFE_TIMER = 600
GAME_FONT = 'optimatic'

#Переменные значения
score = 0
hiscore = 0
lives = 5
level = 1
speed = 3
player_dead = False
life_visible = True
life_x = 150
life_y = 280
life_wait_timer = 1
life_hitbox = (life_x + 2, life_y + 2, 24, 24)
life_taken = False
pause = False

#Инициализация игры
py.init()
game_screen = py.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
py.display.set_caption("Goblin Slayer")
clock = py.time.Clock()


def terminate():
    py.quit()
    sys.exit()

#Начальный экран
def start_screen():
    intro_text = ["wasd или стрелки, чтобы двигаться.",
                  "",
                  "space, чтобы стрелять",
                  "",
                  "P чтобы остановить игру",
                  "",
                  "нажмите любую кнопку, чтобы начать"]

    game_screen.blit(py.image.load('resources/goblin_slayer.jpg'), (-1050, -100))
    font = py.font.Font(None, 30)
    text_coord = 200
    for line in intro_text:
        string_rendered = font.render(line, True, py.Color('green'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 60
        text_coord += intro_rect.height
        game_screen.blit(string_rendered, intro_rect)

    # собственный цикл для показа заставки
    while True:
        for event in py.event.get():
            if event.type == py.QUIT:
                terminate()
            # при нажатии любой кнопки выходим из функции, попадая затем в основной игровой цикл
            elif event.type in (py.KEYDOWN, py.MOUSEBUTTONDOWN):
                return
        py.display.flip()

#Картинки (да, можно было загружать проще)
player_walk_right = [py.image.load('resources/R1.png'), py.image.load('resources/R2.png'),
                     py.image.load('resources/R3.png'), py.image.load('resources/R4.png'),
                     py.image.load('resources/R5.png'), py.image.load('resources/R6.png'),
                     py.image.load('resources/R7.png'), py.image.load('resources/R8.png'),
                     py.image.load('resources/R9.png')]
player_walk_left = [py.image.load('resources/L1.png'), py.image.load('resources/L2.png'),
                    py.image.load('resources/L3.png'), py.image.load('resources/L4.png'),
                    py.image.load('resources/L5.png'), py.image.load('resources/L6.png'),
                    py.image.load('resources/L7.png'), py.image.load('resources/L8.png'),
                    py.image.load('resources/L9.png')]
enemy_walk_right = [py.image.load('resources/R1E.png'), py.image.load('resources/R2E.png'),
                    py.image.load('resources/R3E.png'), py.image.load('resources/R4E.png'),
                    py.image.load('resources/R5E.png'), py.image.load('resources/R6E.png'),
                    py.image.load('resources/R7E.png'), py.image.load('resources/R8E.png'),
                    py.image.load('resources/R9E.png'), py.image.load('resources/R10E.png'),
                    py.image.load('resources/R11E.png')]
enemy_walk_left = [py.image.load('resources/L1E.png'), py.image.load('resources/L2E.png'),
                   py.image.load('resources/L3E.png'), py.image.load('resources/L4E.png'),
                   py.image.load('resources/L5E.png'), py.image.load('resources/L6E.png'),
                   py.image.load('resources/L7E.png'), py.image.load('resources/L8E.png'),
                   py.image.load('resources/L9E.png'), py.image.load('resources/L10E.png'),
                   py.image.load('resources/L11E.png')]
background_platform = py.image.load('resources/background.png')
player_life = py.image.load('resources/life.png')

#Класс игра с присущими ему характеристиками(атрибутами)
class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = PLAYER_SPEED
        self.is_jump = False
        self.left = False
        self.right = False
        self.walk_count = 0
        self.jump_limit = JUMP_LIMIT
        self.standing = True
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)

    def draw(self, game_screen):
        if self.walk_count + 1 >= PLAYER_FRAME_LIMIT:
            self.walk_count = 0
        if not self.standing:
            if self.left:
                game_screen.blit(player_walk_left[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1
            elif self.right:
                game_screen.blit(player_walk_right[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1        
        else:
            if self.right:
                game_screen.blit(player_walk_right[0], (self.x, self.y))
            else:
                game_screen.blit(player_walk_left[0], (self.x, self.y))
        self.hitbox = (self.x + 17, self.y + 11, 29, 52)

    def hit(self):
        self.is_jump = False
        self.jump_limit = JUMP_LIMIT
        self.x = random.randint(0, SCREEN_WIDTH-50)
        self.y = 370
        self.walk_count = 0


#Класс врага с присущими ему характеристиками(атрибутами)
class Enemy:
    def __init__(self, x, y, width, height, end):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.end = end
        self.walk_count = 0
        self.path = [self.x, self.end]
        self.speed = ENEMY_SPEED
        self.hitbox = (self.x + 17, self.y + 2, 31, 57)
        self.health = ENEMY_HEALTH
        self.visible = True
    
    def draw(self, game_screen):
        if self.visible:
            self.move()
            if self.walk_count + 1 >= ENEMY_FRAME_LIMIT:
                self.walk_count = 0
            
            if self.speed > 0:
                game_screen.blit(enemy_walk_right[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1
            else:
                game_screen.blit(enemy_walk_left[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1
            
            py.draw.rect(game_screen, RED, (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
            py.draw.rect(game_screen, GREEN, (self.hitbox[0], self.hitbox[1] - 20,
                                              50 - ((50 / ENEMY_HEALTH) *
                                              (ENEMY_HEALTH - self.health)), 10))
            self.hitbox = (self.x + 17, self.y + 2, 31, 57)

    def move(self):
        if self.speed > 0:
            if self.x + self.speed < self.path[1]:
                self.x += self.speed
            else:
                self.speed = self.speed * -1
                self.walk_count = 0
        else:
            if self.x - self.speed > self.path[0]:
                self.x += self.speed
            else:
                self.speed = self.speed * -1
                self.walk_count = 0

    def hit(self, level):
        if self.health > 0:
            self.health -= 1 if level < 5 else 2
        else:
            self.visible = False                                     

#Класс для пуль(снарядов)
class Projectile:
    def __init__(self, x, y, radius, color, facing):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.facing = facing
        self.speed = 8 * facing

    def draw(self, game_screen):
        py.draw.circle(game_screen, self.color, (self.x, self.y), self.radius)
                                
#Отрисовка справйтов (можно было собрать в группы)
def renderSprites():
    global life_wait_timer, life_taken, life_x, life_y, life_hitbox, life_visible

    game_screen.blit(background_platform, (0, 0))

    logo_font = py.font.SysFont(GAME_FONT, 30, True, True)

    logo_text = logo_font.render('Goblin Slayer V.01', 0, (0, 0, 0))
    game_screen.blit(logo_text, (300, 100))

    font = py.font.SysFont(GAME_FONT, 20, True, True)

    lives_text = font.render('Lives ' + str(lives), 1, RED)
    game_screen.blit(lives_text, (80, 0))

    level_text = font.render('level ' + str(level), 1, BLACK)
    game_screen.blit(level_text, (210, 0))

    hiscore_text = font.render('Speed ' + str(speed), 1, BLACK)
    game_screen.blit(hiscore_text, (330, 0))

    score_text = font.render('Score ' + str(score), 1, BLUE)
    game_screen.blit(score_text, (460, 0))

    hiscore_text = font.render('Hiscore ' + str(hiscore), 1, BLUE)
    game_screen.blit(hiscore_text, (590, 0))

    #Отрисовка игрока, врагов и пуль покадрово
    player.draw(game_screen)

    if level < 5:
        enemy_1.draw(game_screen)
    elif level >= 5 and level < 10:
        enemies = [enemy_1, enemy_2]
        for enemy in enemies:
            enemy.draw(game_screen)
    elif level >= 10:
        enemies = [enemy_1, enemy_2, enemy_3]
        for enemy in enemies:
            enemy.draw(game_screen)

    for bullet in bullets:
        bullet.draw(game_screen)

    #Новая позиция для "поинта жизни" если уже было взято
    if life_taken:
        life_x = random.randint(0, SCREEN_WIDTH-50)
        life_y = random.randint(280, SCREEN_HEIGHT-70)
        life_taken = False
        life_visible = False
    else:
        life_wait_timer += 1

    #Ожидание появления пового "поинта жизни" (сердечка)
    if not life_taken and life_wait_timer % LIFE_TIMER == 0:
        life_visible = True

    if life_visible:
        game_screen.blit(player_life, (life_x, life_y))

    life_hitbox = (life_x + 2, life_y + 2, 24, 24)
    py.display.update()

#Столкновения между игром, врагами, пулями
def  spriteCollisionDetection(enemy, bullets):
    global score, lives, level, life_taken

    #Игрок и враги столкнулись
    if player.hitbox[1] < enemy.hitbox[1] + enemy.hitbox[3] and player.hitbox[1] +\
            player.hitbox[3] > enemy.hitbox[1]:
        if player.hitbox[0] + player.hitbox[2] > enemy.hitbox[0] and player.hitbox[0] <\
                enemy.hitbox[0] + enemy.hitbox[2]:
            if enemy.visible:
                player.hit()
                score -= 5
                score = 0 if score < 0 else score
                lives -= 1
                py.mixer.music.load('resources/player_dead.mp3')
                py.mixer.music.play(1)
                py.time.delay(1000)

    #Игрок и "поинт жизни" столкнулись
    if player.hitbox[1] < life_hitbox[1] + life_hitbox[3] and player.hitbox[1] +\
            player.hitbox[3] > life_hitbox[1]:
        if player.hitbox[0] + player.hitbox[2] > life_hitbox[0] and player.hitbox[0] <\
                life_hitbox[0] + life_hitbox[2]:
            if life_visible:
                lives += 1
                life_taken = True
                py.mixer.music.load('resources/life_up.wav')
                py.mixer.music.play(1)

    #Враг попал под пулю...
    for bullet in bullets:
        if bullet.y - bullet.radius < enemy.hitbox[1] + enemy.hitbox[3] and bullet.y +\
                bullet.radius > enemy.hitbox[1]:
            if bullet.x + bullet.radius > enemy.hitbox[0] and bullet.x - bullet.radius <\
                    enemy.hitbox[0] + enemy.hitbox[2]:
                if enemy.visible:
                    py.mixer.music.load('resources/enemy_bullet_hit.mp3')
                    py.mixer.music.play(1)
                    enemy.hit(level)
                    score += 1
                    bullets.remove(bullet)

        if bullet.x < SCREEN_WIDTH and bullet.x > 0:
            bullet.x += bullet.speed
        
        else:
            bullets.remove(bullet)

#Респавн врагов
def respawnEnemy(enemy):
    py.mixer.music.load('resources/enemy_dead.wav')
    py.mixer.music.play(1)
    py.time.delay(1000)
    enemy.health = ENEMY_HEALTH
    enemy.visible = True
    enemy.x = random.randint(0, SCREEN_WIDTH-50)


if __name__ == '__main__':

    #Cоздание игрока и врага в начале
    player = Player(300, 370, SPRITE_SIZE, SPRITE_SIZE)
    enemy_1 = Enemy(0, 380, SPRITE_SIZE, SPRITE_SIZE, SCREEN_WIDTH-50)
    enemy_2 = Enemy(100, 380, SPRITE_SIZE, SPRITE_SIZE, SCREEN_WIDTH-50)
    enemy_3 = Enemy(200, 380, SPRITE_SIZE, SPRITE_SIZE, SCREEN_WIDTH-50)
    bullets = []
    shoot_loop = 0
    reset_speed = True
    run = True
    pause_freq = 0

    start_screen()

    #Главнй цикл игры
    while run:
        clock.tick(PLAYER_FRAME_LIMIT)

        #Game Over и сброс всех параметров
        if lives <= 0:
            #Сброс переменных
            hiscore = (score + 5) if score > hiscore else hiscore
            lives = 5
            score = 0
            level = 1
            speed = 3
            BULLETS_LIMIT = 5
            LIFE_TIMER = 600
            enemy_1.health = ENEMY_HEALTH
            enemy_1.speed = ENEMY_SPEED
            player.speed = PLAYER_SPEED
            enemy_1.visible = True

            #Отрисовка Game Over и музыка
            game_over_font = py.font.SysFont('arial', 20, True, True)
            game_over_text = game_over_font.render('Game Over (Press ENTER Key)', 1, RED)
            game_screen.blit(game_over_text, (150, 150))
            py.mixer.music.load('resources/game_over.mp3')
            py.mixer.music.play(1)

            for bullet in bullets:           
                bullets.remove(bullet)

            #Отображение и задержка обновления
            py.display.update()
            pause = True   

        #Завершение работы приложения
        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                    
        #Предельная дальность стрельбы
        if shoot_loop > 0:
            shoot_loop += 1
        if shoot_loop > 3:
            shoot_loop = 0        

        #Возрождайте нового врага и проверка столкновения
        if level < 5:
            if not enemy_1.visible and enemy_1.health == 0:
                respawnEnemy(enemy_1)
                enemy_1.speed = abs(enemy_1.speed) + 1
                level += 1
                speed = abs(enemy_1.speed)
            spriteCollisionDetection(enemy_1, bullets)
        elif level >= 5 and level < 10:
            enemies = [enemy_1, enemy_2]
            if level == 5 and reset_speed:
                enemy_1.speed = enemy_2.speed = speed = ENEMY_SPEED
                BULLETS_LIMIT = 7
                LIFE_TIMER = 400
                player.speed += 2
                reset_speed = False
            if level == 9: 
                reset_speed = True

            if not enemy_1.visible and not enemy_2.visible and \
                    enemy_1.health == 0 and enemy_2.health == 0:
                for enemy in enemies:
                    respawnEnemy(enemy)
                    enemy.speed = abs(enemy.speed) + 1
                    speed = abs(enemy.speed)
                level += 1

            for enemy in enemies:    
                spriteCollisionDetection(enemy, bullets)

            if life_taken:
                lives -= 1

        elif level >= 10:
            enemies = [enemy_1, enemy_2, enemy_3]
            if level == 10 and reset_speed:
                enemy_1.speed = enemy_2.speed = enemy_3.speed = speed = ENEMY_SPEED
                player.speed += 3
                BULLETS_LIMIT = 10
                LIFE_TIMER = 200
                reset_speed = False
            if not enemy_1.visible and not enemy_2.visible and not enemy_3.visible and\
                    enemy_1.health == 0 and enemy_2.health == 0 and enemy_3.health == 0:
                
                for enemy in enemies:    
                    respawnEnemy(enemy)
                    enemy.speed = abs(enemy.speed) + 1
                    speed = abs(enemy.speed)
                level += 1

            for enemy in enemies:    
                spriteCollisionDetection(enemy, bullets)

            if life_taken:    
                lives -= 2     

        #Нажатие на клавиши
        keys = py.key.get_pressed()

        #Стрельба
        if keys[py.K_SPACE] and shoot_loop == 0:
            py.mixer.music.load('resources/bullet.mp3')
            py.mixer.music.play(1)
            facing = -1 if player.left else 1    
            projectile = Projectile((player.x + player.width // 2),
                                    round(player.y + player.height // 2), 6, BULLETS_COLOR, facing)
            
            if len(bullets) < BULLETS_LIMIT:
                bullets.append(projectile)
            shoot_loop = 1

        if keys[py.K_p]:
            pause = not pause
            pause_freq += 1

        if pause_freq % 2 == 0 and pause_freq > 0:
            pause_freq = 1
                       

        #Джижения игрока
        if keys[py.K_LEFT] or keys[py.K_a] and player.x > player.speed:
            player.x -= player.speed
            player.left = True
            player.right = False
            player.standing = False
        elif keys[py.K_RIGHT] or keys[py.K_d] and \
                player.x < SCREEN_WIDTH - player.width - player.speed:
            player.x += player.speed
            player.right = True
            player.left = False
            player.standing = False
        else:
            player.standing = True
            player.walk_count = 0
        
        #Прыжки игрока
        if not player.is_jump:
            if keys[py.K_UP] or keys[py.K_w]:
                py.mixer.music.load('resources/player_jump.wav')
                py.mixer.music.play(1)
                player.is_jump = True
                player.right = False
                player.left = False
                player.walk_count = 0
        else:
            if player.jump_limit >= -JUMP_LIMIT:
                player.y -= (player.jump_limit * abs(player.jump_limit)) / 2
                player.jump_limit -= 1
            else:
                player.is_jump = False
                player.jump_limit = JUMP_LIMIT

        if not pause:        
            #Отрисовка спрайтов
            renderSprites()

    py.quit()
