import math

from pygame import fastevent
from tools.load_asset import *
from collision import *


class CuteGirl:
    def __init__(self, transform: Transform, animate_time, camera_pos: Point, attack_callback_event, bridge, heart=3):
        # attack event callback
        self.attack_callback_event = attack_callback_event
        self.attacking = False

        self.camera_pos = camera_pos 
        # center of player
        self.transform = transform

        # heart of player
        self.heart = heart

        # some declare for animation
        self.animate_time = animate_time
        self.idle = load_all_image(os.path.join("Character", "Idle"))
        self.attack = load_all_image(os.path.join("Character", "Attack"))
        self.die = load_all_image(os.path.join("Character", "Die"))
        self.hurt = load_all_image(os.path.join("Character", "Hurt"))
        self.jump = load_all_image(os.path.join("Character", "Jump"))
        self.walk = load_all_image(os.path.join("Character", "Walk")) 

        self.immune = load_all_image(os.path.join("Items", "Immune"))

        self.start_tick = pygame.time.get_ticks()/1000
        self.animate_tick = {
            "attack": self.start_tick,
            "die": self.start_tick,
            "hurt": self.start_tick,
            "jump": 0,
            "walk": 0
        }

        # collision for player
        self.collider = BoxCollider(self.transform.position, 100, 250)

        # state of animation
        self.previous_state = "idle"
        self.state = "idle"

        # when player death
        self.death = False

        self.facing_right = False

        self.is_grounding = False

        # declar for velocity and acceleration
        self.velocity = Point(0,0)
        self.g = 500

        self.jumping_v = -600

        self.moving = 0
        self.speed = 300

        # freeze x axis
        self.freeze_x = False

        self.fire_level = 1

        self.x_moving_range = (50, 9000)

        # when character stand on the bridge
        self.on_bridge = False
        self.bridge = bridge

        self.is_immune = False
        self.immune_time = 0

        self.num_of_coin = 0

        self.attack_sound = load_sound("hit.wav")
        

    def update(self, delta_time):
        # immune effect when player collected item
        if self.is_immune:
            self.immune_time -= delta_time
            if self.immune_time < 0:
                self.is_immune = False
        # die
        if self.heart <= 0 and self.state != "die":
            self.die_event(pygame.time.get_ticks()/1000)

        if self.state == "die":
            self.immune_time = 0
            self.is_immune = False
            return
        
        if self.state == "hurt":
            sign = 1
            if self.facing_right:
                sign = -1
            new_x_pos = self.transform.position.x + sign * 200 * delta_time
            
            if new_x_pos > self.x_moving_range[0] and new_x_pos < self.x_moving_range[1]:
                self.transform.position.x = new_x_pos
            return

        # update state animation
        if self.is_grounding or self.on_bridge:
            if self.state == "attack":
                pass
            elif self.moving == 0 and self.state != "idle":
                self.newstate("idle")
            elif self.moving != 0 and self.state != "walk":
                self.newstate("walk")

        # check facing of the girl
        if (self.facing_right and self.moving == -1) or (not self.facing_right and self.moving == 1):
            self.facing_right = not self.facing_right

        # if attack, stop moving
        if (self.state == "attack" and self.is_grounding) or self.freeze_x:
            self.velocity.x = 0
        else:
            self.velocity.x = self.moving * self.speed

        # on falling
        if not self.is_grounding and not self.on_bridge:
            self.velocity.y += self.g * delta_time
            self.transform.translate(0, self.velocity.y * delta_time)
        elif self.on_bridge:
            self.transform.translate(100 * delta_time * self.bridge.direction , 0)

        # check moving available
        new_x_pos = self.transform.position.x + self.velocity.x * delta_time
        if new_x_pos > self.x_moving_range[0] and new_x_pos < self.x_moving_range[1]:
            self.transform.position.x = new_x_pos

        self.freeze_x = False

    def check_image_direction(self, image):
        if self.facing_right:
            return image
        return pygame.transform.flip(image, True, False)

    def draw(self, surface):
        pos = self.transform.position.x - self.camera_pos.x, self.transform.position.y - self.camera_pos.y
        current_tick = pygame.time.get_ticks()/1000

        try:
        # if True:
            if self.state == "idle":
                index = int(current_tick / self.animate_time.get("idle")) % len(self.idle)
                image = self.check_image_direction(self.idle[index][0])

                surface.blit(image, self.idle[index][1].move(-200 + pos[0], -200 + pos[1]))

            elif self.state == "walk":
                index = int((current_tick - self.animate_tick["walk"]) / self.animate_time.get("walk")) % len(self.walk)
                image = self.check_image_direction(self.walk[index][0])

                surface.blit(image, self.walk[index][1].move(-200 + pos[0], -200 + pos[1]))

            elif self.state == "jump":
                index = int((current_tick - self.animate_tick["jump"]) / self.animate_time.get("jump")) % len(self.jump)
                image = self.check_image_direction(self.jump[index][0])

                surface.blit(image, self.jump[index][1].move(-200 + pos[0], -200 + pos[1]))

            elif self.state == "hurt":
                index = int((current_tick - self.animate_tick["hurt"]) / self.animate_time.get("hurt"))
                if index >= len(self.hurt):
                    index = len(self.hurt) - 1
                    # chanage state back
                    if self.previous_state != "attack":
                        self.state = self.previous_state
                    else:
                        self.newstate("idle")
                    # lost one heart
                    self.heart -= 1

                image = self.check_image_direction(self.hurt[index][0])
                surface.blit(image, self.hurt[index][1].move(-200 + pos[0], -200 + pos[1]))

            elif self.state == "die":
                # no loop this animation
                index = int((current_tick - self.animate_tick["die"]) / self.animate_time.get("die"))
                if index >= len(self.die):
                    index = len(self.die) - 1
                    # complete animation
                    self.death = True

                image = self.check_image_direction(self.die[index][0])
                # draw an image
                surface.blit(image, self.die[index][1].move(-200 + pos[0], -200 + pos[1]))

            elif self.state == "attack":
                index = int((current_tick - self.animate_tick["attack"]) / self.animate_time.get("attack"))

                if index == 8 and not self.attacking:
                    self.attack_callback_event()
                    self.attacking = True

                if index >= len(self.attack):
                    # complete attack
                    index = len(self.attack) - 1
                    self.attacking = False

                    self.state = self.previous_state
                image = self.check_image_direction(self.attack[index][0])
                # draw an image    
                surface.blit(image, self.attack[index][1].move(-200 + pos[0], -200 + pos[1]))

            if self.is_immune:
                idx = int(current_tick / 0.2) % 3
                surface.blit(self.immune[idx][0], self.immune[idx][1].move(-200 + pos[0], -200 + pos[1]))
        except:
            print("Error on draw image from the animation")
            raise SystemExit
        # pygame.draw.rect(surface, (0,255,0), pygame.Rect(self.transform.position.x - 50 - self.camera_pos.x, self.transform.position.y - 125 - self.camera_pos.y, 100, 250))

    def hurt_event(self, current_time, is_right):
        if self.is_immune:
            return

        if (is_right and not self.facing_right) or (not is_right and self.facing_right):
            self.facing_right = not self.facing_right
            
        if self.state in ["hurt", "die"]:
            return
        self.animate_tick["hurt"] = current_time
        # change state to hurt
        self.newstate("hurt")

    def die_event(self, current_time):
        self.animate_tick["die"] = current_time
        # change state to die
        self.newstate("die")

    def jump_event(self, current_time):
        if not self.is_grounding and not self.on_bridge:
            return
        
        self.velocity.y = self.jumping_v
        self.animate_tick["jump"] = current_time
        self.is_grounding = False
        self.on_bridge = False
        self.newstate("jump")

    def attack_event(self, current_time):
        if self.state not in ["hurt", "die", "attack"]:
            self.animate_tick["attack"] = current_time
            self.newstate("attack")
            self.attack_sound.stop()
            self.attack_sound.play()
    
    def fall_event(self):
        if self.is_grounding:
            self.is_grounding = False
        if self.state == "walk":
            self.newstate("idle")
    
    def on_collision(self, collider):
        if collider.obj_type == "ground":
            # if player on top of the ground
            if self.transform.position.y + 110 < collider.position.y - collider.height/2 and self.transform.position.x + 100 > collider.position.x - collider.width/2 and self.transform.position.x - 100 < collider.position.x + collider.width/2 :
                if not self.is_grounding:
                    self.is_grounding = True
                    self.newstate("idle")
            elif self.transform.position.x + 100 > collider.position.x - collider.width/2 and self.transform.position.x - 100 < collider.position.x + collider.width/2:
                self.freeze_x = True
    
    def newstate(self, newstate):
        self.previous_state = self.state
        self.state = newstate

    def update_weapon(self):
        self.fire_level = 2

    def increate_heart(self):
        self.heart += 1

    def immune_event(self):
        self.is_immune = True
        self.immune_time = 20

    
