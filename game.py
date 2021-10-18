from pygame.image import load
from objects import *
from tools.helper import is_contain, is_contain_circle, is_contain_two_circle, smooth_calculate


class PlayingScene:
    def __init__(self):
        self.size = self.widthScreen, self.heightScreen = 1500, 1000
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        self._is_running = True

        self.camera_pos = Point(0, 500)


        self.bridge = Bridge(Transform(Point(4200, 1250),0), self.camera_pos, (4200, 4800), 100)

        # init player
        self.cute_girl = CuteGirl(Transform(Point(200, 1400), 0), {"idle": 0.2,
                                                                  "attack": 0.03,
                                                                  "die": 0.2,
                                                                  "hurt": 0.1,
                                                                  "jump": 0.2,
                                                                  "walk": 0.04},
        self.camera_pos,
        self.fire_event,
        self.bridge,
        heart=10
        )

        self.background = load_image(os.path.join("UI", "background.png"))

        self.grounds = [Ground(Point(1000, 1700), 180, 2100, self.camera_pos), 
                        Ground(Point(2600, 1550), 180, 512, self.camera_pos),
                        Ground(Point(3500, 1300), 180, 868, self.camera_pos),
                        Ground(Point(5300, 1300), 180, 512, self.camera_pos),
                        Ground(Point(8000, 1500), 180, 4350, self.camera_pos),
                        ]
        
        # init enemies
        self.chompers = [
                        #  Chomper(Transform(Point(1000, 1620), 0), self.cute_girl.transform, self.camera_pos, (50, 2030), 500),
                        #  Chomper(Transform(Point(1500, 1620), 0), self.cute_girl.transform, self.camera_pos, (50, 2030), 500),
                        #  Chomper(Transform(Point(2600, 1470), 0), self.cute_girl.transform, self.camera_pos, (2400, 2830), 500),
                        #  Chomper(Transform(Point(3500, 1220), 0), self.cute_girl.transform, self.camera_pos, (3120, 3910), 500),
                        #  Chomper(Transform(Point(5400, 1220), 0), self.cute_girl.transform, self.camera_pos, (5100, 5530), 500),
                        #  Chomper(Transform(Point(6400, 1420), 0), self.cute_girl.transform, self.camera_pos, (5875, 8030), 500),
                         Chomper(Transform(Point(6700, 1420), 0), self.cute_girl.transform, self.camera_pos, (5875, 8030), 500)
                        ]
        # init boss
        self.gunner = Gunner(Point(9500, 1230), self.camera_pos, self.cute_girl.transform.position)

        # init gift box
        self.boxes = [
                        Box(Point(1800, 1500), self.camera_pos, "weapon"),
                        Box(Point(3700, 1100), self.camera_pos, "flask"),
                        Box(Point(5500, 1100), self.camera_pos, "heart"),
        ]
        self.items = []

        # init coins
        self.coins = [
            Item(Point(400, 1500), self.camera_pos, "ruby"),
            Item(Point(800, 1500), self.camera_pos, "ruby"),
            Item(Point(1200, 1500), self.camera_pos, "ruby"),
            Item(Point(1600, 1500), self.camera_pos, "ruby"),
            Item(Point(2000, 1500), self.camera_pos, "ruby"),
            Item(Point(3300, 1000), self.camera_pos, "ruby"),
            Item(Point(3600, 1000), self.camera_pos, "ruby"),
            Item(Point(3900, 1000), self.camera_pos, "ruby"),
            Item(Point(4200, 1000), self.camera_pos, "ruby"),
        ]

        
        self.fires = []

        # collision
        self.spatial_hashmap = SpatialHashmap(50)

        self.jumping = False
        self.moving = 0

    
        # init for deltatime
        self.last_frame_tick = pygame.time.get_ticks()/1000
        self.current_tick = pygame.time.get_ticks()/1000

        self.freeze_cam = False

        # init some field for UI
        self.heart_img = load_image(os.path.join("UI", "heart.png"))
        self.ruby_img = load_image(os.path.join("Items", "ruby.png"), scale=0.25)

        self.heart_txt = Text("x  " + str(self.cute_girl.heart), Point(100,10), (255,0,0), 40)
        self.ruby_txt = Text(str(self.cute_girl.num_of_coin), Point(100,100), (255,0,0), 40)

        self.boss_heart = load_image(os.path.join("UI", "boss_heart.png"))


    def on_render(self):
        self._display_surf.fill((0,0,0))
        self._display_surf.blit(self.background[0], self.background[1].move(-self.camera_pos.x, -self.camera_pos.y))

        if self.gunner.visitable:
            self.gunner.draw(self._display_surf)
            # draw heart for gunner
            self._display_surf.blit(self.boss_heart[0], self.boss_heart[1].move(500, -40))

            boss_heart_length = self.gunner.hp/ 20 * 580
            pygame.draw.rect(self._display_surf, (255,0,0), pygame.Rect(530 + (580 - boss_heart_length), 75, boss_heart_length, 25))
        # draw bright
        if self.bridge.visitable:
            self.bridge.draw(self._display_surf)
        
        # draw gift boxes
        for box in self.boxes:
            if box.visitable:
                box.draw(self._display_surf)

        # draw character
        self.cute_girl.draw(self._display_surf)

        # draw coin
        for coin in self.coins:
            if coin.visitable:
                coin.draw(self._display_surf)

        # draw item
        for item in self.items:
            if item.visitable:
                item.draw(self._display_surf)

        # draw enemies
        for chomper in self.chompers:
            if chomper.visible:
                chomper.draw(self._display_surf)


        
        # draw death panel when player is dying
        if self.cute_girl.death:
            self.death_panel()

        # draw firer
        for fire in self.fires:
            fire.draw(self._display_surf)

        # draw some UI
        self._display_surf.blit(self.heart_img[0], self.heart_img[1].move(10, 10))
        self.heart_txt.text = "x  " +  str(self.cute_girl.heart)
        self.heart_txt.draw(self._display_surf)

        self._display_surf.blit(self.ruby_img[0], self.ruby_img[1].move(10, 100))
        self.ruby_txt.text = str(self.cute_girl.num_of_coin)
        self.ruby_txt.draw(self._display_surf)


        pygame.display.flip()

    def on_loop(self):
        # when player is death
        if self.cute_girl.death:
            return

        if len(self.chompers) == 0 and not self.gunner.visitable:
            self.boss_comming_animation()

        # check y coordinate
        if self.cute_girl.transform.position.y > 3000:
            # find new position and sub player heart
            for ground in reversed(self.grounds):
                if ground.position.x < self.cute_girl.transform.position.x:
                    self.cute_girl.transform.position.equal(ground.position.x + ground.width/2 - 300, ground.position.y - ground.height/2 - 200)
                    self.cute_girl.velocity.y = 0
                    break
            self.cute_girl.heart -= 1
            
        # calculate delta time
        self.current_tick = pygame.time.get_ticks()/1000
        delta_time = self.current_tick - self.last_frame_tick
        self.last_frame_tick = self.current_tick

        # camera follow player
        if not self.freeze_cam:
            # self.camera_pos.equal(self.cute_girl.transform.position.x - 300, self.cute_girl.transform.position.y - 500)
            pos = smooth_calculate(self.camera_pos, Point(self.cute_girl.transform.position.x - 300, self.cute_girl.transform.position.y - 500), 3 * delta_time)
            self.camera_pos.equal(pos.x, pos.y)
            if self.camera_pos.x < 0 :
                self.camera_pos.x = 0
            
            if self.camera_pos.y > 1000:
                self.camera_pos.y = 1000

        self.check_visitable()

        self.collisions()

        # call event
        if self.jumping :
            self.cute_girl.jump_event(self.current_tick)
            self.jumping = False
        
        # moving is value from -1 to 1, -1 to left, 1 to right and 0 for not moving
        self.cute_girl.moving = self.moving

        # update a cute girl
        self.cute_girl.update(delta_time)

        for chomper in self.chompers:
            if chomper.transfrom.position.x < self.camera_pos.x + self.widthScreen + 300 and chomper.transfrom.position.x > self.camera_pos.x - 300:
                chomper.update(delta_time)

        # firer controller 
        for fire in self.fires:
            fire.update(delta_time)
            if fire.transfrom.position.x < self.camera_pos.x - 200 or fire.transfrom.position.x > self.camera_pos.x + self.widthScreen + 200:
                self.fires.remove(fire)
        
        # update moving of the bridge
        if self.bridge.visitable:
            self.bridge.update(delta_time)
        
        # update gunner
        if self.gunner.visitable:
            if self.gunner.firing:
                if self.gunner.check_beam() :
                    self.cute_girl.hurt_event(self.current_tick, True)
            self.gunner.update(delta_time)
        
    def check_visitable(self):
                # calcute visible for grounds and chompers and bridge
        for ground in self.grounds:
            if ground.position.x + ground.width/2 > self.camera_pos.x and ground.position.x - ground.width/2 < self.camera_pos.x + self.widthScreen:
                ground.visible = True
            else:
                ground.visible = False

        for chomper in self.chompers:
            if chomper.death:
                self.chompers.remove(chomper)
                continue

            if chomper.transfrom.position.x + 150 > self.camera_pos.x and chomper.transfrom.position.x - 150 < self.camera_pos.x + self.widthScreen:
                chomper.visible = True
            else:
                chomper.visible = False
        
        # check visitale for gift box object
        for box in self.boxes:
            if box.expire:
                continue

            if box.position.x + 90 > self.camera_pos.x and box.position.x - 90 < self.camera_pos.x + self.widthScreen:
                box.visible = True
            else:
                box.visible = False

        # check visitable for items
        for item in self.items:
            if item.expire:
                continue

            if item.position.x + 90 > self.camera_pos.x and item.position.x - 90 < self.camera_pos.x + self.widthScreen:
                item.visible = True
            else:
                item.visible = False

        # check visitable for coins
        for coin in self.coins:
            if coin.position.x + 90 > self.camera_pos.x and coin.position.x - 90 < self.camera_pos.x + self.widthScreen:
                coin.visible = True
            else:
                coin.visible = False
        
        if self.bridge.transfrom.position.x + 250 > self.camera_pos.x and self.bridge.transfrom.position.x - 250 < self.camera_pos.x + self.widthScreen:
            self.bridge.visitable = True
        else:
            self.bridge.visitable = False

    def collisions(self):
        # collision between player and grounds
        count = 0
        for ground in self.grounds:
            if ground.visible:
                if is_contain(ground.collider, self.cute_girl.collider):
                    self.cute_girl.on_collision(ground)
                    count += 1

        # moving out of the ground
        if count == 0:
            self.cute_girl.fall_event()

        # collision between player and chomper
        for chomper in self.chompers:
            if chomper.visible:
                if is_contain_circle(chomper.collider, self.cute_girl.collider):
                    is_right = True
                    if self.cute_girl.transform.position.x > chomper.transfrom.position.x:
                        is_right = False
                    self.cute_girl.hurt_event(self.current_tick, is_right)
            
        # collision between firer and chompers
        for chomper in self.chompers:
            if chomper.visible:
                for fire in self.fires:
                    if is_contain_two_circle(chomper.collider, fire.collider):
                        # pop fire
                        self.fires.remove(fire)
                        # damage to chomper
                        chomper.damaged(self.cute_girl.fire_level)

        # collision between character and bridge
        if self.bridge.visitable:
            if is_contain(self.cute_girl.collider, self.bridge.collider):
                self.cute_girl.on_bridge = True
            else:
                self.cute_girl.on_bridge = False       
        
        # collision between firer and gift box
        for box in self.boxes:
            if box.visitable:
                for fire in self.fires:
                    if is_contain_circle(fire.collider, box.collider):
                        if box.state == "normal":
                            box.crack_event()
                            # init new item
                            if box.type == "weapon":
                                self.items.append(Item(box.position, self.camera_pos, "weapon"))
                            elif box.type == "heart":
                                self.items.append(Item(box.position, self.camera_pos, "heart"))
                            elif box.type == "flask":
                                self.items.append(Item(box.position, self.camera_pos, "flask"))
        
        # collision between character and items
        for item in self.items:
            if item.visitable:
                if is_contain(self.cute_girl.collider, item.collider):
                    # collect item
                    if item.type == "weapon":
                        self.cute_girl.update_weapon()
                        # remove this item
                    elif item.type == "heart":
                        self.cute_girl.increate_heart()
                    elif item.type == "flask":
                        self.cute_girl.immune_event()
                    
                    self.items.remove(item)
                    
        # collision between character and coins
        for coin in self.coins:
            if coin.visitable:
                if is_contain(self.cute_girl.collider, coin.collider):
                    # collect coin
                    self.cute_girl.num_of_coin += 1
                    self.coins.remove(coin)

        # collision between gunner and charactere
        if self.gunner.visitable and self.gunner.hp > 0:
            for fire in self.fires:
                if is_contain_circle(fire.collider, self.gunner.collider):
                    # attack
                    self.gunner.hp -= self.cute_girl.fire_level
                    if self.gunner.hp == 0:
                        # boss die
                        self.gunner.state = "die"
                        self.gunner.animate_tick["die"] = self.current_tick

                    self.fires.remove(fire)


    def death_panel(self):
        pygame.draw.rect(self._display_surf, (255,255,255), pygame.Rect(500, 250, 500, 500))

    def boss_comming_animation(self):
        target_camera_pos = Point(8500, 780)

        self.moving_camera(target_camera_pos, 500)

        self.boss_comming()

        self.moving_player(Point(8800, 1285.7))

        self.freeze_cam = True
        self.cute_girl.x_moving_range = (8550, 9200)

    def moving_player(self, to_pos):
        self.cute_girl.transform.position.y = to_pos.y
        self.cute_girl.moving = 1
        self.cute_girl.is_grounding = True

        while True:
            self.current_tick = pygame.time.get_ticks()/1000
            delta_time = self.current_tick - self.last_frame_tick
            self.last_frame_tick = self.current_tick
            pos = smooth_calculate(self.camera_pos, Point(self.cute_girl.transform.position.x - 300, self.cute_girl.transform.position.y - 500), 3 * delta_time)
            self.camera_pos.equal(pos.x, pos.y)

            if to_pos.x < self.cute_girl.transform.position.x:
                self.cute_girl.moving = 0
                break

            self.cute_girl.update(delta_time)
            self.on_render()
  
    def moving_camera(self, to_pos, speed):
        while True:
            self.current_tick = pygame.time.get_ticks()/1000
            delta_time = self.current_tick - self.last_frame_tick
            self.last_frame_tick = self.current_tick

            if to_pos.x < self.camera_pos.x:
                break
            self.camera_pos.x += speed * delta_time

            self.on_render()

    def boss_comming(self):
        self.gunner.visitable = True
        self.gunner.animate_tick["comming"] = self.current_tick

        while True:
            if self.gunner.state == "idle":
                break

            self.current_tick = pygame.time.get_ticks()/1000
            delta_time = self.current_tick - self.last_frame_tick
            self.last_frame_tick = self.current_tick

            self.gunner.update(delta_time)
            self.on_render()


    def on_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jumping = True
                elif event.key == pygame.K_d:
                    self.moving += 1
                elif event.key == pygame.K_a:
                    self.moving -=1
                elif event.key == pygame.K_f:
                    self.attack_event()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    self.moving -= 1
                elif event.key == pygame.K_a:
                    self.moving += 1
    
    def attack_event(self):
        self.cute_girl.attack_event(pygame.time.get_ticks()/1000)
        # self.fire_event()

    def fire_event(self):
        sign = -1
        if self.cute_girl.facing_right:
            sign = 1
        transform = Transform(Point(self.cute_girl.transform.position.x, self.cute_girl.transform.position.y + 50), 0)

        self.fires.append(Fire(transform, self.camera_pos, sign, self.cute_girl.fire_level))

    def excute(self):
        while self._is_running:
            self.on_loop()
            self.on_event(pygame.event.get())
            self.on_render()


if __name__ == '__main__':
    pygame.init()
    playing = PlayingScene()
    playing.excute()
