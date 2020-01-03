import common
import data
import map
import game
import particle

class Actor:
    int kind
    int aid
    int d, f
    float x, y, z # map cell coordinates
    int tracks, trees
    int step_count
    int turning
    int moving
    bool was_moving
    int on_tracks
    float speed
    int extra_speed
    bool broken
    int burning

    int draw_next_aid

global float actor_dx[] = {1,  1,  0, -1, -1, -1, 0, 1}
global float actor_dy[] = {0, -1, -1, -1,  0,  1, 1, 1}

global int actor_curve_slope = 4
# That way if the AI can solve a level, there likely is also different
# solutions available.
global int actor_curve_slope_ai = 2

def actor_new(int kind) -> Actor*:
    auto game = game_global()
    auto m = game.map
    if not m.actors:
        m.actors = land_array_new()
        land_array_add(m.actors, None)

    Actor* self
    land_alloc(self)
    self.aid = land_array_count(m.actors)
    self.kind = kind
    self.speed = 1
    if self.kind == DataDragon0: self.speed = 0.5
    if self.kind == DataDragon1: self.speed = 0.75
    if self.kind == DataEngine or self.kind == DataCar: self.speed = 0.25
    land_array_add(m.actors, self)
    return self

def actor_get(int aid) -> Actor*:
    auto game = game_global()
    auto m = game.map
    return land_array_get(m.actors, aid)

def actor_draw(Actor* self, float x, y):
    float s = 144 / 512.0
    int f = self.f / 8
    if f == 3: f = 1
    
    auto image = data_monster(self.kind - DataTroll, self.d * 3 + f)
    land_image_draw_scaled(image.image if not (common_outline) else image.outline,
        x, y - self.z, s, s)

def actor_move(Actor* self) -> bool:
    auto game = game_global()
    float s = self.speed / 24.0
    float ox = self.x
    float oy = self.y
    float nx = self.x + actor_dx[self.d] * s
    float ny = self.y + actor_dy[self.d] * s
    auto ct = map_get(game.map, ox, oy)
    auto nt = map_get(game.map, nx, ny)
    if abs(nt.height - ct.height) > 14:
        if self.kind == DataDragon0 or self.kind == DataDragon1 or self.kind == DataDragon2:
            pass
        else:
            return False
    map_unplace_actor(game.map, ox, oy)
    if map_place_actor(game.map, nx, ny, self.aid):
        self.x = nx
        self.y = ny
        return True
    map_place_actor(game.map, ox, oy, self.aid)
    return False

def actors_tick(Game *game):
    for Actor* a in LandArray* game.map.actors:
        if not a: continue
        if a.kind == DataTroll:
            troll_tick(a)
        elif a.kind == DataEngine or a.kind == DataCar:
            engine_tick(a)
        else:
            dragon_tick(a)

def troll_build_tracks(Actor* troll, int d) -> bool:
    auto game = game_global()
    auto tile = map_get(game.map, troll.x, troll.y)
    #print("%.1f %.1f %d", troll.x, troll.y, d)
    if tile.slope:
        if tile.slope % 4 == 1 or tile.slope % 4 == 3:
            if d == 2 or d == 6:
                tile.track = 10
                data_play(DataTrackSound)
                return True
        if tile.slope % 4 == 0 or tile.slope % 4 == 2:
            if d == 0 or d == 4:
                tile.track = 5
                data_play(DataTrackSound)
                return True
    else:
        if d == 0 or d == 2 or d == 4 or d == 6:
            if map_place_track_or_curve(game.map, troll.x, troll.y, d):
                data_play(DataTrackSound)
                if tile.track == 5 or tile.track == 10: # no curve
                    if not map_grade(game.map, troll.x, troll.y, d):
                        map_grade(game.map, troll.x, troll.y, (d + 4) % 8)
                return True
    return False

