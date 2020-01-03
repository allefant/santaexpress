import main
import map
import particle
import title

bool _debug = True

enum GameState:
    Title
    Ready
    Playing
    Over
    Won
    Complete

class Game:
    Map* map
    int state
    int last_state
    int state_t
    int level
    int t
    str seed
    LandArray* maps
    Actor* player

Game* _game

"""

the 3d model for a tile is a square with a side of 2.0 Blender units
we rotate the camera 45° so the width is 2.0 * sqrt(2)
in Blender we render ortographic and set the entire picture width to 3 * sqrt(2) (with ortho_scale)
the picture is 256 pixel, the tile spans 256 * 2 * sqrt(2) / (3 * sqrt(2) = 256 * 2 / 3 = 170.67 pixel
a tile in-game is 48 pixel, so we need scaling of 48 / 170.67 or 144 / 512

we also offset the Blender camera by sqrt(2)*3/4 unit in y direction, which is 1/4th of the picture


         
       _-''-_      _-''-_
    _-'      '-__-'      '-_
    '-_      _-''-_      _-'
       '-__-'      '-__-'
       _-''-_      _-''-_
    _-'      '-__-'      '-_
    '-_      _-''-_      _-'
       '-__-'      '-__-'


x/y
           
            -1/-1
     -1/0  _-''-_   0/-1   
        _-'      '-_
  -1/+1  '-_  0/0 _-'  +1/-1
           '-__-'   
     0/+1          +1/0
            +1/+1
    
angle
             3
         4 _-''-_ 2
     5  _-'      '-_  1
        '-_      _-'
         6 '-__-' 0
             7
    
bits
    
       4   _-''-_   2   
        _-'      '-_
        '-_      _-'
       8   '-__-'   1

slope
    
       2   _-''-_   1
        _-'      '-_
        '-_      _-'
       3   '-__-'   0

x+y
    
           _-'0'-_
        _- 1  1  1-_
        2   2   2   2
        '- 3  3   3-'
           '-_4_-'    


x-y

           -1'0'1_   
        -2'-1 0 1 2-_
        -2_-1 0 1 2-'
           -1_0_1'   

"""

def game_global -> Game*:
    return _game

def _cmp(void const *a, void const *b) -> int:
    Map* const* pma = a
    Map* const* pmb = b
    Map* ma = *pma
    Map* mb = *pmb
    if ma.score < mb.score: return -1
    if ma.score > mb.score: return 1
    return 0

def game_create_levels():
    if _game.maps:
        for Map* m in LandArray* _game.maps:
            map_destroy(m)
        land_array_destroy(_game.maps)

    _game.maps = land_array_new()
    auto sortmaps = land_array_new()

    int seed = 0
    int sn = strlen(_game.seed)
    for int i in range(sn):
        int d = 0
        int c = _game.seed[i]
        if c >= 'a' and c <= 'z':
            d = c - 'a'
        if c >= '0' and c <= '1':
            d = 26 + c - '0'
            
        seed *= 36
        seed += d

    int n = 100
    for int i in range(n):
        _game.map = map_new(_game, seed * 100 + i)
        map_solve(_game.map)
        #print("%d %d", i, _game.map.score)
        if _game.map.score == 0:
            map_destroy(_game.map)
            n++
            continue
        land_array_add(sortmaps, _game.map)
        _game.map = None

    land_array_sort(sortmaps, _cmp)
    for int i in range(10):
        Map* m = land_array_get(sortmaps, i * 99 / 9)
        land_array_add(_game.maps, m)
        #print("level %d: %d", 1 + i, m.score)
    land_array_destroy(sortmaps)

def game_init:
    data_load()
    particles_init()
    land_alloc(_game)

def game_create(str code):
    _game.seed = code
    _game.level = 0
    game_create_levels()
    game_next_level()

def game_next_level:
    Map* m = land_array_get(_game.maps, _game.level)
    _game.map =  map_new(_game, m.seed)
    _game.t = 0
    _game.state = Ready

def game_state_tick:
    if _game.state != _game.last_state:
        _game.last_state = _game.state
        _game.state_t = _game.t
        data_stop(DataEngineSound)
    int t = _game.t - _game.state_t

    if _game.state == Ready:
        if t >= 120:
            _game.state = Playing
            common_outline = 0
        elif t >= 60:
            common_outline = (t / 2) % 2
        else:
            common_outline = 1
    elif _game.state == Over:
        if t >= 120:
            game_next_level()
    elif _game.state == Won:
        if t >= 120:
            if _game.level < 9:
                _game.level++
                game_next_level()
            else:
                _game.state = Complete
    elif _game.state == Playing:
        actors_tick(_game)
    _game.t++

