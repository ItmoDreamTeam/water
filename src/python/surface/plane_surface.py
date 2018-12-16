import numpy as np

from surface.base_surface import BaseSurface


class PlaneSurface(BaseSurface):
    def __init__(self, size=(100, 100), nwave=5, max_height=0.2):
        super().__init__(size)
        self._wave_vector = 5 * (2 * np.random.rand(nwave, 2) - 1)
        self._angular_frequency = 3 * np.random.rand(nwave)
        self._phase = 2 * np.pi * np.random.rand(nwave)
        self._amplitude = max_height * np.random.rand(nwave) / nwave

    def height(self):
        x = np.linspace(-1, 1, self._size[0])[:, None]
        y = np.linspace(-1, 1, self._size[1])[None, :]
        z = np.zeros(self._size, dtype=np.float32)
        for n in range(self._amplitude.shape[0]):
            z[:, :] += self._amplitude[n] * np.cos(self._phase[n] +
                                                   x * self._wave_vector[n, 0] + y * self._wave_vector[n, 1] +
                                                   self._time * self._angular_frequency[n])
        return z

    def normal(self):
        x = np.linspace(-1, 1, self._size[0])[:, None]
        y = np.linspace(-1, 1, self._size[1])[None, :]
        grad = np.zeros(self._size + (2,), dtype=np.float32)
        for n in range(self._amplitude.shape[0]):
            dcos = -self._amplitude[n] * np.sin(self._phase[n] +
                                                x * self._wave_vector[n, 0] + y * self._wave_vector[n, 1] +
                                                self._time * self._angular_frequency[n])
            grad[:, :, 0] += self._wave_vector[n, 0] * dcos
            grad[:, :, 1] += self._wave_vector[n, 1] * dcos
        return grad
