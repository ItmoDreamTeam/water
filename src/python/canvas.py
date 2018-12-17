import numpy as np
from vispy import gloo, app, io

from shaders import Shaders


class Canvas(app.Canvas):

    @staticmethod
    def normalize(vec):
        vec = np.asarray(vec, dtype=np.float32)
        return vec / np.sqrt(np.sum(vec * vec, axis=-1))[..., None]

    @staticmethod
    def run():
        app.run()

    def __init__(self, surface, sky, bed):
        self.surface = surface
        self.sky = io.read_png(sky)
        self.bed = io.read_png(bed)
        app.Canvas.__init__(self, size=(800, 800), position=(500, 100), title="Waving Water")
        gloo.set_state(clear_color=(1, 1, 1, 1))

        # Create shaders
        self.program_main = gloo.Program(Shaders.MAIN_VERTEX_SHADER, Shaders.MAIN_FRAGMENT_SHADER)
        self.program_point = gloo.Program(Shaders.MAIN_VERTEX_SHADER, Shaders.POINT_FRAGMENT_SHADER)
        self.program_background = gloo.Program(Shaders.BACKGROUND_VERTEX_SHADER, Shaders.BACKGROUND_FRAGMENT_SHADER)
        self.program_caustics = gloo.Program(Shaders.CAUSTICS_VERTEX_SHADER, Shaders.CAUSTICS_FRAGMENT_SHADER)

        # Set values
        positions = self.surface.position()
        self.program_main["a_position"] = positions
        self.program_point["a_position"] = positions
        self.program_caustics["a_position"] = positions
        self.program_background['a_position'] = np.array([[-1.0, -1.0], [1.0, -1.0],
                                                          [1.0, 1.0], [-1.0, 1.0]], dtype=np.float32)
        self.program_main['u_sky_texture'] = self.program_background['u_sky_texture'] = \
            gloo.Texture2D(self.sky, wrapping='repeat', interpolation='linear')
        self.program_main['u_bed_texture'] = self.program_background['u_bed_texture'] = \
            gloo.Texture2D(self.bed, wrapping='repeat', interpolation='linear')
        self.program_point["u_eye_height"] = self.program_main["u_eye_height"] = \
            self.program_background['u_eye_height'] = self.program_caustics["u_eye_height"] = 0.4
        self.program_main["u_alpha"] = \
            self.program_caustics["u_alpha"] = 0.7
        self.program_main["u_bed_depth"] = self.program_background['u_bed_depth'] = \
            self.program_caustics["u_bed_depth"] = 0.5
        self.program_main["u_sun_direction"] = self.program_background['u_sun_direction'] = \
            self.program_caustics["u_sun_direction"] = Canvas.normalize([0, 0, 1])
        self.program_main["u_sun_diffused_color"] = [1, 1, 0.5]
        self.program_main["u_sun_reflected_color"] = self.program_background['u_sun_reflected_color'] = [1, 1, 0.5]
        self.program_main["u_water_ambient_color"] = \
            self.program_background['u_water_ambient_color'] = [0.5, 0.75, 0.9]
        self.triangles = gloo.IndexBuffer(self.surface.triangulation())
        self.triangles_background = gloo.IndexBuffer(np.array([[0], [1], [2], [2], [3], [0]], dtype=np.uint16))

        # GUI
        self.camera = np.array([0, 0, 1])
        self.up = np.array([0, 1, 0])
        self.set_camera()
        self.are_points_visible = False
        self.drag_start = None
        self.diffused_flag = True
        self.reflected_flag = True
        self.bed_flag = True
        self.depth_flag = True
        self.sky_flag = True
        self.caustics_flag = False
        self.apply_flags()

        # Run everything
        self._timer = app.Timer(connect=self.on_timer, start=True)
        self.activate_zoom()
        self.show()

    def on_draw(self, event):
        heights = self.surface.height()
        normals = self.surface.normal()
        self.program_main["a_height"] = self.program_caustics["a_height"] = \
            self.program_point["a_height"] = heights
        self.program_main["a_normal"] = self.program_caustics["a_normal"] = normals

        gloo.clear()
        if self.caustics_flag:
            self.program_caustics.draw('triangles', self.triangles)
        else:
            self.program_background.draw('triangles', self.triangles_background)
            self.program_caustics.draw('triangles', self.triangles)
            self.program_main.draw('triangles', self.triangles)
        if self.are_points_visible:
            self.program_point.draw('points')

    def apply_flags(self):
        self.program_main["u_diffused_mult"] = 0.5 if self.diffused_flag else 0
        self.program_main["u_reflected_mult"] = \
            self.program_background["u_reflected_mult"] = 1.0 if self.reflected_flag else 0
        self.program_main["u_bed_mult"] = self.program_background["u_bed_mult"] = 1 if self.bed_flag else 0
        self.program_main["u_depth_mult"] = self.program_background["u_depth_mult"] = 1 if self.depth_flag else 0
        self.program_main["u_sky_mult"] = self.program_background["u_sky_mult"] = 1 if self.sky_flag else 0

    def set_camera(self):
        rotation = np.zeros((4, 4), dtype=np.float32)
        rotation[3, 3] = 1
        rotation[0, :3] = np.cross(self.up, self.camera)
        rotation[1, :3] = self.up
        rotation[2, :3] = self.camera
        world_view = rotation
        self.program_main['u_world_view'] = world_view.T
        self.program_point['u_world_view'] = world_view.T
        self.program_background['u_world_view'] = world_view.T
        self.program_caustics['u_world_view'] = world_view.T

    def rotate_camera(self, shift):
        right = np.cross(self.up, self.camera)
        new_camera = self.camera - right * shift[0] + self.up * shift[1]
        new_up = self.up - self.camera * shift[0]
        self.camera = Canvas.normalize(new_camera)
        self.up = Canvas.normalize(new_up)
        self.up = np.cross(self.camera, np.cross(self.up, self.camera))

    def activate_zoom(self):
        self.width, self.height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)

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
            print("Show lattice vertices:", self.are_points_visible)
        elif event.key == '1':
            self.diffused_flag = not self.diffused_flag
            print("Show sun diffused light:", self.diffused_flag)
            self.apply_flags()
        elif event.key == '2':
            self.bed_flag = not self.bed_flag
            print("Show refracted image of seabed:", self.bed_flag)
            self.apply_flags()
        elif event.key == '3':
            self.depth_flag = not self.depth_flag
            print("Show ambient light in water:", self.depth_flag)
            self.apply_flags()
        elif event.key == '4':
            self.sky_flag = not self.sky_flag
            print("Show reflected image of sky:", self.sky_flag)
            self.apply_flags()
        elif event.key == '5':
            self.reflected_flag = not self.reflected_flag
            print("Show reflected image of sun:", self.reflected_flag)
            self.apply_flags()
        elif event.key == '`':
            self.caustics_flag = not self.caustics_flag
            print("Show caustics only:", self.caustics_flag)

    def screen_to_gl_coordinates(self, pos):
        return 2 * np.array(pos) / np.array(self.size) - 1

    def on_mouse_press(self, event):
        self.drag_start = self.screen_to_gl_coordinates(event.pos)

    def on_mouse_move(self, event):
        if not self.drag_start is None:
            pos = self.screen_to_gl_coordinates(event.pos)
            self.rotate_camera(pos - self.drag_start)
            self.drag_start = pos
            self.set_camera()
            self.update()

    def on_mouse_release(self, event):
        self.drag_start = None
