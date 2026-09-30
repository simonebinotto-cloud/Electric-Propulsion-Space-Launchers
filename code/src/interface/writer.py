"""
It is specified in the ressources PDF that the interface shall be using text files for interface.
(cf 4.4.14)

This code thus is designed to save the program results in a given output file.
"""

from src.design.design import Designer

def write(filename, designer):
    """
    Output in given file all the design elements
    """
    
    #change: added auto .txt 
    if not filename.endswith(".txt"):
        filename += ".txt"
    
    with open(filename, "w") as file:

        file.write("## Optimal operating point:\n")
        file.write("beam_voltage: " + str(round(designer.beam_voltage, 1)) + " V\n")
        file.write("beam_current: " + str(round(designer.beam_current, 3)) + " A\n")
        file.write("isp: " + str(round(designer.isp, 0)) + " s\n")
        file.write("thrust: " + str(round(designer.thrust, 3)) + " mN\n")
        file.write("eta_T: " + str(round(designer.eta_T * 100, 1)) + " %\n")
        file.write("electrical_power: " + str(round(designer.electrical_power, 1)) + " W\n")
        file.write("discharge_power: " + str(round(designer.discharge_power, 1)) + " W\n")
        file.write("epsilon_d: " + str(round(designer.epsilon_d, 1)) + " eV/ion\n")

        file.write("\n## Mass budget:\n")
        file.write("motor_mass: " + str(round(designer.motor_mass, 3)) + " kg\n")
        file.write("propellant_mass: " + str(round(designer.propellant_mass, 3)) + " kg\n")
        file.write("total_mass: " + str(round(designer.total_mass, 3)) + " kg\n")

        file.write("\n## Mission:\n")
        file.write("trip_time: " + str(round(designer.trip_time, 1)) + " h\n")
        file.write("trip_time_days: " + str(round(designer.trip_time / 24, 1)) + " days\n")

        throttle_points = sorted(designer.sweep_results, key=lambda r: r["thrust"])

        file.write("\n## Throttle table:\n")
        file.write("# {:<8}{:<8}{:<10}{:<10}{:<10}{:<10}{:<12}{:<12}\n".format(
            "Vb(V)", "Ib(A)", "T(mN)", "Isp(s)", "Pin(W)", "eta_T(%)", "mp(kg)", "t(days)"))
        for r in throttle_points:
            file.write("{:<8}{:<8}{:<10}{:<10}{:<10}{:<10}{:<12}{:<12}\n".format(
                round(r["V_b"], 0), round(r["I_b"], 3), round(r["thrust"], 2),
                round(r["isp"], 0), round(r["electrical_power"], 1),
                round(r["eta_T"] * 100, 1), round(r["propellant_mass"], 3),
                round(r["trip_time"] / 24, 1)))

        file.write("\n## Full sweep (V_b, I_b space):\n")
        file.write("# {:<8}{:<8}{:<10}{:<10}{:<12}{:<12}\n".format(
            "Vb(V)", "Ib(A)", "T(mN)", "Isp(s)", "TotMass(kg)", "t(days)"))
        for r in designer.sweep_results:
            file.write("{:<8}{:<8}{:<10}{:<10}{:<12}{:<12}\n".format(
                round(r["V_b"], 0), round(r["I_b"], 3), round(r["thrust"], 2),
                round(r["isp"], 0), round(r["total_mass"], 2),
                round(r["trip_time"] / 24, 1)))


#function to write the sensivity report. not using objects atm since, so i ahve to pass more stuff into the expected inputs

def write_sensitivity(filename: str, report: dict) -> tuple[bool, str]:
    """
    Output the sensitivity analysis report in text file, separate from the main results for enhanced clarity and to differentiate from the main project objetive.
    The structure tries to mimic the original structure of the code above.
    
    """
    if not filename.endswith(".txt"):
        filename += ".txt"
        
    try:
        with open(filename, "w", encoding="utf-8") as f:
            base_val = report["base_value"]
            sens_res = report["sensitivity_results"]
            

            def format_s(data, step):
                val = data.get(step)
                return f"{val/step:+.3f}" if val is not None else "N/D"

            def format_abs(data, step):
                val = data.get(step)
                return f"{base_val * (1 + val/100):.2f}" if val is not None else "N/D"

            f.write("## Sensitivity Analysis:\n")
            f.write(f"objective: {report['obj_label']}\n")
            f.write(f"base_value: {base_val:.3f}\n\n")
            
            f.write("## Normalized Sensitivity Index (S):\n")
            f.write(f"# {'Parameter':<15}{'S(-1%)':<12}{'S(+1%)':<12}{'S(-5%)':<12}{'S(+5%)':<12}\n")
            for p_name, data in sens_res.items():
                f.write(f"{p_name:<15}{format_s(data, -1):<12}{format_s(data, 1):<12}{format_s(data, -5):<12}{format_s(data, 5):<12}\n")

            f.write("\n## Absolute Values at +/- 5% Variation:\n")
            f.write(f"# {'Parameter':<15}{'Obj (-5%)':<15}{'Base':<15}{'Obj (+5%)':<15}\n")
            for p_name, data in sens_res.items():
                f.write(f"{p_name:<15}{format_abs(data, -5):<15}{base_val:<15.2f}{format_abs(data, 5):<15}\n")

            if report.get("propellants"):
                f.write("\n## Propellant Comparison:\n")
                f.write(f"# {'Propellant':<15}{'Obj':<15}{'Diff(%)':<15}\n")
                for prop in report["propellants"]:
                    val_str = f"{prop['val']:.2f}" if prop['val'] is not None else "Err."
                    diff_str = f"{prop['diff']:.2f}" if prop['diff'] is not None else "N/D"
                    f.write(f"{prop['name']:<15}{val_str:<15}{diff_str:<15}\n")

            f.write("\n## Full Sweep results (Objective Variation in %):\n")
            params = list(sens_res.keys())
            
            # Dynamic header
            header = f"# {'Variation(%)':<15}"
            for p in params:
                header += f"{p:<16}"
            f.write(header + "\n")
            
            if params:
                for step in sorted(sens_res[params[0]].keys()):
                    line = f"  {step:+d}%".ljust(15)
                    for p in params:
                        val = sens_res[p].get(step)
                        if val is not None:
                            line += f"{f'{val:+.3f}':<16}" 
                        else:
                            line += f"{'Err.':<16}"
                    f.write(line + "\n")

        return True, filename
    except Exception as e:
        return False, str(e)