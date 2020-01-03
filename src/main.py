"""
The Krampus moves around the map (with cursor keys). While standing on
a position and facing a direction, pressing number keys is different
tasks:
1 connect rail 
2 start bridge
3 grade
"""
import common
static import game

int _vol = 3

def init:
    land_find_data_prefix("data/")
    game_init()

def tick:
    if land_was_resized():
        double scale = land_scale_to_fit(1280, 720, 256)
        data_reload_fonts(scale)


    if land_key_pressed('f'):
        land_display_toggle_fullscreen()
    
    if land_key_pressed('m'):
        _vol++
        _vol %= 4
        if _vol == 0:
            land_stream_set_playing(land_stream_default(), False)
        else:
            land_stream_set_playing(land_stream_default(), True)
            land_stream_volume(land_stream_default(), _vol / 3.0)

    
    game_tick()

def draw:
    game_draw()

def done:
    game_done()

def realmain():
    land_init()
    land_set_display_parameters(1280, 720, LAND_WINDOWED | LAND_OPENGL |
        LAND_RESIZE)
    land_callbacks(init, tick, draw, done)
    land_mainloop()

land_use_main(realmain)
