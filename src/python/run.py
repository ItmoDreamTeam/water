from canvas import Canvas
from shaders import Shaders
from surface.plane_surface import PlaneSurface

ROOT = "../.."
Shaders.init(ROOT + "/src/glsl")
surface = PlaneSurface(nwave=5, max_height=0.3)
c = Canvas(surface, sky=ROOT + "/src/resources/fluffy_clouds.png", bed=ROOT + "/src/resources/seabed.png")
c.measure_fps()
c.run()