class Ground:
    def __init__(self, postion:Point, height, width, camera_pos):
        self.position = postion
        self.width = width
        self.height = height
        self.camera_pos = camera_pos
        self.obj_type = "ground"

        self.collider = BoxCollider(self.position, self.width, self.height)
        self.visible = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, (255,0,0), pygame.Rect(self.position.x - self.width/2 - self.camera_pos.x, self.position.y - self.height/2 - self.camera_pos.y, self.width, self.height))

    def update(self):
        pass
    def on_collision(self, collider):
        pass


class Chomper:
    def __init__(self, transform:Transform, player_transfrom:Transform, camera_pos, moving_range, vision_range):
        self.transfrom = transform
        self.player_transfrom = player_transfrom
        self.camera_pos = camera_pos
        self.moving_range = moving_range
        self.vision_range = vision_range

        # state of enemy
        self.state = "idle"

        # initial time for each animation
        self.animate_tick = {
            "idle" : 0,
            "walk" : 0,
            "attack": 0,
            "die": 0
        }
        
        # time change sprite of each animation
        self.animate_time = {
            "idle" : 0.1,
            "walk" : 0.1,
            "attack": 0.1,
            "die": 0.2
        }

        # image assets
        self.attack = load_all_image(os.path.join("Enemies", "Chomper", "Attack"))
        self.walk = load_all_image(os.path.join("Enemies", "Chomper", "Walk"))
        self.idle = load_all_image(os.path.join("Enemies", "Chomper", "Idle"))
        self.die = load_all_image(os.path.join("Enemies", "Chomper", "Death"))

        self.direction = -1

        self.death = False
        self.collider = CircleCollier(Point(self.transfrom.position.x + self.direction * 10, self.transfrom.position.y - 70), 60, enable=False)

        self.speed = 500

        self.ready = False

        self.hp = 3

        self.visible = False 

        self.attack_sound = load_sound(os.path.join("chomper", "attack.mp3"))
        self.die_sound = load_sound(os.path.join("chomper", "die.mp3"))


        
    def update(self, delta_time):
        if self.state == "die":
            return

        # update collider position
        self.collider.center.equal(self.transfrom.position.x + self.direction * 100, self.transfrom.position.y - 70)

        # distance from enemy and player
        arrange = self.transfrom.position.x - self.player_transfrom.position.x
        
        if abs(arrange) < self.vision_range:
            self.ready = True

        if not self.ready:
            return
        
        if arrange < 0:
            self.direction = 1
        else:
            self.direction = -1

        if self.state != "attack":
            if abs(arrange) < 50:
                self.state = "attack"
                self.animate_tick["attack"] = pygame.time.get_ticks()/1000
                self.attack_sound.stop()
                self.attack_sound.play()
            else:
                newpos = self.transfrom.position.x + self.direction * self.speed * delta_time
                if newpos < self.moving_range[0] or newpos > self.moving_range[1]:
                    self.state = "idle"
                else:
                    self.state = "walk"
                    self.transfrom.position.x = newpos
            self.collider.enable = False

    def draw(self, surface):
        current_time = pygame.time.get_ticks()/1000

        if self.state == "idle":
            index = int((current_time - self.animate_tick["idle"]) / self.animate_time["idle"]) % len(self.idle)
            image = self.check_image_direction(self.idle[index][0])

            surface.blit(image, self.idle[index][1].move(self.transfrom.position.x - self.idle[index][1].width/2 - self.camera_pos.x, self.transfrom.position.y - self.idle[index][1].width/2 - self.camera_pos.y))
          
        elif self.state == "attack":
            index = int((current_time - self.animate_tick["attack"]) / self.animate_time["attack"])
            if index > 6 and not self.collider.enable:
                self.collider.enable = True

            if index >= len(self.attack):
                index = len(self.idle)
                self.state = "idle"
            image = self.check_image_direction(self.attack[index][0])

            surface.blit(image, self.attack[index][1].move(self.transfrom.position.x - self.camera_pos.x - self.attack[index][1].width/2, self.transfrom.position.y - self.camera_pos.y - self.attack[index][1].width/2))

        elif self.state == "die":
            index = int((current_time - self.animate_tick["die"]) / self.animate_time["die"])
            if index >= len(self.die):
                self.death = True
                return

            image = self.check_image_direction(self.die[index][0])

            surface.blit(image, self.die[index][1].move(self.transfrom.position.x - self.camera_pos.x - self.die[index][1].width/2, self.transfrom.position.y - self.camera_pos.y - self.die[index][1].width/2))

        elif self.state == "walk":
            index = int((current_time - self.animate_tick["walk"]) / self.animate_time["walk"]) % len(self.walk)
            image = self.check_image_direction(self.walk[index][0])

            surface.blit(image, self.walk[index][1].move(self.transfrom.position.x - self.camera_pos.x - self.walk[index][1].width/2, self.transfrom.position.y - self.camera_pos.y - self.walk[index][1].width/2))
        

        # if self.collider.enable:
        # pygame.draw.circle(surface, (255,0,0), (self.transfrom.position.x + self.direction * 100 - self.camera_pos.x, self.transfrom.position.y - self.camera_pos.y - 70), 60)

    def damaged(self, damage):
        if self.state == "die":
            return
        self.hp -= damage
        if self.hp <= 0:
            self.state = "die"
            self.animate_tick["die"] = pygame.time.get_ticks()/1000
            self.die_sound.stop()
            self.die_sound.play()
    
    def check_image_direction(self, image):
        if self.direction == 1:
            return image
        return pygame.transform.flip(image, True, False)
    

