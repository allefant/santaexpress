import land.land

macro pi LAND_PI

global int common_mode
global int common_outline
global int common_grid

def print(char const *s, ...):
    va_list args
    va_start(args, s)
    vprintf(s, args)
    va_end(args)
    printf("\n")
