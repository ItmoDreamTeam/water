from vispy import gloo, app, io
from shader import *
from surface import Surface


class Canvas(app.Canvas):
    def __init__(self, surface, sky="./src/resources/fluffy_clouds.png", bed="./src/resources/seabed.png"):
        app.Canvas.__init__(self, size=(600, 600), title="Water surface simulator 2")
        self.surface = surface
        self.sky = io.read_png(sky)
        self.bed = io.read_png(bed)
        self.program = gloo.Program(VERTEX_SHADER, TRIANGLE_FRAGMENT_SHADER)
        self.program_point = gloo.Program(VERTEX_SHADER, POINT_FRAGMENT_SHADER)
        pos = self.surface.position()
        self.program["a_position"] = pos
        self.program_point["a_position"] = pos
        self.program['u_sky_texture'] = gloo.Texture2D(self.sky, wrapping='repeat', interpolation='linear')
        self.program['u_bed_texture'] = gloo.Texture2D(self.bed, wrapping='repeat', interpolation='linear')
        self.program_point["u_eye_height"] = self.program["u_eye_height"] = 3
        self.program["u_alpha"] = 0.9
        self.program["u_bed_depth"] = 1
        self.triangles = gloo.IndexBuffer(self.surface.triangulation())
        self.are_points_visible = False
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.activate_zoom()
        self.show()

    def activate_zoom(self):
        self.width, self.height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)

    def on_draw(self, event):
        gloo.set_state(clear_color=(0, 0, 0, 1), blend=False)
        gloo.clear()
        self.program["a_height"] = self.surface.height()
        self.program["a_normal"] = self.surface.normal()
        gloo.set_state(depth_test=True)
        self.program.draw('triangles', self.triangles)
        if self.are_points_visible:
            self.program_point["a_height"] = self.program["a_height"]
            gloo.set_state(depth_test=False)
            self.program_point.draw('points')

    def on_timer(self, event):
        self.surface.propagate(0.01)
        self.update()

    def on_resize(self, event):
        self.activate_zoom()

    def on_key_press(self, event):
        if event.key == 'Escape':
            self.close()
        elif event.key == ' ':
            self.are_points_visible = not self.are_points_visible


if __name__ == '__main__':
    c = Canvas(Surface(nwave=5, max_height=0.3))
    app.run()
