import os
import pygame
import random
import settings as s

vec = pygame.math.Vector2


class SpriteSheet:
    """Utility class for loading and parsing spritesheets.
    """

    def __init__(self, filename):
        """Loads the spritesheet.

        Args:
            filename (str): Filename of the spritesheet to be loaded.
        """

        self.spritesheet = pygame.image.load(filename).convert()

    def get_image(self, x, y, width, height, scale=0.5):
        """Grabs a smaller image from the larger spritesheet.

        Args:
            x (int): x coordinate of the image.
            y (int): y coordinate of the image.
            width (int): width of the image.
            height (int): height of the image.
            scale (float, optional): scale factor between 0 and 1.
                Defaults to 0.5

        Returns:
            image (pygame.Surface): a scaled image.
        """

        image = pygame.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pygame.transform.scale(image, (int(width * scale),
                                               int(height * scale)))

        return image


class Cloud(pygame.sprite.Sprite):

    def __init__(self, game):
        """Initializing a Cloud sprite.

        Args:
            game (game_instance): Game instance.
        """

        self._layer = s.CLOUD_LAYER
        groups = game.all_sprites, game.clouds
        super(Cloud, self).__init__(groups)

        self.game = game
        self.image = random.choice(self.game.cloud_images)
        self.image.set_colorkey(s.BLACK)
        self.rect = self.image.get_rect()
        scale = random.randrange(50, 101) / 100
        self.image = pygame.transform.scale(self.image, (int(self.rect.width * scale),
                                                         int(self.rect.height * scale)))
        self.rect.x = random.randrange(s.WIDTH, s.WIDTH + self.rect.width)
        self.rect.y = random.randrange(0, s.HEIGHT - 350)

    def update(self):
        """Updates sprite.

        Kills the sprite if out of screen.
        """
        if self.rect.right < 0:
            self.kill()


