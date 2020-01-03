import common
import data
import actor
import game

macro W 64
macro H 64

class Tile:
    int height
    int base_height
    int base
    int slope
    int obj
    int actor
    int actor_draw

    bool visited[4]

    int track # 0 = none, 5 = /, 10 = \, 3/6/9/12 = curves

class Map:
    LandMap* tilemap
    LandView* view
    LandGrid* grid
    Tile tiles[W * H]
    int seed
    int score

    int start_x, start_y
    int end_x, end_y

    LandArray *actors

int _pass

def map_new(Game* game, int seed) -> Map*:
    Map* self; land_alloc(self)
    game.map = self
    self.seed = seed
    self.tilemap = land_map_new()
    self.view = land_view_new(0, 128, 1280, 720 + 128) # add at the bottom for height > 0
    land_view_scroll_center(self.view, 0, 24 * 32)
    auto grid = land_isometric_custom_grid(24, 12, 24, 12, W, H,
        False,_draw_cell)
    self.grid = grid
    land_map_add_layer(self.tilemap, land_layer_new_with_grid(grid))

    if common_mode != 6:
        create_heightmap(seed)

    land_seed(seed)

    _flatten(self, 14, 39, 5)
    _flatten(self, 39, 14, 5)
    
    assign_bases()
    if common_mode != 2:
        assign_slopes()
        if common_mode != 3:
            assign_back_slopes()

    map_forests(self)

    place_signs(self)

    place_actors(game, self)

    return self

def map_destroy(Map* self):
    land_map_destroy(self.tilemap)
    land_view_destroy(self.view)
    land_free(self)

def _erase(Map* self, int x, y):
    auto tile = map_get(self, x, y)
    tile.obj = DataStop
    tile.base = 0
    tile.slope = 0

def place_actors(Game* game, Map* self):
    Actor* dra = None
    int dragon_count = game.level * 2
    for int i in range(dragon_count):
        for int j in range(5):
            if dra == None:
                int a = 2
                if game.level == 2: a = 1
                if game.level < 2: a = 0
                dra = actor_new(DataDragon0 + land_rand(0, a))
            dra.x = 1.5 + i + j
            dra.y = 27.5 - i
            dra.d = land_rand(0, 3) * 2
            if map_place_actor_on_map(self, dra.x, dra.y, dra.aid):
                dra = None
                break

    _erase(self, 0, 27)
    _erase(self, 27, 0)
    _erase(self, 36, 63)
    _erase(self, 63, 36)
    for int i in range(27):
        _erase(self, i, 26 - i) # top
        _erase(self, 37 + i, 63 - i) # bottom

    for int i in range(36):
        _erase(self, i, 28 + i) # left
        _erase(self, 28 + i, i) # right

    auto troll = actor_new(DataTroll)
    game.player = troll
    troll.x = self.start_x + 1.5
    troll.y = self.start_y + 0.5
    map_place_actor_on_map(self, troll.x, troll.y, troll.aid)

def place_signs(Map* self):
    self.start_x = 14
    self.start_y = 39
    self.end_x = 39
    self.end_y = 14
    put_sign(self, self.start_x, self.start_y)
    put_sign(self, self.end_x, self.end_y)

    auto santa = actor_new(DataEngine)
    santa.x = 14.5
    santa.y = 38.5
    santa.d = 2
    map_place_actor_on_map(self, santa.x, santa.y, santa.aid)

    for int i in range(3):
        auto car = actor_new(DataCar)
        car.x = 14.5
        car.y = 39.5 + (i if i < 2 else 1)
        car.d = 2
        car.f = i * 8
        map_place_actor_on_map(self, car.x, car.y, car.aid)

def put_sign(Map *self, int x, y):
    int r = 1
    for int j in range(-r, r + 1):
        for int i in range(-r, r + 1):
            auto tile = map_get(self, x + i, y + j)
            tile.obj = 0
            if i == -1 and j == 0: tile.obj = DataSign
            if i == 0 and j >= -1 and j <= 1: tile.track = 10

def _flatten(Map* self, int x, y, r):
    int h = 0
    int n = 0
    for int j in range(-r, r + 1):
        for int i in range(-r, r + 1):
            auto tile = map_get(self, x + i, y + j)
            h += tile.height
            n += 1
    h /= n
    for int j in range(-r, r + 1):
        for int i in range(-r, r + 1):
            auto tile = map_get(self, x + i, y + j)
            int d = max(abs(j) - 2, abs(i) - 2)
            d = max(d, 0)
            tile.height = h * (r - d) / r + tile.height * d / r

