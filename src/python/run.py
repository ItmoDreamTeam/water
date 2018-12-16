from canvas import Canvas
from shaders import Shaders
from surface.plane_surface import PlaneSurface
from surface.circular_surface import CircularSurface

ROOT = "../.."
Shaders.init(ROOT + "/src/glsl")
# surface = PlaneSurface()
surface = CircularSurface(max_height=0.02)
c = Canvas(surface, sky=ROOT + "/src/resources/fluffy_clouds.png", bed=ROOT + "/src/resources/seabed.png")
c.measure_fps()
c.run()