class Platform(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        """Initializing a platform sprite.

        Args:
            game (game_instance): Game instance.
            x (int): x coordinate of the center of the platform.
            y (int): y coordinate of the center of the platform.
        """

        self._layer = s.PLATFORM_LAYER
        groups = game.all_sprites, game.platforms
        super(Platform, self).__init__(groups)

        self.game = game

        # load a random image
        images = [
            self.game.plat_spritesheet.get_image(0, 96, 380, 94),  # stone
            self.game.plat_spritesheet.get_image(0, 192, 380, 94),  # stone broken
            self.game.plat_spritesheet.get_image(382, 408, 200, 100),  # stone small
            self.game.plat_spritesheet.get_image(232, 1288, 200, 100),  # stone small broken
        ]

        self.image = random.choice(images)

        self.image.set_colorkey(s.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Base(pygame.sprite.Sprite):

    def __init__(self, game, x):
        """Initializing a Base sprite.

        Args:
            game (game_instance): Game instance.
            x (int): x coordinate of the Base sprite.
        """

        self._layer = s.PLATFORM_LAYER
        groups = game.all_sprites
        super(Base, self).__init__(groups)

        self.game = game
        self.image = self.game.base_img
        self.image.set_colorkey(s.BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = s.HEIGHT - s.BASE_HEIGHT


class Player(pygame.sprite.Sprite):

    def __init__(self, game):
        """Initializing player.

        Args:
            game (game_instance): Game instance.
        """

        self._layer = s.PLAYER_LAYER
        groups = game.all_sprites
        super(Player, self).__init__(groups)

        self.game = game
        # self.idle = True
        self.running = False
        self.jumping = False
        self.isRight = True
        # self.shooting = False
        # self.hurt = False

        # tracking for animation
        self.current_frame = 0
        self.last_update = 0

        # load image data
        self.load_images()

        self.image = self.standing_frames_r[0]
        self.rect = self.image.get_rect()
        self.rect.center = (20, s.HEIGHT - 50)  # initial pos of player

        self.pos = vec(40, s.HEIGHT - 50)  # position vector
        self.vel = vec(0, 0)  # velocity vector
        self.acc = vec(0, 0)  # acceleration vector

    def load_images(self):
        """Loads all necessary images for animation.
        """

        # standing / idle frames
        self.standing_frames_r = []
        stand_dir = os.path.join(self.game.img_dir, s.PLAYER_IDLE)
        for image in os.listdir(stand_dir):
            frame = pygame.image.load(os.path.join(stand_dir, image)).convert()
            rect = frame.get_rect()
            frame = pygame.transform.scale(frame, (int(rect.width * 0.2),
                                                   int(rect.height * 0.2)))
            frame.set_colorkey(s.BLACK)
            self.standing_frames_r.append(frame)

        self.standing_frames_l = []
        for frame in self.standing_frames_r:  # flip x, and not y
            self.standing_frames_l.append(pygame.transform.flip(frame, True, False))

        # hurt frames
        self.hurt_frames_r = []
        hurt_dir = os.path.join(self.game.img_dir, s.PLAYER_HURT)
        for image in os.listdir(hurt_dir):
            frame = pygame.image.load(os.path.join(hurt_dir, image)).convert()
            rect = frame.get_rect()
            frame = pygame.transform.scale(frame, (int(rect.width * 0.2),
                                                   int(rect.height * 0.2)))
            frame.set_colorkey(s.BLACK)
            self.hurt_frames_r.append(frame)

        self.hurt_frames_l = []
        for frame in self.hurt_frames_r:  # flip x, and not y
            self.hurt_frames_l.append(pygame.transform.flip(frame, True, False))

        # jumping frames
        self.jumping_frames_r = []
        jump_dir = os.path.join(self.game.img_dir, s.PLAYER_JUMP)
        for image in os.listdir(jump_dir):
            frame = pygame.image.load(os.path.join(jump_dir, image)).convert()
            rect = frame.get_rect()
            frame = pygame.transform.scale(frame, (int(rect.width * 0.2),
                                                   int(rect.height * 0.2)))
            frame.set_colorkey(s.BLACK)
            self.jumping_frames_r.append(frame)

        self.jumping_frames_l = []
        for frame in self.jumping_frames_r:  # flip x, and not y
            self.jumping_frames_l.append(pygame.transform.flip(frame, True, False))

        # run frames
        self.run_frames_r = []
        run_dir = os.path.join(self.game.img_dir, s.PLAYER_RUN)
        for image in os.listdir(run_dir):
            frame = pygame.image.load(os.path.join(run_dir, image)).convert()
            rect = frame.get_rect()
            frame = pygame.transform.scale(frame, (int(rect.width * 0.2),
                                                   int(rect.height * 0.2)))
            frame.set_colorkey(s.BLACK)
            self.run_frames_r.append(frame)

        self.run_frames_l = []
        for frame in self.run_frames_r:  # flip x, and not y
            self.run_frames_l.append(pygame.transform.flip(frame, True, False))

        # shooting frames
        self.shooting_frames_r = []
        shot_dir = os.path.join(self.game.img_dir, s.PLAYER_SHOT)
        for image in os.listdir(shot_dir):
            frame = pygame.image.load(os.path.join(shot_dir, image)).convert()
            rect = frame.get_rect()
            frame = pygame.transform.scale(frame, (int(rect.width * 0.2),
                                                   int(rect.height * 0.2)))
            frame.set_colorkey(s.BLACK)
            self.shooting_frames_r.append(frame)

        self.shooting_frames_l = []
        for frame in self.shooting_frames_r:  # flip x, and not y
            self.shooting_frames_l.append(pygame.transform.flip(frame, True, False))

    def jump(self):
        """Jumps the player.

        Jumps only if player is on platform, to avoid double jumping.
        """

        self.rect.x += 2  # see upto 2 pixels below
        plat_hits = pygame.sprite.spritecollide(self, self.game.platforms, False)  # don't kill
        base_hits = pygame.sprite.spritecollide(self, self.game.bases, False)
        self.rect.x -= 2

        hits = plat_hits or base_hits

        if hits and not self.jumping:
            # add sound for jumping
            self.jumping = True
            self.vel.y = s.PLAYER_JUMP_VEL * -1

    def jump_cut(self):
        """Stop the jump if key is released.

        This allows the Player sprite to jump higher iff key is kept
        pressed down.
        """

        if self.jumping:
            if self.vel.y < s.JUMP_THRESHOLD * -1:
                self.vel.y = s.JUMP_THRESHOLD * -1

    def update(self):
        """Update attributes of the player.

        Movements, animation, friction and gravity.
        """

        self.animate()

        # apply gravity to player
        self.acc = vec(0, s.PLAYER_GRAV)

        keys = pygame.key.get_pressed()

        # add acceleration if key is pressed
        if keys[pygame.K_LEFT]:
            self.acc.x = s.PLAYER_ACC * -1
        elif keys[pygame.K_RIGHT]:
            self.acc.x = s.PLAYER_ACC

        # apply friction
        self.acc.x += self.vel.x * s.PLAYER_FRICTION * -1

        # v = u + at | t = 1
        self.vel += self.acc
        # if vel is very low, stop movement.
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0

        # x = ut + 0.5 * at**2 | t = 1
        self.pos += self.vel + 0.5 * self.acc

        # prevent player from going towards left
        if self.rect.left < 0:
            self.pos.x = self.rect.left + 50

        # update the position of the sprite with calculated pos
        self.rect.midbottom = self.pos

    def animate(self):
        """Handles player animation.
        """

        now = pygame.time.get_ticks()

        if self.vel.x != 0:
            self.running = True
        else:
            self.running = False

        # show running animation
        if self.running:
            if now - self.last_update > s.PLAYER_RUN_FREQ:
                self.last_update = now
                # get index of the next frame
                self.current_frame = (self.current_frame + 1) % len(self.run_frames_l)
                bottom = self.rect.bottom

                if self.vel.x > 0:
                    self.image = self.run_frames_r[self.current_frame]
                else:
                    self.image = self.run_frames_l[self.current_frame]

                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # show idle animation
        if not self.jumping and not self.running:
            if now - self.last_update > s.PLAYER_IDLE_FREQ:
                self.last_update = now
                # get index of the next frame
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames_r)
                bottom = self.rect.bottom

                if self.pos.x > 0:
                    self.image = self.standing_frames_r[self.current_frame]
                else:
                    self.image = self.standing_frames_l[self.current_frame]

                self.rect = self.image.get_rect()
                self.rect.bottom = bottom

        # show shooting animation

        # show hurt animation

        self.mask = pygame.mask.from_surface(self.image)


class Slime(pygame.sprite.Sprite):

    def __init__(self, game):
        self.layer = s.ENEMY_LAYER
        groups = game.all_sprites, game.enemies
        super(Slime, self).__init__(groups)

        self.game = game
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.walk_images[0]
        self.rect = self.image.get_rect()
        self.rect.left = s.WIDTH
        self.rect.bottom = s.HEIGHT - s.BASE_HEIGHT + 5
        self.vx = random.randrange(1, 4)  # speed

    def load_images(self):
        """Loads images from spritesheet.
        """

        self.walk_images = [
            self.game.enemy_spritesheet.get_image(52, 125, 50, 28, scale=1.5),
            self.game.enemy_spritesheet.get_image(0, 125, 51, 26, scale=1.5)
        ]

        for frame in self.walk_images:
            frame.set_colorkey(s.BLACK)

        self.die_image = self.game.enemy_spritesheet.get_image(0, 112, 59, 12)
        self.die_image.set_colorkey(s.BLACK)

    def update(self):
        """Update the sprite.

        Animate, Update position, kill if out of screen.
        """

        self.animate()

        self.rect.x -= self.vx

        if self.rect.right < 0:
            self.kill()

    def animate(self):
        """Handles sprite animation.
        """

        now = pygame.time.get_ticks()

        if now - self.last_update > 180:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.walk_images)
            self.image = self.walk_images[self.current_frame]

        self.mask = pygame.mask.from_surface(self.image)