def map_forests(Map* self):
    int fc = 20
    int tc = 20
    for int fi in range(fc):
        int x = land_rand(0, W)
        int y = land_rand(0, H)
        for int ti in range(tc):
            auto tile = get(x, y)
            tile.obj = DataSpruce + land_rand(0, 1)
            x += land_rand(-3, 3)
            y += land_rand(-3, 3)

def create_heightmap(int seed):
    auto game = game_global()
    auto noise = land_noise_new(LandNoisePerlin, seed)
    land_noise_set_wrap(noise, False)
    land_noise_set_size(noise, W, H)
    land_noise_set_minmax(noise, 0, 255)
    land_noise_z_transform(noise, 200, 32)
    land_noise_set_levels(noise, 4)
    land_noise_prepare(noise)
    for int y in range(H):
        for int x in range(W):
            int h = land_noise_at(noise, x, y)
            #int cx = x - W / 2
            #int cy = y - H / 2
            #cx = W / 2 - abs(cx)
            #cy = H / 2 - abs(cy)
            #int h = (cx + cy) * 6
            game.map.tiles[x + y * W].height = h

    if common_mode == 1:
        return

    # int flat_height = 4
    # for int y in range(H):
        # for int x in range(W):
            # auto tile = get(x, y)
            # for int d2 in range(4):
                # int d = d2 / 2
                # auto tile_d = get_neighbor(x, y, d)
                # int h = tile.height - tile_d.height
                # if h > 0 and h <= flat_height:
                    # tile.height = tile_d.height

def assign_bases:
    for int y in range(H):
        for int x in range(W):
            auto tile = get(x, y)
            
            auto down = get(x, y + 1)
            auto right = get(x + 1, y)
            int low = down.height if down.height < right.height else right.height
            int d = tile.height - low
            if d <= 0:
                tile.base_height = tile.height
                tile.base = DataSnow
            elif d < 14:
                tile.base_height = tile.height - d
                tile.base = DataSnow125 + d / 2
            else:
                tile.base_height = tile.height - 28
                tile.base = DataSnow2000

def assign_slopes:
    for int y in range(H):
        for int x in range(W):
            auto tile = get(x, y)
            auto left = get(x - 1, y)
            auto up = get(x, y - 1)
            int dx = left.height - tile.height
            int dy = up.height - tile.height
            bool xok = dx > 0 and dx <= 14
            bool yok = dy > 0 and dy <= 14
            if xok and (dx > dy or not yok):
                tile.slope = (DataSnow125 + dx / 2) * 4 + 2
            elif yok:
                tile.slope = (DataSnow125 + dy / 2) * 4 + 1

def assign_back_slopes:
    for int y in range(H):
        for int x in range(W):
            auto tile = get(x, y)
            if tile.slope: continue
            auto right = get(x + 1, y)
            auto down = get(x, y + 1)
            int dx = right.height - tile.height
            int dy = down.height - tile.height
            bool xok = dx > 0 and dx <= 14
            bool yok = dy > 0 and dy <= 14
            if xok and (dx > dy or not yok):
                tile.slope = (DataSnow125 + dx / 2) * 4 + 0
            elif yok:
                tile.slope = (DataSnow125 + dy / 2) * 4 + 3

def map_get(Map* self, int x, y) -> Tile*:
    if x < 0: return get(0, y)
    if y < 0: return get(x, 0)
    if x >= W: return get(W - 1, y)
    if y >= H: return get(x, H - 1)
    
    return self.tiles + x + y * W

def map_get_neighbor(Map* self, int x, y, d) -> Tile*:
    return map_get(self, x + actor_dx[d], y + actor_dy[d])

def get(int x, y) -> Tile*:
    auto game = game_global()
    return map_get(game.map, x, y)

def get_neighbor(int x, y, d) -> Tile*:
    auto game = game_global()
    return map_get_neighbor(game.map, x, y, d)

def _draw(Tile* tile, int aid):
    if tile.actor_draw:
        auto actor = actor_get(tile.actor_draw)
        while actor.draw_next_aid:
            actor = actor_get(actor.draw_next_aid)
        actor.draw_next_aid = aid
    else:
        tile.actor_draw = aid