def troll_tick(Actor* troll):
    auto game = game_global()
    int kx = 0, ky = 0
    
    if land_key(LandKeyLeft) or land_key('a'): kx -= 1
    if land_key(LandKeyRight) or land_key('d'): kx += 1
    if land_key(LandKeyUp) or land_key('w'): ky -= 1
    if land_key(LandKeyDown) or land_key('s'): ky += 1
    if land_key_pressed('1') or land_key_pressed(' '):
        auto tile = map_get(game.map, troll.x, troll.y)
        if tile.track:
            tile.track = 0
            troll.tracks++
            _debris(troll, 20, 0, 0, 0, 1)
            data_play(DataRemoveTrackSound)
        else:
            if troll_build_tracks(troll, troll.d):
                _debris(troll, 10, .5, .3, 0, 1)
                _debris(troll, 10, .1, .1, 0, 1)
            else:
                int d = 0
                for d in range(0, 8, 2):
                    auto nt = map_get_neighbor(game.map, troll.x, troll.y, d)
                    if nt.track:
                        break
                if d != 8:
                    for int t in range(4):
                        if t == 2: d = (d + 2) % 8
                        else: d = (d + 4) % 8
                        if troll_build_tracks(troll, d):
                            _debris(troll, 20, .5, .3, 0, 1)
                            break
    if land_key_pressed('2'):
        int d = troll.d
        if d % 2 == 0:
            auto tile = map_get_neighbor(game.map, troll.x, troll.y, d)
            if tile.obj:
                if map_is_tree(tile.obj):
                    tile.obj = 0
                    troll.trees++
                    data_play(DataClearSound)
                    _debris(troll, 10, .2, .3, 0, 1)
                    _debris(troll, 10, .3, .4, .1, 1)
            elif not tile.actor:
                tile.obj = DataSpruce + land_rand(0, 1)
                troll.trees--
                data_play(DataPlantSound)
                _debris(troll, 10, .2, .3, 0, 1)
                _debris(troll, 10, .3, .4, .1, 1)
    if land_key_pressed('3'):
        auto tile = map_get(game.map, troll.x, troll.y)
        if tile.track:
            tile.track = 0
            troll.tracks++
        if map_grade(game.map, troll.x, troll.y, troll.d):
            _debris(troll, 10, .8, .8, 1, 1)
            _debris(troll, 10, .4, .3, .1, 1)
            if tile.slope:
                data_play(DataSnowDownSound)
            else:
                data_play(DataSnowUpSound)

    if kx or ky:
        if troll.f == 8:
            _gas(troll.x - actor_dx[troll.d] * 0.2, troll.y - actor_dy[troll.d] * 0.2, troll.z)
        if troll.f == 8 or troll.f == 24:
            data_play(DataStepSound1 + land_rand(0, 3))
        if troll.f % 8 == 0:
            float dx = actor_dx[troll.d]
            float dy = actor_dy[troll.d]
            float d = sqrt(dx * dx + dy * dy)
            float sx = -dy * 0.2 / d
            float sy = dx * 0.2 / d
            if (troll.f / 8) % 2 == 0:
                sx = -sx
                sy = -sy

            _imprint(troll.x + sx + dx * 0.1 / d, troll.y + sy + dy * 0.1 / d, troll.z)
            _imprint(troll.x + sx, troll.y + sy, troll.z)
        int a = ((int)((atan2(kx, ky) - pi * 0.25) / (pi * 0.25)) + 8) % 8
        troll.d = a
        troll.f += 1
        troll.f %= 32
        actor_move(troll)
    else:
        if troll.f < 24 and troll.f != 8:
            troll.f += 1
            troll.f %= 32
        else:
            troll.d = (troll.d / 2) * 2

    actor_climb(troll)

def _play_distance(int did, Actor* a):
    auto game = game_global()
    auto player = game.player
    float dx = a.x - player.x
    float dy = a.y - player.y
    float d = sqrt(dx * dx + dy * dy)
    float vol = 1
    if d > 3:
        vol -= (d - 3) / 15
        if vol < 0.25: vol = 0.25
    #print("vol %f", vol)
    data_play_vol(did, vol)