def game_tick:
    if land_closebutton(): land_quit()
    if land_key_pressed(LandKeyEscape):
        if _game.state == Title:
            land_quit()
        else:
            _game.state = Title

    if _game.state == Title:
        title_tick()
        return

    game_state_tick()

    if land_key_pressed('r'):
        _game.state = Over

    if _debug:
        if land_key_pressed('t'):
            int seed = _game.map.seed
            map_destroy(_game.map)
            _game.map = map_new(_game, seed)

        if land_key_pressed('n'):
            _game.state = Won
        if land_key_pressed('g'):
            map_solve(_game.map)
        if land_key_pressed('u'):
            for int t in range(180):
                game_state_tick()
        
        if land_key_pressed(LandKeyFunction + 1): common_mode = 0
        if land_key_pressed(LandKeyFunction + 2): common_mode = 1
        if land_key_pressed(LandKeyFunction + 3): common_mode = 2
        if land_key_pressed(LandKeyFunction + 4): common_mode = 3
        if land_key_pressed(LandKeyFunction + 5): common_mode = 4
        if land_key_pressed(LandKeyFunction + 6): common_mode = 5
        if land_key_pressed(LandKeyFunction + 7): common_mode = 6
        if land_key_pressed(LandKeyFunction + 9): common_grid ^= 1
        if land_key_pressed(LandKeyFunction + 10): common_outline ^= 1

    if common_mode == 5:
        int kx = 0, ky = 0
        if land_key(LandKeyLeft): kx -= 1
        if land_key(LandKeyRight): kx += 1
        if land_key(LandKeyUp): ky -= 1
        if land_key(LandKeyDown): ky += 1
        if land_key_pressed('c'): land_view_scroll_center(_game.map.view, 0, 24 * 32)
        land_view_scroll(_game.map.view, 6 * kx, 3 * ky)

    particles_tick()

def game_draw:
    land_scale_to_fit(1280, 720, 0)
    data_font_scale(True)
    land_unclip()
    land_clear(0.5, 0.5, 0.5, 1)

    if _game.state == Title:
        title_draw()
        return
    
    if common_mode != 5:
        LandFloat cx1 = 0, cy1 = 0, cz1 = 0
        LandFloat cx2 = 1280, cy2 = 720, cz2 = 0
        land_transform(&cx1, &cy1, &cz1)
        land_transform(&cx2, &cy2, &cz2)
        land_clip(cx1, cy1, cx2, cy2)
    else:
        land_unclip()
    map_draw(_game.map)
    particles_draw()

    land_font_set(small_font)
    land_text_pos(0, 0)
    land_color_set(land_color_name("black"))
    land_write(" Level %d/%d ", 1 + _game.level, 10)
    land_color_set(land_color_name("saddlebrown/2"))
    land_write("1: Build ")
    land_color_set(land_color_name("chartreuse"))
    land_write("2: Plant ")
    land_color_set(land_color_name("wheat"))
    land_write("3: Grade ")
    land_color_set(land_color_name("red"))
    land_write("R: Restart level ")
    land_color_set(land_color_name("black"))
    land_write("F: Fullscreen ")
    land_color_set(land_color_name("blue"))
    land_write("M: Music ")

    land_text_pos(1280, 0)
    land_color_set(land_color_name("black"))
    land_write_right("%d FPS ", land_get_current_fps())

    if _game.state == Ready:
        land_color_set(land_color_name("black"))
        land_font_set(big_font)
        land_text_pos(640, 180)
        land_print_center("Get Ready!")
        land_font_set(medium_font)
        land_print_center("Level %d/10", 1 + _game.level)

    if _game.state == Won:
        land_color_set(land_color_name("forestgreen"))
        land_font_set(big_font)
        land_text_pos(640, 180)
        land_print_center("Level Complete!")

    if _game.state == Over:
        land_color_set(land_color_name("red"))
        land_font_set(big_font)
        land_text_pos(640, 180)
        land_print_center("Failed!")

    if _game.state == Complete:
        land_color_set(land_color_name("skyblue"))
        land_font_set(big_font)
        land_text_pos(640, 180)
        land_print_center("Congratulations!")
        land_font_set(medium_font)
        land_print_center("You have completed the game!")

def game_done:
    pass
