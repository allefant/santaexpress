import game

char code[100] = "krampus1"
int codepos = -1
int _t = 0

def title_tick:
    _t++
    if _t > 60 * 30: _t = 0
    if not land_keybuffer_empty():
        int k, u
        land_keybuffer_next(&k, &u)
        if u == 13:
            game_create(code)
            land_stream_volume(land_stream_default(), 1 / 3.0)
            return
        if u == 8:
            if codepos == -1:
                codepos = 0
                memset(code, '.', 8)
            if codepos > 0:
                codepos--
        if codepos >= 0:
            if (u >= 'a' and u <= 'z') or (u >= '0' and u <= '9'):
                code[codepos++] = u
                if codepos > 7:
                    codepos = 7

def _text(int b, str t):
    auto lines = land_wordwrap_text(1280 - b, 720, t)
    land_print_lines(lines, 0)
    land_text_destroy_lines(lines)

def title_draw:
    float y = 0

    land_text_pos(640, y)
    land_color_set(land_color_name("white"))
    land_font_set(medium_font)
    land_print_center("KrampusHack 2019")
    y += land_line_height()

    land_text_pos(640, y)
    land_color_set(land_color_name("white"))
    land_font_set(small_font)
    land_print_center("entry by elias")
    y += land_line_height()
    
    land_color_set(land_color_name("crimson"))
    land_font_set(big_font)
    land_text_pos(640, y)
    land_print_center("Santa Express")
    y += land_line_height()

    land_text_pos(640, y)
    land_color_set(land_color_name("red"))
    land_font_set(medium_font)
    land_print_center("for FrankDrebin")
    y += land_line_height() * 2

    float x = 16
    land_color_set(land_color_name("silver"))
    land_filled_rectangle(8, y - 8, 1280 - 8, 720 - 8)
    land_color_set(land_color_name("dark green/2"))
    land_rectangle(8, y - 8, 1280 - 8, 720 - 8)
    land_font_set(small_font)
    land_text_pos(x + 56, y)
    land_image_draw_scaled(data_monster(0, (_t / 8) % 3)->image, x + 20, y + 64, 0.5, 0.5)
    _text(88, """'Tis the night before Christmas. Santa and the elves are busy with last minute preparations. As are you - the Krampus. You're on kitchen duty today, preparing food for the reindeer. You make your favorite dish, fish and bean stew. Unfortunately, soon after eating the stew, all the reindeer come down with a bad case of diarrhea. And Santa decides to go by train instead of sleigh this year.
""")

    land_image_draw_scaled(data_monster(4, 5 * 3 + (_t / 8) % 3)->image, x + 1280 + 60 * 3 - _t, y + 140, 0.5, 0.5)
    land_text_pos(x, y + 150)

    _text(32, """However, tragedy strikes. Apparently a horde of dragons has damaged the train tracks. Santa asks you to fix the tracks for him!
""")

    land_color_set(land_color_name("dark green"))
    _text(32, """The wishlist for this game was:
    1. The game should be 2D.
    2. Use a dynamically generated terrain.
    3. Cool exaggerated particle effects.
""")

    land_color_set(land_color_name("dark green/2"))
    _text(32, """All levels are randomly generated from a password. You can type a new password or keep the default one.
""")

    land_write("Password: ")
    land_font_set(medium_font)
    land_color_set(land_color_name("orange"))
    land_write("%s", code)
    land_color_set(land_color_name("black"))
    land_font_set(small_font)

    if codepos < 0:
        land_write(" (backspace to change)")
    else:
        land_write(" (type to change)")
    land_font_set(medium_font)
    land_print("")
        

    land_color_set(land_color_name("red") if (_t / 30) % 2 else land_color_name("white"))
    land_print("Press enter to create levels!")

    land_image_draw_scaled(data_monster(5, 5 * 3 + (_t / 8) % 3)->image, 1280 + 60 * 8 - _t * 1.5, 720 - 16, 0.5, 0.5)
    land_image_draw_scaled(data_monster(5, 1 * 3 + (_t / 8) % 3)->image, 8 - 60 * 18 + _t * 2, 190, 0.5, 0.5)
    land_image_draw_scaled(data_monster(5, 6 * 3 + (_t / 8) % 3)->image, 1280 + 60 * 39 - _t * 3, 0 - 60 * 18 + _t * 1.5, 0.5, 0.5)
    
    land_image_draw_scaled(data_monster(3, 1 * 3 + (_t / 8) % 3)->image, _t * 3 - 60 * 12 * 3, 480, 0.5, 0.5)
