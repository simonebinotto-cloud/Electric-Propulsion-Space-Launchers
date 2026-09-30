##########################################
#
# Name: Ion Thruster Preliminary Design Tool
# Curent version: 1.3
# Authors: Simone Binotto, Marco Azevedo, Philippe Quichaud, Corentin Ouisse, Andre Matosa, Theo Demesy
# Initial coding: 02/03/26
# Description: A sweep search that calculates optimal ion thruster design in the (V_b, I_b) space and performs sensitivity analysis
# Used algorithms: All code was created by the authors. Scaling laws are sourced form Goebel & Katz, 2008
# Sensitivity analysis logic: Evaluated using a simple local derivative approach. Different parameters influence evaluated independently using One-Factor-at-a-Time method. Looped for [+-20%] parameter influence range.
# Inputs and outputs: cf. README file to have the full descriptions of all the inputs and outputs and some examples
# Dependencies: Matplotlib (the program can run without, but sensitivity analysis has a graphical component)
# Framework: Python3
# Last version changes:
# - version 1.3 : Added sensitivity analysis
# - version 1.2 : Implemented (Vb, Ib) space sweep
# - version 1.1 : Implemented an iterative motor design with scaling laws
# - version 1.0 : Implemented User Interface
#########################################

from src.interface.reader import Reader
from src.interface.termcolor import print_termcolor
from src.design.design import Designer
from src.interface.writer import write
from src.design.sensitivity import run_sensitivity


#getting the path
print("Please specify the path of parameters file")
filename = input()

#launching the read
print_termcolor("Reading file...", "blue")
reader = Reader(filename)

#error management
errors_list = reader.get_errors()

if len(errors_list) == 0:
    print_termcolor("No errors were detected", "green")
else:
    print_termcolor(str(len(errors_list)) + " errors were encountered:", "red")
    for error in errors_list:
        print(error)
    print()
    if reader.is_valid():
        print("The program indicates that despite encountered errors, it has sufficient data to launch")
        proceed = input("Do you want to proceed? (y/n) ")
        if not (proceed in ['y', 'Y']):
            exit()
    else:
        print("The program is unable to launch")
        exit()

#data retrieval
requirements, filters = reader.get_parameters()

#main program run
print_termcolor("Executing the program...", "blue")

designer = Designer(requirements, filters)

try:
    designer.design()
except ValueError as e:
    print_termcolor("An unexpected error has occured:", "red")
    print(e.args)
    print_termcolor("Closing program without results", "red")
    exit()

print_termcolor("The design has been successfully carried out", "green")

print("Please specify the path of output file")
filename = input()

#data save
print_termcolor("Saving results", "blue")
write(filename, designer)

#optional sensitivy analysis

print_termcolor("Do you want to run optional sensitivity analysis? (y/n)", "green")

if input().lower() in ['y', 'Y']:
    run_sensitivity(requirements, filters)

#end
print_termcolor("The program has concluded", "blue")