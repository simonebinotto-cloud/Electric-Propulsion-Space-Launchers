"""
It is specified in the ressources PDF that the interface shall be using text files for interface.
(cf 4.4.14)

This code thus is designed to read parameter files and compile their value in a dictionnary,
as well as detecting and dealing with potential errors that could occur in those files.

Files should be on the format:
parameter1: value1
parameter2: value2
...
parametern: valuen
"""

#necessary parameters (requirements)
requirements_list = [
    "deltav", "payload_mass"
]

#non-necessary parameters (filters or default values)
filters_list = [
    "min_thrust", "max_power", "propellant",
    "eta_m", "eta_e", "xi",
    "beam_voltage_min", "beam_voltage_max", "beam_voltage_step",
    "beam_current_min", "beam_current_max", "beam_current_step",
    "max_duration",
    "objective"
]

filters_default = {
    "min_thrust" : 0,
    "max_power" : float('inf'),
    "propellant" : 0,
    "eta_m":             0.90,
    "eta_e":             0.85,
    "xi":                0.97,
    "beam_voltage_min":  800,
    "beam_voltage_max":  2000,
    "beam_voltage_step": 10,
    "beam_current_min":  0.5,
    "beam_current_max":  3.0,
    "beam_current_step": 0.1,
    "max_duration":      float('inf'),
    "objective":         0
}

class Reader:

    def __init__(self, filename : str):
        """
        Creates the reader and binds it to a file. Launches the read
        """
        self.filename = filename
        self.line_number = 0
        #data dictionaries
        self.requirements = {}
        self.filters = {}
        #ready status for execution
        self.valid = True
        #detected errors lists
        self.errors = []
        #read launch
        self.read()
        #final checks
        self.validation()


    def read(self : str):
        """
        Main function of the read. Opens the parameter file and parses it line by line
        """
        try:
            with open(self.filename, "r") as file:
                for line in file:
                    self.line_number+=1
                    self.read_line(line)
        except FileNotFoundError:
            self.add_error(
                "Given filename does not exists ",
                self.filename
            )
            return

    def read_line(self, line):
        """
        Parses a singular line of parameter, performs checks and save its value
        """
        cleaned_line = line.strip()
        #ignore comments and empty line
        if cleaned_line == "" or line[0] == '#':
            return
        #tokenization
        tokens = cleaned_line.split()
        #syntax checks
        if len(tokens) < 2:
            self.add_error(
                "Unsufficient amount of tokens, expected \"param: value\", got ",
                cleaned_line
            )
            return
        if len(tokens) > 2:
            self.add_error(
                "Unexpected additional tokens, expected \"param: value\", got these additionnal tokens ",
                tokens[2:]
            )
            return
        if tokens[0][-1] != ':':
            self.add_error(
                "Parameter does not present colon, got ",
                cleaned_line
            )
            return
        #value retrieval
        value = 0.
        try:
            value = float(tokens[1])
        except ValueError:
            self.add_error(
                "Given value for parameter is not a valid double, got ",
                tokens[1]
            )
            return
        #data save
        parameter = tokens[0][:-1]
        self.save_parameter(parameter, value)
        
    def is_requirement(name : str) -> bool:
        """
        Checks if the given name is a valid requirement name
        """
        return name in requirements_list

    def is_filter(name : str) -> bool:
        """
        Checks if the given name is a valid filter name
        """
        return name in filters_list
    
    def get_parameters(self) -> tuple[dict, dict]:
        """
        Returns the two dictionnaries of parameters, the first one being the requirements
        and the second the filters
        """
        return (self.requirements, self.filters)
    
    def save_parameter(self, parameter, value):
        """
        Saves a parameters in the correct data dictionnary, if it is a valid parameter
        """
        target = None
        if Reader.is_requirement(parameter):
            target = self.requirements
        elif Reader.is_filter(parameter):
            target = self.filters
        else:
            self.add_error(
                "Given parameter is not recognized, got ",
                parameter
            )
            return
        if parameter in target.keys():
            self.add_error(
                "Given parameter was already specified, old value is not overwriten ",
                (parameter, target[parameter])
            )
            return
        target[parameter] = value
    
    def validation(self):
        """
        Performs some final verification and operations to ensure that parameters are sufficient to launch execution
        """
        given_requirements = self.requirements.keys()
        #given_requirements is included is requirements_list. Thus if lenth is equal, sets are equals
        if len(given_requirements) != len(requirements_list): 
            self.valid = False
            #missing requirements
            #missing = requirements_list - given_requirements #-from vscode debug helper: cannot use the minus operator (-) between a list and dict_keys. 
            missing = set(requirements_list) - set(given_requirements)
            self.add_error(
                "Not all requirements are specified, missing ",
                missing
            )
        for key in filters_default:
            if not (key in self.filters.keys()):
                self.filters[key] = filters_default[key]

    def add_error(self, msg : str, arg):
        """
        Adds an error to the list of errors with line number, explicit error message and additionnal infos
        """
        self.errors.append("[line " + str(self.line_number) + "] " + msg + str(arg))

    def get_errors(self) -> list[str]:
        """
        Returns the list of all errors the reader ran into during the file reading
        """
        return self.errors
    
    def is_valid(self) -> bool:
        """
        Indicates if the retrieved data is sufficient to launch the program, despite some errors the reader may have encounter
        """
        return self.valid