def get_tint(Tile* t, float *r, *g, *b):
    if t.height < 32:
        *r = 1 - (32 - t.height) / 32.0 / 20
        *g = 1
        *b = 1
    elif t.height < 32 * 2:
        *r = 1
        *g = 1
        *b = 1
    elif t.height < 32 * 3:
        *r = 1 - (t.height - 32 * 2) / 32.0 / 20
        *g = 1 - (t.height - 32 * 2) / 32.0 / 20
        *b = 1
    elif t.height < 32 * 4:
        *r = 1 + (t.height - 32 * 4) / 32.0 / 20
        *g = 1 + (t.height - 32 * 4) / 32.0 / 20
        *b = 1
    elif t.height < 32 * 5:
        *r = 1 - (t.height - 32 * 4) / 32.0 / 10
        *g = 1 - (t.height - 32 * 4) / 32.0 / 10
        *b = 1 - (t.height - 32 * 4) / 32.0 / 10
    else:
        *r = *g = *b = 1

def _draw_cell(LandGrid *grid, LandView *view, int cell_x, cell_y, float x, y):
    float s = 144 / 512.0
    auto tile = get(cell_x, cell_y)

    if _pass == 0:
        tile.actor_draw = 0
        return

    if _pass == 1:
        if not tile.actor: return
        auto tile0 = get_neighbor(cell_x, cell_y, 0)
        bool ok0 = abs(tile0.height - tile.height) <= 14
        if ok0:
            _draw(tile0, tile.actor)
        else:
            auto tile6 = get_neighbor(cell_x, cell_y, 6)
            bool ok6 = abs(tile6.height - tile.height) <= 14
            if ok6:
                _draw(tile6, tile.actor)
            else:
                _draw(tile, tile.actor)
        
        return

    if common_mode != 4 and tile.base:
        auto image = data_image(tile.base)
        float r, g, b
        get_tint(tile, &r, &g, &b)
        land_image_draw_scaled_tinted(image.image if not (common_outline) else image.outline,
            x, y - tile.base_height + 12, s, s, r, g, b, 1)
        if not tile.slope and tile.track
            image = data_track(tile.track)
            land_image_draw_scaled_tinted(image.image if not (common_outline) else image.outline,
                x, y - tile.height + 12, s, s, r, g, b, 1)

    if tile.slope:
        auto image = data_slope(tile.slope)
        if tile.track:
            image = data_slope_tracks(tile.slope)
        float r, g, b
        get_tint(tile, &r, &g, &b)
        land_image_draw_scaled_tinted(image.image if not (common_outline) else image.outline,
            x, y - tile.height + 12, s, s,
                r, g, b, 1)

    if tile.obj:
        auto image = data_image(tile.obj)
        land_image_draw_scaled(image.image if not (common_outline) else image.outline,
            x, y - tile.height + 12, s, s)

    int aid = tile.actor_draw
    while aid:
        auto actor = actor_get(aid)
        float vx, vy
        land_grid_get_cell_position(grid, view, actor.x, actor.y, &vx, &vy)
        float r = 12
        land_premul(0, 0, 0, .5)
        land_filled_circle(vx - r, vy - tile.height - r / 2, vx + r, vy - tile.height + r / 2)
        actor_draw(actor, vx, vy)
        aid = actor.draw_next_aid

    if common_grid:
        land_grid_isometric_placeholder(grid, view, cell_x, cell_y, x, y - tile.height)

def map_draw(Map* self):
    for Actor* a in LandArray* self.actors:
        if not a: continue
        a.draw_next_aid = 0

    _pass = 0 # clear actor_draw
    land_map_draw(self.tilemap, self.view)
    _pass = 1 # calculate actor_draw
    land_map_draw(self.tilemap, self.view)
    _pass = 2 # draw
    land_map_draw(self.tilemap, self.view)

def map_place_actor(Map* self, float x, y, int aid) -> bool:
    auto tile = get(x, y)
    if tile.actor != 0: return False
    if tile.obj != 0: return False
    tile.actor = aid
    return True

def map_place_actor_on_map(Map* self, float x, y, int aid) -> bool:
    if map_place_actor(self, x, y, aid):
        auto actor = actor_get(aid)
        auto tile = get(x, y)
        actor.z = tile.height
        return True
    return False

def map_unplace_actor(Map* self, float x, y):
    auto tile = get(x, y)
    tile.actor = 0

