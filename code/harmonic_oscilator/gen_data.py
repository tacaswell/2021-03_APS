"""
Generate synthetic damped oscillator data for demo.
"""
from collections import namedtuple

import numpy as np
from scipy.optimize import curve_fit

import xarray as xa

# ζ, φ, ω0, π

π = np.pi


def single_get_data(t, *, ζ=0.05, ω0=5, φ=π / 2, A=2, noise_scale=0.05):
    r"""
    Generate single time trace of a damped harmonic oscillator

    This returns data of the form

    .. math::

        y(t) = A e^{-\zeta\omega_0t} \sin\left(\sqrt{1 - \zeta^2}\omega_0t + \varphi\right) + \eta


    where :math:`\eta` noise drawn from the normal distribution and scaled by
    *noise_scale*.

    Parameters
    ----------
    t : array
        The times to sample at

    ζ : float, 0 < ζ < 1
        The damping term.

    ω0 : float, 0 < ω0
        The frequency of the oscillator

    φ : float, 0 < φ < 2π
        The phase of the amplitude

    A : float
        The amplitude of the oscillator at t=0

    noise_scale : float
        scaling factor for the inject noise.

    Returns
    -------
    y : array
       The position of the oscillator at times *t* + noise.

    """
    y = A * np.exp(-t * ζ * ω0) * np.sin(np.sqrt(1 - ζ * ζ) * ω0 * t + φ)
    y += np.random.randn(*y.shape) * noise_scale
    return y


def get_data(N=25, seed=19680808):
    """
    Generate sample data set of measurements from several oscillators.

    The frequency of the oscillators scales with the square of an arbitrary
    *control* value and the damping varies randomly.

    This is meant to simulating fabricating *N* oscillators, varying some
    independent parameter.

    These oscillators are characterized by displacing them from their
    equilibrium position by a fixed amount and measuring the displacement as a
    function of time as they ring down.

    Parameters
    ----------
    N : int
        The number of sample datasets to generate.

    seed : int
        The seed to use pass to `np.random.seed`.  This ensures the reproducibility of
        the data generation.

    Returns
    -------
    d : xarray.DataArray
        The first dimension is *control* and the second is *time*
    """
    np.random.seed(seed)
    t = np.linspace(0, 5 * 2 * π, 2056 * 2)
    control = np.linspace(15, 30, N)
    d = xa.DataArray(
        [
            single_get_data(
                t, ω0=2 + (c / 15) ** 2, ζ=(0.02 + np.random.random() * 0.04)
            )
            for c in control
        ],
        dims=("control", "time"),
        coords={"control": control, "time": t},
    )
    return d


def curve(t, A, zeta, omega, phi):
    """Function for fitting damped oscillators"""
    return (
        A * np.exp(-t * zeta * omega) * np.sin(np.sqrt(1 - zeta ** 2) * omega * t + phi)
    )


class Params(namedtuple("Params", "A,zeta,omega,phi")):
    """Helper class to wrap result of scipy.optomize.curve_fit"""

    def __str__(self):
        return (
            f"(A={self.A:.2f}, "
            f"ζ={self.zeta:.2f}, "
            f"ω0={self.omega:.2f}, "
            f"φ={self.phi:.2f})"
        )

    def _repr_latex_(self):
        return (
            f"$(A={self.A:.2f}, "
            f"\\zeta={self.zeta:.2f}, "
            f"\\omega_0={self.omega:.2f},"
            f"\\varphi={self.phi:.2f})$"
        )

    def sample(self, t):
        return curve(t, *self)


def fit(m):
    """
    Given single oscillator decay, fit it.
    """
    t = m.coords["time"]
    z = m.values
    # fit
    popt, pcov = curve_fit(
        curve, t, z, bounds=([0, 0, 0, 0], [np.inf, 1, np.inf, 2 * np.pi])
    )
    # wrap
    return Params(*popt)