def dragon_tick(Actor* actor):
    auto game = game_global()
    actor.f += 1
    actor.f %= 32
    actor_climb(actor)
    if actor.burning:
        actor.burning--
        _fire(actor.x + actor_dx[actor.d] * 0.3, actor.y + actor_dy[actor.d] * 0.3, actor.z, actor.d)
        if actor.burning == 0:
            auto tile = map_get_neighbor(game.map, actor.x, actor.y, actor.d)
            tile.obj = 0
        return
    if actor.turning:
        actor.step_count -= 1
    else:
        int amount = 0
        if actor_move(actor):
            actor.step_count -= 1
            auto tile = map_get(game.map, actor.x, actor.y)
            if tile.track:
                actor.burning = 180
                _play_distance(DataFireSound, actor)
                amount = 15
                tile.track = 0
                actor.step_count = 0
        else:
            actor.step_count = 0
            auto tile = map_get_neighbor(game.map, actor.x, actor.y, actor.d)
            amount = 5
            if tile.obj:
                if map_is_tree(tile.obj):
                    actor.burning = 180
                    amount = 15
                    _play_distance(DataFireSound, actor)
            elif tile.actor:
                auto who = actor_get(tile.actor)
                if who.kind == DataEngine or who.kind == DataCar:
                    amount = 15
                    _play_distance(DataFireSound, actor)
                    who.burning = 180
                    actor.burning = 180
        for int i in range(amount):
            _fire(actor.x + actor_dx[actor.d] * 0.3, actor.y + actor_dy[actor.d] * 0.3, actor.z, actor.d)

    if actor.step_count <= 0:
        if actor.turning:
            actor.step_count = 24
            if actor.turning > 0:
                actor.turning -= 1
                actor.d += 1
            else:
                actor.turning += 1
                actor.d -= 1
            if actor.d < 0: actor.d += 8
            if actor.d > 7: actor.d -= 8
            if actor.turning == 0:
                actor.step_count = 24 * land_rand(12, 16)
        else:
            actor.step_count = 24
            if actor.kind == DataDragon2: actor.turning = 2
            if actor.kind == DataDragon1: actor.turning = -2
            if actor.kind == DataDragon0: actor.turning = 4

def _smoke(float x, y, z):
    auto game = game_global()
    float vx, vy
    land_grid_get_cell_position(game.map.grid, game.map.view, x, y, &vx, &vy)
    auto p = particle_add(vx, vy, z + 32, 0, 0, 0, 1, land_rnd(3, 9))
    p.dx = land_rnd(-.5, .5)
    p.dy = land_rnd(-.5, -.5)
    p.dz = land_rnd(.2, .6)
    p.fade = 0.982
    p.grow = 1.01
    p.t = 120

def _gas(float x, y, z):
    auto game = game_global()
    float vx, vy
    land_grid_get_cell_position(game.map.grid, game.map.view, x, y, &vx, &vy)
    auto p = particle_add(vx, vy, z + 8, 0.2, 0.3, 0, 1, 4)
    p.dz = .5
    p.fade = 0.99
    p.grow = 1.02
    p.t = 60

def _snow(float x, y, z, r, g, b, a):
    auto game = game_global()
    float vx, vy
    land_grid_get_cell_position(game.map.grid, game.map.view, x, y, &vx, &vy)
    auto p = particle_add(vx, vy, z, r, g, b, a, 2)
    p.dz = .4
    p.dx = land_rnd(-.5, .5)
    p.dy = land_rnd(-.5, .5)
    p.fade = 0.98
    p.grow = 1.01
    p.gravity = -.01
    p.t = 60

def _fire(float x, y, z, int d):
    auto game = game_global()
    float dx = actor_dx[d] - actor_dy[d]
    float dy = actor_dx[d] + actor_dy[d]
    float vx, vy
    land_grid_get_cell_position(game.map.grid, game.map.view, x, y, &vx, &vy)
    auto p = particle_add(vx, vy, z + 8, 1, land_rnd(0, 1), 0, 1, land_rand(1, 4))
    p.dx = land_rnd(0.2, 0.6) * dx
    p.dy = land_rnd(0.2, 0.6) * dy
    p.dz = -0.01
    p.fade = 0.99
    p.grow = 1.01
    p.t = 90

