import arcade
import random
import time


SCREEN_WIDTH, SCREEN_HEIGHT = arcade.get_display_size()
ms = 4
run_ms = 8


def load_texture(filename):
    return [arcade.load_texture(filename),
            arcade.load_texture(filename, flipped_horizontally=True)]


class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        super(PlayerCharacter, self).__init__()
        self.stay_textures = []
        self.walk_textures = []
        self.atack_textures = []
        self.die_textures = []
        self.center_y = SCREEN_HEIGHT/2
        self.atack_range = 25
        self.jump_texture = None
        self.atacked_jump_texture = None
        self.cur_texture = 0
        self.player_face_direction = 0
        self.atack = False
        self.damaged = False
        self.can_jump = False
        self.in_jump = False
        self.died = False
        self.hp = 5
        self.hitting = False
        self.atack_range = 25
        self.scale = 2
        self.load_all_textures()

    def update_animation(self, delta_time: float = 1/60):
        self.atack = False
        if self.died:
            if self.cur_texture < 7.5:
                frame = int(self.cur_texture / 1.5) % 5
                self.texture = self.die_textures[frame][self.player_face_direction]
            else:
                self.texture = self.die_textures[4][self.player_face_direction]

        else:
            if not self.damaged:
                if self.change_x < 0:
                    self.player_face_direction = 1
                elif self.change_x > 0:
                    self.player_face_direction = 0

            if self.in_jump:
                self.texture = self.jump_texture[self.player_face_direction]
            else:
                if self.damaged:
                    self.texture = self.atacked_jump_texture[self.player_face_direction]
                else:
                    if self.change_x == 0:
                        if self.hitting:
                            frame = int(self.cur_texture * 1.5) % 7
                            self.texture = self.atack_textures[frame][self.player_face_direction]
                            if int(self.cur_texture * 1.5) == 7:
                                self.hitting = False
                                self.atack = True
                        else:
                            frame = int(self.cur_texture) % 5
                            self.texture = self.stay_textures[frame][self.player_face_direction]
                    else:
                        frame = int(self.cur_texture) % 9
                        self.texture = self.walk_textures[frame][self.player_face_direction]
            if self.change_y == 0 and self.damaged:
                self.damaged = False
                self.change_x = 0
        self.cur_texture += 0.15

    def update(self):
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH
        if self.change_y == 0:
            self.can_jump = True
            self.in_jump = False

    def damage_player(self):
        self.in_jump = False
        self.damaged = True
        self.hitting = False
        self.hp -= 1
        if self.hp < 1:
            self.died = True
            self.change_x = 0
            self.cur_texture = 0
        else:
            self.change_y = 2
            if self.player_face_direction == 0:
                self.change_x = -ms
            else:
                self.change_x = ms

    def refresh(self):
        self.load_all_textures()
        self.atack = False
        self.damaged = False
        self.can_jump = False
        self.in_jump = False
        self.died = False
        self.center_y = SCREEN_HEIGHT/2
        self.scale = 2
        self.hp = 5
        self.hitting = False

    def load_all_textures(self):
        self.stay_textures.clear()
        self.walk_textures.clear()
        self.atack_textures.clear()
        self.die_textures.clear()
        for i in range(1, 6):
            texture = load_texture(f"stay/cavemen_stay_{i}.png")
            self.stay_textures.append(texture)

        for i in range(1, 10):
            texture = load_texture(f"walk/cavemen_walk_{i}.png")
            self.walk_textures.append(texture)

        for i in range(1, 8):
            texture = load_texture(f"atack/cavemen_atack_{i}.png")
            self.atack_textures.append(texture)

        for i in range(1, 6):
            texture = load_texture(f"die/cavemen_die_{i}.png")
            self.die_textures.append(texture)

        self.jump_texture = load_texture("jump/cavemen_jump_3.png")
        self.atacked_jump_texture = load_texture("atack/cavemen_atack_4.png")


