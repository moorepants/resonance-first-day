import numpy as np
import sympy as sm
import matplotlib.pyplot as plt
import matplotlib.patches as pat
from resonance.nonlinear_systems import SingleDoFNonLinearSystem


def print_eq(lhs, rhs):
    """Returns a SymPy equality of the provided left and right hand sides.

    Parameters
    ==========
    lhs : string
        A valid LaTeX string.
    rhs : sympifiable
        A SymPy expression.

    """
    return sm.Eq(sm.Symbol(lhs), rhs)


def eom_in_first_order_form(T, U, q, u, t):
    """Returns the equations of motion of a system.abs

    Parameters
    ==========
    T
    U
    q
    u
    t
    """
    L = T - U
    eom = L.diff(q.diff()).diff(t) - L.diff(q)
    mass = eom.expand().coeff(q.diff(t, 2))
    kin = u
    dyn = -eom.xreplace({q.diff(t, 2): 0}).xreplace({q.diff(): u}) / mass
    dyn = sm.simplify(dyn)
    return sm.Eq(sm.Matrix([q.diff(), u.diff()]), sm.Matrix([kin, dyn]))


class BookCupSystem(SingleDoFNonLinearSystem):

    def __init__(self):

        super(BookCupSystem, self).__init__()

        self.constants['d'] = 0.029  # m
        self.constants['l'] = 0.238  # m
        self.constants['r'] = 0.042  # m
        self.constants['m'] = 1.058  # kg
        self.constants['g'] = 9.81  # m/s**2
        self.coordinates['theta'] = 0.0  # rad
        self.speeds['omega'] = 0.0  # rad/s

        def bottom_left_x(r, l, theta):
            return r * np.sin(theta) - (r * theta + l / 2) * np.cos(theta)

        self.add_measurement('bottom_left_x', bottom_left_x)

        def bottom_left_y(r, l, theta):
            return r + r * np.cos(theta) + (r * theta + l / 2) * np.sin(theta)

        self.add_measurement('bottom_left_y', bottom_left_y)

        def create_plot(r, l, d, theta, bottom_left_x, bottom_left_y):
            fig, ax = plt.subplots(1, 1)
            width = max(l, r * 2)
            ax.set_xlim((-width / 2 - width / 10, width / 2 + width / 10))
            ax.set_ylim((0.0, 2 * r + 2 * d))
            ax.set_xlabel('x [m]')
            ax.set_ylabel('y [m]')
            ax.set_aspect('equal')

            circ = pat.Circle((0.0, r), radius=r)

            rect = pat.Rectangle((bottom_left_x, bottom_left_y),
                                 l, d,
                                 angle=-np.rad2deg(theta),
                                 color='black')

            ax.add_patch(circ)
            ax.add_patch(rect)

            # make sure to return the rectangle, which moves at each time step!
            return fig, rect

        self.config_plot_func = create_plot

        def update_frame(theta, bottom_left_x, bottom_left_y, rect):
            rect.set_xy((bottom_left_x, bottom_left_y))
            rect.angle = -np.rad2deg(theta)
            rect._angle = -np.rad2deg(theta)

        self.config_plot_update_func = update_frame