def _imprint(float x, y, z):
    auto game = game_global()
    float vx, vy
    land_grid_get_cell_position(game.map.grid, game.map.view, x, y, &vx, &vy)
    auto p = particle_add(vx, vy, z, 0, 0, 0, .5, 4)
    p.dz = 0
    p.dx = 0
    p.dy = 0
    p.fade = 0.98
    p.grow = 1
    p.gravity = 0
    p.t = 300

def _debris(Actor* self, int n, float r, g, b, a):
    for int i in range(n):
        _snow(self.x, self.y, self.z, r, g, b, a)

def engine_tick(Actor* self):
    auto game = game_global()

    if self.broken:
        game.state = Over
        return

    if self.burning:
        self.burning--
        _smoke(self.x, self.y, self.z)
        _debris(self, 1, 1, land_rnd(0, 1), 0, 1)
        if self.burning == 0:
            self.broken = True
        return

    if self.kind == DataEngine:
        _smoke(self.x + actor_dx[self.d] * 0.5, self.y + actor_dy[self.d] * 0.5, self.z)
        int cx = self.x
        int cy = self.y
        if cx == game.map.end_x and cy == game.map.end_y:
            game.state = Won
    
    if not self.on_tracks:
        auto tile = map_get(game.map, self.x, self.y)
        auto ntile = map_get_neighbor(game.map, self.x, self.y, self.d)
        bool steep = abs(tile.height - ntile.height) > 14
        int ld = (self.d + 2) % 8
        int bd = (self.d + 4) % 8
        int rd = (self.d + 6) % 8

        if ntile.actor:
            self.step_count = 12
        elif tile.track & (1 << (self.d / 2)):
            if ntile.base == 0 or steep:
                self.broken = True
            elif ntile.track & (1 << (bd / 2)):
                self.step_count = 24 * 4
                self.moving = 1
            else:
                self.step_count = 24 * 4
        elif tile.track & (1 << (ld / 2)):
            auto ctile = map_get_neighbor(game.map, self.x, self.y, (self.d + 2) % 8)
            if ctile.base == 0 or ctile.height - tile.height > actor_curve_slope:
                self.broken = True
            else:
                self.turning = 1
                self.step_count = 24
        elif tile.track & (1 << (rd / 2)):
            auto ctile = map_get_neighbor(game.map, self.x, self.y, (self.d + 6) % 8)
            if ctile.base == 0 or ctile.height - tile.height > actor_curve_slope:
                self.broken = True
            else:
                self.turning = -1
                self.step_count = 24
        else:
            self.broken = True
        self.on_tracks = True
        
    actor_climb(self)

    bool was_moving = self.moving != 0 or self.turning != 0
    
    if self.moving:
        int moved = 0
        for int i in range(1 + self.extra_speed):
            if actor_move(self):
                self.step_count -= 1
                moved++
                if self.step_count == 0:
                    if self.extra_speed < 4:
                        self.extra_speed += 1
                    break
        if moved:
            self.f += 1
            self.f %= 32
    else:
        self.step_count -= 1
    if self.step_count == 12:
        if self.turning:
            self.d = (self.d + 8 + self.turning) % 8
    if self.step_count == 0:
        self.on_tracks = 0
        self.moving = 0
        self.d = (self.d + 8 + self.turning) % 8
        self.turning = 0

    if was_moving:
        if not self.was_moving:
            self.was_moving = True
            if self.kind == DataEngine:
                data_play(DataWhistleSound)
                data_loop(DataEngineSound)
            self.extra_speed = 0
    else:
        if self.was_moving:
            self.was_moving = False
            if self.kind == DataEngine:
                data_stop(DataEngineSound)

def actor_climb(Actor* actor):
    auto game = game_global()
    auto tile = map_get(game.map, actor.x, actor.y)
    if actor.z < tile.height:
        actor.z += 1
    if actor.z > tile.height:
        actor.z -= 1
