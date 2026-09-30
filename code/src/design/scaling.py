"""
These are scaling laws for the motor. The scaling function are made to compute
caracteristics of the motor, given other parameters. If a function can't evaluate
a caracteristic (for example if out of range), it shall throw a ValueError exception
"""

class Scaler:
    """
    We create an object so that it can save global parameters
    """
    SPECIFIC_MASS_KG_PER_KW = 4  # kg/kW, conservative GIE estimate

    def __init__(self, requirements, filters):
        #saving a reference to gloabal parameters
        self.requirements = requirements
        self.filters = filters

    def scaling_mass(self, power_W : float) -> float:
        """
        Returns thruster mass in kg given input power in W.

        Source: Goebel & Katz (2008) flight hardware survey
        NSTAR:   8.0 kg / 2.3 kW = 3.5 kg/kW
        XIPS-25: 8.5 kg / 4.5 kW = 1.9 kg/kW
        T6:      ~3.0 kg/kW
        Conservative estimate: 4.0 kg/kW
        Uncertainty: factor ~2 depending on thruster class.
        """
        #potential errors
        if power_W <= 0:
            raise ValueError("Scaling error: power must be positive, got " + str(power_W))
        #law
        return self.SPECIFIC_MASS_KG_PER_KW * power_W / 1000