class Fire:
    def __init__(self, tranfrom:Transform, camera_pos, flying_right, level):
        self.transfrom = tranfrom
        self.camera_pos = camera_pos
        self.flying_right = flying_right
        self.level = level % 3
        self.speed = 500

        if self.level == 1:
            self.image = load_image(os.path.join("UI", "StaffSwish.png"))
        else:
            self.image = load_image(os.path.join("UI", "Bullet.png"))

        self.collider = CircleCollier(self.transfrom.position, 60)
    
    def update(self, delta_time):
        self.transfrom.translate(self.flying_right * self.speed * delta_time, 0)

    def draw(self, surface):
        image = self.check_image_direction(self.image[0])
        surface.blit(image, self.image[1].move(self.transfrom.position.x - self.camera_pos.x - 128, self.transfrom.position.y - self.camera_pos.y - 128))
    
    def check_image_direction(self, image):
        if self.flying_right == 1:
            return image
        return pygame.transform.flip(image, True, False)


class Bridge:
    def __init__(self, transfrom:Transform, camera_pos, moving_range, speed):
        self.transfrom = transfrom
        self.camera_pos = camera_pos
        self.moving_range = moving_range
        self.speed = speed

        self.direction = 1
        self.visitable = False

        self.image = load_image(os.path.join("UI", "Bridge.png"), scale=0.5)

        self.collider = BoxCollider(self.transfrom.position, 400, 40)

    def update(self, delta_time):
        if self.transfrom.position.x < self.moving_range[0] or self.transfrom.position.x > self.moving_range[1]:
            self.direction = -self.direction
        self.transfrom.translate(self.speed * self.direction * delta_time, 0)
    
    def draw(self, surface):
        surface.blit(self.image[0], self.image[1].move(self.transfrom.position.x - self.image[1].width/2 - self.camera_pos.x, self.transfrom.position.y - self.image[1].height/2 - self.camera_pos.y))
        
        # pygame.draw.rect(surface, (255,0,0), pygame.Rect(self.transfrom.position.x - 200 - self.camera_pos.x, self.transfrom.position.y - 20 - self.camera_pos.y, 400, 40))

