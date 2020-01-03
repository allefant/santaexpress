import common

macro N 256
macro TS 32

class Particle:
    float x, y, z
    float dx, dy, dz, fade, grow, gravity
    float r, g, b, a
    float s
    int t

Particle particles[N]
int _first, _last
LandTriangles* _t

def _cb(int x, int y, unsigned char *rgba, void *user):
    int m = TS / 2 - 1
    x -= m
    y -= m
    float v = sqrt(x * x + y * y)
    v = 1 - v / m
    if v < 0: v = 0
    v = (1 - ((1 - v) * (1 - v))) * 255
    if v > 255: v = 255
    rgba[0] = v
    rgba[1] = v
    rgba[2] = v
    rgba[3] = v

def particles_init:
    _t = land_triangles_new()
    land_triangles_can_cache(_t, False)
    for int i in range(N):
        for int j in range(6):
            land_add_vertex(_t, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    auto tex = land_image_new(TS, TS)
    land_image_write_callback(tex, _cb, None)
    land_triangles_texture(_t, tex)

def particle_add(float x, y, z, r, g, b, a, s) -> Particle*:
    Particle* p = particles + _last
    p.x = x
    p.y = y
    p.z = z
    p.r = r
    p.g = g
    p.b = b
    p.a = a
    p.s = s
    p.dx = 0
    p.dy = 0
    p.dz = 0
    p.fade = 1
    p.grow = 1
    p.t = 60
    p.gravity = 0

    _last++
    if _last >= N: _last = 0
    if _last == _first:
        _first++
        if _first >= N: _first = 0

    return p

def _add(int ip):
    Particle* p = particles + ip
    int i = ip * 6
    if p.t == 0:
        for int j in range(6):
            land_update_vertex(_t, i + j, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        return
    float x = p.x, y = p.y - p.z, z = 0, s = p.s
    land_update_vertex(_t, i + 0, x - s, y - s, z, 0, 0, p.r, p.g, p.b, p.a) 
    land_update_vertex(_t, i + 1, x + s, y - s, z, TS, 0, p.r, p.g, p.b, p.a) 
    land_update_vertex(_t, i + 2, x + s, y + s, z, TS, TS, p.r, p.g, p.b, p.a)

    land_update_vertex(_t, i + 3, x + s, y + s, z, TS, TS, p.r, p.g, p.b, p.a) 
    land_update_vertex(_t, i + 4, x - s, y - s, z, 0, 0, p.r, p.g, p.b, p.a) 
    land_update_vertex(_t, i + 5, x - s, y + s, z, 0, TS, p.r, p.g, p.b, p.a) 

def particles_tick:
    for int i in range(N):
        Particle* p = particles + i
        if p.t == 0: continue
        p.x += p.dx
        p.y += p.dy
        p.z += p.dz
        p.r *= p.fade
        p.g *= p.fade
        p.b *= p.fade
        p.a *= p.fade
        p.s *= p.grow
        p.dz += p.gravity
        p.t--

def particles_draw:
    for int i in range(N):
        _add(i)
    land_triangles_refresh(_t)
    land_triangles_draw(_t)
