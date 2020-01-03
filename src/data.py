import common

enum:
    DataNone
    DataSnow
    DataSnow125
    DataSnow250
    DataSnow375
    DataSnow500
    DataSnow625
    DataSnow750
    DataSnow875
    DataSnow1000
    DataSnow2000
    DataSlopesCount
    DataSpruce
    DataPine
    DataTroll
    DataDragon0
    DataDragon1
    DataDragon2
    DataEngine
    DataCar
    DataMonsterCount
    DataSign
    DataStop
    DataEngineSound
    DataTrackSound
    DataStepSound1
    DataStepSound2
    DataStepSound3
    DataStepSound4
    DataRemoveTrackSound
    DataPlantSound
    DataClearSound
    DataSnowUpSound
    DataSnowDownSound
    DataWhistleSound
    DataFireSound
    DataCount

class Image:
    LandImage* image
    LandImage* outline

Image _images[DataCount]
Image _slopes[DataSlopesCount * 4]
#Image _corners[DataCount * 4]
#Image _inlays[DataCount * 4]
Image _slopes_tracks[DataSlopesCount * 4]
Image _monster[(DataMonsterCount - DataTroll) * 8 * 3]
Image _track[16]
LandSound *_sounds[DataCount]
LandAtlas *_atlas

global LandFont *small_font, *medium_font, *big_font
double _font_scale

def data_image(int id) -> Image*:
    return _images + id

def data_slope(int id) -> Image*:
    return _slopes + id

#def data_corner(int id) -> Image*:
#    return _corners + id

def data_slope_tracks(int id) -> Image*:
    return _slopes_tracks + id

def data_monster(int id, frame) -> Image*:
    return _monster + id * 8 * 3 + frame

def data_track(int id) -> Image*:
    return _track + id

def _load(int id, Image* array, str name)
    for int i in range(2):
        char *s = land_strdup("pics/")
        land_concatenate(&s, name)
        land_concatenate(&s, "_0001" if i == 0 else "_0001_outline")
        land_concatenate(&s, ".png")

        auto pic = land_atlas_image_create(_atlas, s)
        if pic:
            pic.x += 256 / 2
            pic.y += 256 * 3 / 4
        else:
            print("Not in atlas: %s", s)
            pic = land_image_load(s)
            land_image_offset(pic, 256 / 2, 256 * 3 / 4)
            land_image_auto_crop(pic)
        if not pic:
            print("Could not load %s", s)
            return
        #print("loaded %s", s)
        if i == 0: array[id].image = pic
        if i == 1: array[id].outline = pic

        land_free(s)

def _loads(int id, str name):
    char *s = land_strdup("sounds/")
    land_concatenate(&s, name)
    land_concatenate(&s, ".ogg")
    auto sound = land_sound_load(s)
    if not sound:
        print("Could not load %s", s)
        return
    _sounds[id] = sound
    land_free(s)

def _loadm(int id, str name):
    char *s = land_strdup("sounds/")
    land_concatenate(&s, name)
    land_concatenate(&s, ".ogg")
    land_stream_music(land_stream_default(), s)
    land_stream_volume(land_stream_default(), 1)
    land_free(s)

def data_load:
    _loadm(1, "Winter Snow")

    _atlas = land_atlas_new("atlas.txt")
    
    _loads(DataEngineSound, "engine")
    _loads(DataTrackSound, "clamour3")
    _loads(DataStepSound1, "grassy-footstep1")
    _loads(DataStepSound2, "grassy-footstep2")
    _loads(DataStepSound3, "grassy-footstep3")
    _loads(DataStepSound4, "grassy-footstep4")
    _loads(DataRemoveTrackSound, "clamour9")
    _loads(DataPlantSound, "thwack-02")
    _loads(DataClearSound, "thwack-07")
    _loads(DataSnowUpSound, "Snow_Shoes-08")
    _loads(DataSnowDownSound, "Snow_Shoes-19")
    _loads(DataWhistleSound, "steamwhistle_0")
    _loads(DataFireSound, "fire")
    
    _load(DataSnow, _images, "snow")
    _load(DataSpruce, _images, "snow_spruce")
    _load(DataPine, _images, "snow_pine")
    _load(DataSnow2000, _images, "snow2000")
    for int i in range(8):
        int h = 125 * (1 + i)
        char name[100]
        sprintf(name, "snow%d", h)
        _load(DataSnow125 + i, _images, name)
        for int j in range(4):
            sprintf(name, "snow%d_slope%d", h, j)
            _load(j + (DataSnow125 + i) * 4, _slopes, name)
            #sprintf(name, "snow%d_corner%d", h, j)
            #_load(j + (DataSnow125 + i) * 4, _corners, name)
            #sprintf(name, "snow%d_inlay%d", h, j)
            #_load(j + (DataSnow125 + i) * 4, _inlays, name)

            str a = "5" if j == 0 or j == 2 else "10"
            sprintf(name, "tracks%s_%d_%d", a,j, h)
            _load(j + (DataSnow125 + i) * 4, _slopes_tracks, name)

    str monsters[] = {"snow_troll", "snowdragon2", "snowdragon1",
        "snowdragon0", "engine", "snowcar"}
    for int mi in range(DataTroll, DataMonsterCount):
        _load((mi - DataTroll) * 24, _monster, monsters[mi - DataTroll])
        for int d in range(8):
            for int a in range(3):
                char name[100]
                sprintf(name, "%s_%d%d", monsters[mi - DataTroll], d, a)
                _load((mi - DataTroll) * 24 + a + d * 3, _monster, name)
    _load(5, _track, "tracks5")
    _load(10, _track, "tracks10")
    _load(3, _track, "curve1")
    _load(6, _track, "curve2")
    _load(9, _track, "curve0")
    _load(12, _track, "curve3")
    _load(DataSign, _images, "trainsign")
    _load(DataStop, _images, "stopsign")

    float scale = land_scale_to_fit(1280, 720, 256)
    data_reload_fonts(scale)

def data_reload_fonts(double scale):
    if small_font: land_font_destroy(small_font)
    if medium_font: land_font_destroy(medium_font)
    if big_font: land_font_destroy(big_font)

    _font_scale = scale

    small_font = land_font_load("URWGothicBook.ttf", 18 * _font_scale)
    medium_font = land_font_load("URWGothicBook.ttf", 32 * _font_scale)
    big_font = land_font_load("URWGothicBook.ttf", 48 * _font_scale)

def data_font_scale(bool on):
    double s = on ? 1.0 / _font_scale : 1.0
    land_font_scale(big_font, s)
    land_font_scale(medium_font, s)
    land_font_scale(small_font, s)

def data_play(int sid):
    land_sound_play(_sounds[sid], 1, 0, 1)

def data_play_vol(int sid, float vol):
    land_sound_play(_sounds[sid], vol, 0, 1)

def data_loop(int sid):
    land_sound_loop(_sounds[sid], 1, 0, 1)

def data_stop(int sid):
    land_sound_stop(_sounds[sid])