class Gunner:
    def __init__(self, position, camera_pos, character_pos, hp=20):
        self.position = position
        self.camera_pos = camera_pos
        self.character_pos  = character_pos

        self.state = "comming"

        self.comming_bg = load_all_image_not_cache(os.path.join("Enemies", "Gunner", "Cutscene", "Background"))
        self.comming_ch = load_all_image_not_cache(os.path.join("Enemies", "Gunner", "Cutscene", "Character"), scale=0.5) 
        self.attack = load_all_image_not_cache(os.path.join("Enemies", "Gunner", "BeamAttack"))
        self.die = load_all_image_not_cache(os.path.join("Enemies", "Gunner", "Death"))
        self.idle = load_all_image_not_cache(os.path.join("Enemies", "Gunner", "Idle"))

        self.beam = load_image(os.path.join("UI", "Beam.png"), scale=0.5)
        self.image_fire = None


        self.animate_tick = {
            "idle": 0,
            "comming": 0,
            "attack": 0,
            "die":0
        }

        self.animate_time = {
            "idle": 0.2,
            "comming": 0.3,
            "attack": 0.1,
            "die":0.3
        }
        
        self.visitable = False

        self._x_pading = 250

        # collision
        self.collider = BoxCollider(Point(self.position.x , self.position.y - 80), 300, 150)

        self.death = False

        self.wating = 0

        self.length = 0
        self.angle = 0


        self.firing = False

        self.cooldown_time = 5

        self.hp = hp

        self.attack_sound = load_sound(os.path.join("gunner", "attack.mp3"))

        self.attack_sound_played = False
        

    def update(self, delta_time):
        if self.state == "die":
            return

        if self.state == "comming":
            return

        self.cooldown_time -= delta_time
        if self.cooldown_time <= 0:
            self.attack_event(pygame.time.get_ticks()/1000)
            self.cooldown_time = 8

    def draw(self, surface):
        current_time = pygame.time.get_ticks()/1000

        if self.state == "comming":
            idx = int((current_time - self.animate_tick["comming"]) / self.animate_time["comming"])
            if idx >= len(self.comming_bg):
                idx = len(self.comming_bg) - 1
                # new state
                self.state = "idle"
                self.animate_tick["idle"] = current_time

            surface.blit(self.comming_bg[idx][0], self.comming_bg[idx][1].move(self.position.x - self.comming_bg[idx][1].width/2 - self.camera_pos.x + self._x_pading, self.position.y - self.comming_bg[idx][1].height/2 - self.camera_pos.y))
            surface.blit(self.comming_ch[idx][0], self.comming_ch[idx][1].move(self.position.x - self.comming_ch[idx][1].width/2 - self.camera_pos.x + self._x_pading, self.position.y - self.comming_ch[idx][1].height/2 - self.camera_pos.y))

        elif self.state == "idle":
            idx = int((current_time - self.animate_tick["idle"]) / self.animate_time["idle"]) % len(self.idle)
            surface.blit(self.idle[idx][0], self.idle[idx][1].move(self.position.x - self.idle[idx][1].width/2 - self.camera_pos.x, self.position.y - self.idle[idx][1].height/2 - self.camera_pos.y))

        elif self.state == "attack":
            idx = int((current_time - self.animate_tick["attack"]) / self.animate_time["attack"])
            # draw firer
            if idx == 24 and not self.attack_sound_played:
                self.attack_sound.stop()
                self.attack_sound.play()
            if idx >= 24 and idx <= 26:
                self.firing = True
                surface.blit(self.image_fire[0], self.image_fire[1].move(self.position.x - self.camera_pos.x - self.image_fire[1].width,self.position.y -self.camera_pos.y - 200 ))
            else:
                self.firing = False
            
            if idx >= len(self.attack):
                idx = len(self.attack) - 1
                self.attack_sound_played = False
                # back to idle state 
                self.state = "idle"
                self.animate_tick["idle"] = current_time

            surface.blit(self.attack[idx][0], self.attack[idx][1].move(self.position.x - self.attack[idx][1].width/2 - self.camera_pos.x, self.position.y - self.attack[idx][1].height/2 - self.camera_pos.y))
        
        elif self.state == "die":
            idx = int((current_time - self.animate_tick["die"]) / self.animate_time["die"])
            if idx >= len(self.die) :
                idx = len(self.die) - 1
                self.death = True
                # self.visitable = False

            surface.blit(self.die[idx][0], self.die[idx][1].move(self.position.x - self.die[idx][1].width/2 - self.camera_pos.x, self.position.y - self.die[idx][1].height/2 - self.camera_pos.y))

        # pygame.draw.rect(surface, (255,0,0), pygame.Rect(self.position.x - 150 - self.camera_pos.x, self.position.y - 155 - self.camera_pos.y, 300, 150))


    def calc_fire(self, from_pos:Point, to_pos:Point):
        self.length = math.sqrt((from_pos.x - to_pos.x) ** 2 + (from_pos.y - to_pos.y) ** 2) + 150
        self.angle = math.atan(abs(from_pos.y - to_pos.y - 100) / abs(from_pos.x - to_pos.x)) * (180 / 3.1416)

        image = pygame.transform.scale(self.beam[0] , (int(self.length), self.beam[1].height))
        image = pygame.transform.rotate(image, self.angle)

        return image, image.get_rect()

    def attack_event(self, current_time):
        self.image_fire = self.calc_fire(self.position, self.character_pos)
        self.state = "attack"
        self.animate_tick["attack"] = current_time
    
    def check_beam(self):
        if self.character_pos.x + 50 < self.position.x - self.length:
            return False
        
        s1 = self.character_pos.y + 125 - (self.position.y - 200)
        s2 = s1 / math.tan(self.angle * (3.1416 / 180))
        if self.position.x - s2 > self.character_pos.x + 50:
            return False

        return True

