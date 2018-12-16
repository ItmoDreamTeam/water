class Shaders:
    MAIN_VERTEX_SHADER = None
    BACKGROUND_VERTEX_SHADER = None
    CAUSTICS_VERTEX_SHADER = None

    POINT_FRAGMENT_SHADER = None
    TRIANGLE_FRAGMENT_SHADER = None
    BACKGROUND_FRAGMENT_SHADER = None
    CAUSTICS_FRAGMENT_SHADER = None

    @classmethod
    def init(cls, root):
        with open(root + "/vertex/main_vertex_shader.glsl") as file:
            cls.MAIN_VERTEX_SHADER = "".join(file.readlines())
        with open(root + "/vertex/background_vertex_shader.glsl") as file:
            cls.BACKGROUND_VERTEX_SHADER = "".join(file.readlines())
        with open(root + "/vertex/caustics_vertex_shader.glsl") as file:
            cls.CAUSTICS_VERTEX_SHADER = "".join(file.readlines())

        with open(root + "/fragment/point_fragment_shader.glsl") as file:
            cls.POINT_FRAGMENT_SHADER = "".join(file.readlines())
        with open(root + "/fragment/triangle_fragment_shader.glsl") as file:
            cls.TRIANGLE_FRAGMENT_SHADER = "".join(file.readlines())
        with open(root + "/fragment/background_fragment_shader.glsl") as file:
            cls.BACKGROUND_FRAGMENT_SHADER = "".join(file.readlines())
        with open(root + "/fragment/caustics_fragment_shader.glsl") as file:
            cls.CAUSTICS_FRAGMENT_SHADER = "".join(file.readlines())