class GameWindow(arcade.Window):
    def __init__(self, s_w, s_h):
        super(GameWindow, self).__init__(s_w, s_h, "Atack of titans", True)
        arcade.set_background_color(arcade.color.AIR_FORCE_BLUE)
        self.player_list = None
        self.player_1 = None
        self.player_2 = None
        self.physics_engine_1 = None
        self.physics_engine_2 = None
        self.walls = []
        self.bg_list = None
        self.bg = None
        self.trees = None
        self.tree = None
        self.platform_list = None
        self.platform = None
        self.count = 0
        self.cactus = None
        self.cactus_list = None
        self.start_message = True
        self.end_message = False
        self.time_before_start = 2.99
        self.end_time = 3
        self.game_ended = 0
        self.wins = None
        self.p1_point = 0
        self.p2_point = 0

    def setup(self):
        x = 0
        self.platform_list = arcade.SpriteList()
        while x < SCREEN_WIDTH:
            self.platform = arcade.Sprite("platforms/desert_platform.jpg")
            self.platform.left = x
            self.platform.bottom = 0
            self.platform_list.append(self.platform)
            x = self.platform.right
        x = 0
        self.bg_list = arcade.SpriteList()
        while x < SCREEN_WIDTH:
            self.bg = arcade.Sprite("bg.png")
            self.bg.scale = 5
            self.bg.left = x
            self.bg.bottom = self.platform.top
            self.bg_list.append(self.bg)
            x = self.bg.right
        self.player_1 = PlayerCharacter()
        self.player_1.player_face_direction = 1
        self.player_2 = PlayerCharacter()
        self.player_1.center_x = SCREEN_WIDTH
        self.player_2.center_x = 0
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_1)
        self.player_list.append(self.player_2)
        self.physics_engine_1 = arcade.PhysicsEnginePlatformer(self.player_1, self.platform_list, 0.4)
        self.physics_engine_2 = arcade.PhysicsEnginePlatformer(self.player_2, self.platform_list, 0.4)
        self.trees = arcade.SpriteList()
        self.cactus_list = arcade.SpriteList()
        self.create_trees()
        self.p1_point = 0
        self.p2_point = 0
        self.start_message = True
        self.end_message = False
        self.time_before_start = 2.99

    def load_level(self):
        self.player_1.center_x = SCREEN_WIDTH
        self.player_2.center_x = 0
        self.player_1.player_face_direction = 1
        self.player_2.player_face_direction = 0
        self.player_1.refresh()
        self.player_2.refresh()
        self.cactus_list = arcade.SpriteList()
        self.trees = arcade.SpriteList()
        self.create_trees()
        self.start_message = True
        self.end_message = False
        self.time_before_start = 2.99

    def on_draw(self):
        arcade.start_render()
        self.bg_list.draw()
        self.trees.draw()
        self.cactus_list.draw()
        self.platform_list.draw()
        self.player_list.draw()
        arcade.draw_text(str("P1"), self.player_1.center_x, self.player_1.top, arcade.color.BLUE, 20, bold=True)
        arcade.draw_text(str("P2"), self.player_2.center_x, self.player_2.top, arcade.color.RED, 20, bold=True)
        if self.start_message:
            arcade.draw_text(str(int(self.time_before_start) + 1), SCREEN_WIDTH/2 - 30, SCREEN_HEIGHT/2 - 100,
                             arcade.color.BLACK, 200)
        elif self.end_message:
            if self.wins == 0:
                text = "DRAW"
            else:
                text = f"WINS P{self.wins}"
            arcade.draw_text(text, SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.BLACK, 50)

        arcade.draw_text(str(self.p2_point), 100, SCREEN_HEIGHT * 0.9, arcade.color.BLACK_BEAN, 40)
        arcade.draw_text(str(self.p1_point), SCREEN_WIDTH - 200, SCREEN_HEIGHT * 0.9, arcade.color.BLACK, 40)

    def on_update(self, delta_time: float):
        self.physics_engine_1.update()
        self.physics_engine_2.update()
        self.player_list.update_animation()
        self.player_list.update()
        self.touch_cactus(self.player_1)
        self.touch_cactus(self.player_2)
        if self.player_1.atack:
            self.hitting(self.player_1, self.player_2)
        if self.player_2.atack:
            self.hitting(self.player_2, self.player_1)
        if self.start_message:
            self.time_before_start -= delta_time
            if self.time_before_start <= 0:
                self.start_message = False

        if self.end_message:
            if time.time() - self.game_ended >= self.end_time:
                self.load_level()
        elif self.player_1.died or self.player_2.died:
            self.end_message = True
            self.game_ended = time.time()
            if self.player_1.died and self.player_2.died:
                self.wins = 0
            elif self.player_1.died:
                self.wins = 2
                self.p2_point += 1
            else:
                self.wins = 1
                self.p1_point += 1

    def on_key_press(self, key: int, modifiers: int):
        if not self.player_1.died and not self.player_2.died and not self.start_message:
            if not self.player_1.hitting and not self.player_1.damaged:
                if key == arcade.key.LEFT:
                    self.player_1.change_x = -ms
                if key == arcade.key.RIGHT:
                    self.player_1.change_x = ms
                if key == arcade.key.M and self.player_1.can_jump:
                    self.player_1.hitting = True
                    self.player_1.change_x = 0
                    self.player_1.cur_texture = 0
                if key == arcade.key.UP and self.player_1.can_jump:
                    arcade.PhysicsEnginePlatformer.jump(self.physics_engine_1, 10)
                    self.player_1.can_jump = False
                    self.player_1.in_jump = True
                    self.player_1.cur_texture = 0

            if not self.player_2.hitting and not self.player_2.damaged and not self.player_2.died:
                if key == arcade.key.A:
                    self.player_2.change_x = -ms
                if key == arcade.key.D:
                    self.player_2.change_x = ms
                if key == arcade.key.SPACE and self.player_2.can_jump:
                    self.player_2.hitting = True
                    self.player_2.change_x = 0
                    self.player_2.cur_texture = 0
                if key == arcade.key.W and self.player_2.can_jump:
                    arcade.PhysicsEnginePlatformer.jump(self.physics_engine_2, 10)
                    self.player_2.can_jump = False
                    self.player_2.in_jump = True
                    self.player_2.cur_texture = 0

    def on_key_release(self, key: int, modifiers: int):
        if (key == arcade.key.RIGHT or key == arcade.key.LEFT) and not self.player_1.damaged:
            self.player_1.change_x = 0
        if (key == arcade.key.D or key == arcade.key.A) and not self.player_2.damaged:
            self.player_2.change_x = 0

    def create_trees(self):
        count = random.randint(4, 10)
        for _ in range(count):
            self.tree = arcade.Sprite(f"trees/palm{random.randint(1, 6)}.png")
            self.tree.center_x = random.randint(0, SCREEN_WIDTH)
            self.tree.bottom = self.platform.top - 2
            self.trees.append(self.tree)
        count = random.randint(10, 10)
        c_range = int(SCREEN_WIDTH/(3 * count))
        for i in range(count):
            self.cactus = arcade.Sprite(f"trees/cactus1.png")
            self.cactus.center_x = SCREEN_WIDTH/3 + i * c_range + random.randint(0, c_range)
            self.cactus.scale = 0.1 * random.randint(5, 10)
            self.cactus.bottom = self.platform.top - 2
            self.cactus_list.append(self.cactus)

    def touch_cactus(self, player):
        touched_cactus = arcade.check_for_collision_with_list(player, self.cactus_list)
        if touched_cactus.__len__() > 0 and not player.damaged:
            player.damage_player()

    def hitting(self, player, player2):
        for cactus in self.cactus_list:
            if player.player_face_direction == 0:
                if abs(cactus.center_x - player.right) <= player.atack_range:
                    self.cactus_list.remove(cactus)
            else:
                if abs(player.left - cactus.center_x) <= player.atack_range:
                    self.cactus_list.remove(cactus)

        if player.player_face_direction == 0 and not player2.in_jump:
            if player2.left - player.atack_range <= player.right <= player2.right + player.atack_range:
                player2.damage_player()
        else:
            if player2.left - player.atack_range <= player.left <= player2.right + player.atack_range:
                player2.damage_player()


window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()
arcade.set_window(window)
arcade.run()