class Box:
    def __init__(self, position, camera_pos, type):
        self.position = position
        self.camera_pos = camera_pos
        self.type = type

        self.collider = BoxCollider(self.position, 180, 180)
        self.image = load_image(os.path.join("Box", "Box.png"))
        self.crack = load_all_image(os.path.join("Box", "Crack"))

        self.crack_tick = 0
        self.visitable = True

        self.expire= False

        self.state = "normal"

    def draw(self, surface):
        # pygame.draw.rect(surface, (255,0,0), pygame.Rect(self.position.x - 90 - self.camera_pos.x, self.position.y - 90 - self.camera_pos.y, 180 , 180))

        if self.state == "normal":
            surface.blit(self.image[0], self.image[1].move(self.position.x - self.image[1].width / 2 - self.camera_pos.x, self.position.y - self.image[1].height / 2 - self.camera_pos.y))
        else:
            current_time = pygame.time.get_ticks()/1000
            idx = int((current_time - self.crack_tick) / 0.3)
            if idx >= len(self.crack):
                self.visitable = False
                self.expire = False
            else:
                surface.blit(self.crack[idx][0], self.crack[idx][1].move(self.position.x - self.crack[idx][1].width / 2 - self.camera_pos.x, self.position.y - self.crack[idx][1].height / 2 - self.camera_pos.y))
   
    def crack_event(self):
        self.state = "crack"
        self.crack_tick = pygame.time.get_ticks()/ 1000
        