def map_place_track_or_curve(Map* self, int x, y, int d) -> bool:
    auto tile = get(x, y)
    auto tto = map_get_neighbor(self, x, y, d)
    bool curve_ok = tto.height - tile.height < 3
    if d == 0 or d == 4:
        auto tl = get(x, y + 1)
        auto tr = get(x, y - 1)
        if tl.track & 2 and tr.track & 8:
            tile.track = 5
        elif (tl.track & 2) and tl.height - tile.height <= actor_curve_slope and curve_ok:
            tile.track = 9 if d == 0 else 12
        elif (tr.track & 8) and tr.height - tile.height <= actor_curve_slope and curve_ok:
            tile.track = 3 if d == 0 else 6
        else:
            tile.track = 5
        return True
    elif d == 2 or d == 6:
        auto tl = get(x - 1, y)
        auto tr = get(x + 1, y)
        if tl.track & 1 and tr.track & 4:
            tile.track = 10
        elif (tl.track & 1) and tl.height - tile.height <= actor_curve_slope and curve_ok:
            tile.track = 6 if d == 2 else 12
        elif (tr.track & 4) and tr.height - tile.height <= actor_curve_slope and curve_ok:
            tile.track = 3 if d == 2 else 9
        else:
            tile.track = 10
        return True
    return False

def map_grade(Map* self, int x, y, d) -> bool:
    auto tile = get(x, y)
    if tile.slope:
        tile.slope = 0
        return True
    else:
        if d % 2 == 0:
            auto look = get(x + actor_dx[d], y + actor_dy[d])
            int diff = look.height - tile.height
            bool ok = diff > 0 and diff <= 14
            if ok:
                tile.slope = (DataSnow125 + diff / 2) * 4 + d / 2
                return True
    return False

def map_is_tree(int ob) -> bool:
    return ob == DataSpruce or ob == DataPine

class Node:
    int x, y
    Node* prev
    Node* next
    int d
    int steps

LandQueue *_nodes
LandArray *_allocated

def _node_add(int x, y, Node* prev, int d, steps):
    auto tile = get(x, y)
    if tile.visited[d / 2]: return
    Node *node; land_alloc(node)
    node.x = x
    node.y = y
    node.prev = prev
    node.d = d
    node.steps = steps
    tile.visited[d / 2] = True
    land_queue_add(_nodes, node)
    land_array_add(_allocated, node)

def _node_get -> Node*:
    return land_queue_pop(_nodes)

def _node_add_neighbors(Node* node):
    for int i in range(4):
        int d = i * 2
        int pd = (node.d + 4) % 8
        if d == pd: continue # can't make a u-turn
        int dx = actor_dx[d]
        int dy = actor_dy[d]
        auto tile = get(node.x, node.y)
        auto ntile = get(node.x + dx, node.y + dy)
        if not ntile.base: continue
        if ntile.obj and not map_is_tree(ntile.obj): continue
        if abs(ntile.height - tile.height) > 14: continue
        if d == node.d:
            pass
        else:
            auto ptile = get(node.x + actor_dx[pd], node.y + actor_dy[pd])
            if abs(ptile.height - tile.height) > actor_curve_slope_ai: continue # incoming can't be too high for curve
            if abs(ntile.height - tile.height) > actor_curve_slope_ai: continue # outgoing can't be too high for curve
        _node_add(node.x + dx, node.y + dy, node, d, node.steps + 1)

def _cmp(void *data1, void *data2) -> int:
    Node* node1 = data1
    Node* node2 = data2
    if node1.steps < node2.steps: return -1
    if node1.steps > node2.steps: return 1
    return 0
    
def map_solve(Map* self):
    self.score = 0
    _nodes = land_queue_new(_cmp)
    _allocated = land_array_new()
    Node* winner = None
    _node_add(self.start_x, self.start_y - 2, None, 2, 0)
    while True:
        auto node = _node_get()
        if not node: break
        if node.x == self.end_x and node.y == self.end_y:
            winner = node
            break
        _node_add_neighbors(node)

    Node* first = winner
    while first:
        Node* prev = first.prev
        if not prev: break
        prev.next = first
        first = prev

    while first and first.next:
        Node* next = first.next
        auto tile = get(first.x, first.y)
        auto ntile = map_get_neighbor(self, first.x, first.y, next.d)
        if tile.obj:
            tile.obj = 0
        if tile.slope:
            tile.slope = 0

        if first.d == next.d: # not a curve
            if not map_grade(self, first.x, first.y, next.d):
                map_grade(self, first.x, first.y, (next.d + 4) % 8)
            self.score += 1 + abs(ntile.height - tile.height)
        else:
            self.score += 3
        map_place_track_or_curve(self, first.x, first.y, next.d)
        first = next

    land_queue_destroy(_nodes)
    land_array_destroy_with_free(_allocated)

