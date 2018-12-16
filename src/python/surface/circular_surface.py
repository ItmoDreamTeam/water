import numpy as np

from surface.base_surface import BaseSurface


class CircularSurface(BaseSurface):
    def __init__(self, size=(100, 100), max_height=0.2, wave_length=0.3, center=(0., 0.), speed=3):
        super().__init__(size)
        self._amplitude = max_height
        self._omega = 2 * np.pi / wave_length
        self._center = np.asarray(center, dtype=np.float32)
        self._speed = speed

    def height(self):
        x = np.linspace(-1, 1, self._size[0])[:, None]
        y = np.linspace(-1, 1, self._size[1])[None, :]
        d = np.sqrt((x - self._center[0]) ** 2 + (y - self._center[1]) ** 2)
        arg = self._omega * d - self._time * self._speed
        z = np.zeros(self._size, dtype=np.float32)
        z[:, :] = self._amplitude * np.cos(arg)
        return z

    def normal(self):
        x = np.linspace(-1, 1, self._size[0])[:, None]
        y = np.linspace(-1, 1, self._size[1])[None, :]
        d = np.sqrt((x - self._center[0]) ** 2 + (y - self._center[1]) ** 2)
        arg = self._omega * d - self._time * self._speed
        dcos = -self._amplitude * self._omega * np.sin(arg)
        grad = np.zeros(self._size + (2,), dtype=np.float32)
        grad[:, :, 0] += (x - self._center[0]) * dcos / d
        grad[:, :, 1] += (y - self._center[1]) * dcos / d
        return grad