class Item:
    def __init__(self, position, camera_pos, type):
        self.position = position
        self.camera_pos = camera_pos
        self.type = type

        self.collider = BoxCollider(self.position, 100, 100)
        self.visitable = True
        
        self.expire = False

        if self.type == "ruby":
            self.image = load_image(os.path.join("Items", "ruby.png"), scale=0.5)

        elif self.type == "weapon":
            self.image = load_image(os.path.join("Items", "fire.png"), scale=0.5)

        elif self.type == "heart":
            self.image = load_image(os.path.join("Items", "HealingGlobe.png"), scale=0.5)  

        elif self.type == "flask":
            self.image = load_image(os.path.join("Items", "flask.png"), scale=0.5)  
        # images
        
    def draw(self, surface):
        # pygame.draw.rect(surface, (255,0,0), pygame.Rect(self.position.x - self.camera_pos.x - 50, self.position.y - self.camera_pos.y - 50, 100, 100))
        surface.blit(self.image[0], self.image[1].move(self.position.x - self.camera_pos.x - self.image[1].width/2, self.position.y - self.camera_pos.y - self.image[1].height/2))

class Text:
    def __init__(self, text, pos, color, size):
        self.text = text
        self.pos = pos
        self.color = color
        self.size = size
        self.font = pygame.font.Font(os.path.join(GAME_FOLDER, "Assets", "Fonts", "BubbleShine.ttf"), self.size)

    def draw(self, surface):
        lb = self.font.render(self.text, True, self.color)
        surface.blit(lb, (self.pos.x, self.pos.y))


class Button:
    def __init__(self, pos, height, width, text:Text):
        self.pos = pos
        self.height = height
        self.width = width
        self.text = text

        self.image = load_image(os.path.join("Menu", "Button.png"))

    def check_click(self, click_pos):
        if self.pos.x > click_pos[0] or self.pos.x + self.width < click_pos[0]:
            return False

        if self.pos.y > click_pos[1] or self.pos.y + self.height < click_pos[1]:
            return False
        
        print("click button {}".format(self.text.text))
        return True

    def draw(self, surface):
        # draw text
        surface.blit(self.image[0], self.image[1].move(self.pos.x, self.pos.y))
        self.text.draw(surface)
