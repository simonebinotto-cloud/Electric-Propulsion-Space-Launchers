"""
Main design module for the ion thruster preliminary design tool.

Sweeps over beam voltage V_b and beam current I_b to find the
operating point that best satisfies the chosen objective.

V_b controls Isp (efficiency), I_b controls thrust and power.

Equations from Goebel & Katz, Fundamentals of Electric
Propulsion, JPL (2008).
"""
from src.design.scaling import Scaler
import math

#g0
G0 = 9.81

# Propellant ion masses in AMU
PROPELLANT_MASS_AMU = {
    0: 131.3,   # Xenon
    1: 83.8,    # Krypton
    2: 126.9    # Iodine
}

# Physical constants
E_CHARGE = 1.602e-19   # C
AMU      = 1.6605e-27  # kg

class Designer:

    def __init__(self, requirements, filters):
        """
        Sets up the designer with mission requirements and
        design filters from the reader.
        """
        #saving a reference to gloabal parameters
        self.requirements = requirements
        self.filters = filters

        #creating a scaler
        self.scaler = Scaler(requirements, filters)

        # These will hold the best result after design()
        self.motor_mass       = 0
        self.propellant_mass  = 0
        self.total_mass       = 0
        self.isp              = 0
        self.thrust           = 0
        self.electrical_power = 0
        self.beam_current     = 0
        self.eta_T            = 0
        self.discharge_power  = 0
        self.epsilon_d        = 0
        self.trip_time        = 0
        self.beam_voltage     = 0

        # Full sweep results (all feasible points)
        self.sweep_results    = []

    def design(self):
        """
        Runs the 2D sweep over V_b and I_b and stores the best
        feasible result.

        A point is feasible if:
          - input power <= max_power
          - thrust >= min_thrust
          - trip time <= max_duration

        Raises ValueError if no feasible point is found.
        """
        V_min  = self.filters["beam_voltage_min"]
        V_max  = self.filters["beam_voltage_max"]
        V_step = self.filters["beam_voltage_step"]
        I_min  = self.filters["beam_current_min"]
        I_max  = self.filters["beam_current_max"]
        I_step = self.filters["beam_current_step"]

        self.sweep_results = []
        best = None

        V_b = V_min
        while V_b <= V_max:
            I_b = I_min
            while I_b <= I_max:
                try:
                    result = self.evaluate(V_b, I_b)
                    self.sweep_results.append(result)
                    if best is None or self._is_better(result, best):
                        best = result
                except ValueError:
                    pass
                I_b += I_step
            V_b += V_step

        if best is None:
            raise ValueError(
                "No feasible design found. Check power budget, thrust limits and mission requirements."
            )

        # store best
        self.beam_voltage    = best["V_b"]
        self.beam_current    = best["I_b"]
        self.isp             = best["isp"]
        self.thrust          = best["thrust"]
        self.eta_T           = best["eta_T"]
        self.motor_mass      = best["motor_mass"]
        #self.ppu_mass        = best["ppu_mass"]
        #self.tank_mass       = best["tank_mass"]
        self.propellant_mass = best["propellant_mass"]
        self.total_mass      = best["total_mass"]
        self.electrical_power = best["electrical_power"]
        self.discharge_power = best["discharge_power"]
        self.epsilon_d       = best["epsilon_d"]
        self.trip_time       = best["trip_time"]

    def _is_better(self, candidate, current_best):
        """
        Returns True if candidate is better than current_best
        according to the chosen objective.
        objective 0: minimise total mass
        objective 1: minimise trip time
        objective 2: maximise Isp
        """
        obj = int(self.filters["objective"])
        if obj == 0:
            return candidate["total_mass"] < current_best["total_mass"]
        elif obj == 1:
            return candidate["trip_time"] < current_best["trip_time"]
        elif obj == 2:
            return candidate["isp"] > current_best["isp"]
        else:
            raise ValueError("Unknown objective: " + str(obj))

    def evaluate(self, V_b, I_b):
        """
        Evaluates one (V_b, I_b) operating point and returns
        all computed quantities as a dict.
        Raises ValueError if the point is infeasible.
        """
        eta_m = self.filters["eta_m"]
        eta_e = self.filters["eta_e"]
        xi    = self.filters["xi"]

        M = PROPELLANT_MASS_AMU[int(self.filters["propellant"])] * AMU

        # Exhaust velocity (Goebel 2.3-6)
        v_e = math.sqrt(2 * E_CHARGE * V_b / M)

        # Isp (Goebel 2.4-8)
        isp = xi * eta_m * v_e / G0

        # Total efficiency (Goebel 2.5-7)
        eta_T = xi**2 * eta_m * eta_e

        # Thrust from beam current (Goebel 2.3-8)
        thrust = I_b * math.sqrt(2 * M * V_b / E_CHARGE) * 1000  # mN

        # Input power (Goebel 2.5-1)
        electrical_power = I_b * V_b / eta_e  # W

        if electrical_power > self.filters["max_power"]:
            raise ValueError("Power budget exceeded")

        if thrust < self.filters["min_thrust"]:
            raise ValueError("Thrust below minimum")

        # Discharge power and ion production cost (Goebel 2.5-2)
        discharge_power = electrical_power - I_b * V_b
        epsilon_d = discharge_power / I_b  # eV/ion

        # Motor mass from scaling
        motor_mass = self.scaler.scaling_mass(electrical_power)

        # Propellant mass (Goebel 2.1-11)
        empty_mass = self.requirements["payload_mass"] + motor_mass
        propellant_mass = empty_mass * (
            math.exp(self.requirements["deltav"] * 1000 / (G0 * isp)) - 1
        )
        total_mass = empty_mass + propellant_mass

        # Trip time
        m_dot     = thrust * 1e-3 / v_e
        trip_time = propellant_mass / m_dot / 3600  # hours

        if trip_time > self.filters["max_duration"]:
            raise ValueError("Trip time exceeds mission duration limit")

        return {
            "V_b":              V_b,
            "I_b":              I_b,
            "isp":              isp,
            "thrust":           thrust,
            "eta_T":            eta_T,
            "motor_mass":       motor_mass,
            "propellant_mass":  propellant_mass,
            "total_mass":       total_mass,
            "electrical_power": electrical_power,
            "discharge_power":  discharge_power,
            "epsilon_d":        epsilon_d,
            "trip_time":        trip_time
        }