class Shaders:
    VERTEX_SHADER = None
    TRIANGLE_FRAGMENT_SHADER = None
    POINT_FRAGMENT_SHADER = None

    @classmethod
    def init(cls, root):
        with open(root + "/vertex_shader.glsl") as file:
            cls.VERTEX_SHADER = "".join(file.readlines())
        with open(root + "/triangle_fragment_shader.glsl") as file:
            cls.TRIANGLE_FRAGMENT_SHADER = "".join(file.readlines())
        with open(root + "/point_fragment_shader.glsl") as file:
            cls.POINT_FRAGMENT_SHADER = "".join(file.readlines())
