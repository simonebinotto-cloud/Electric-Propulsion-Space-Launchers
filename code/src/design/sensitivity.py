from src.design.design import Designer
from src.interface.termcolor import print_termcolor
from src.interface.writer import write_sensitivity 

# condition to check if matlobplotmatplotlib is avaible.
#if not, the plotting section is skipped, thus snuring the program runs without crashing if the lib is not installed.

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

def run_sensitivity(requirements, filters):
    print_termcolor("\n------ Sensitivity Analysis ------\n", "blue")
    

    #check what type of objective main calculation did. // cal main fnc to get base results and params.

    obj = int(filters["objective"])
    if obj == 0: obj_label = "Total Mass"
    elif obj == 1: obj_label = "Trip Time"
    elif obj == 2: obj_label = "ISP"
    else: return

    base_designer = Designer(requirements, filters)
    base_designer.design()
    
    if obj == 0: base_value = base_designer.total_mass
    elif obj == 1: base_value = base_designer.trip_time
    elif obj == 2: base_value = base_designer.isp
        
    print(f"Objective: {obj_label} | Reference Result: {base_value:.2f}\n")

    #section to stablish the parameters to test the variation effect

    testing_parameters = {
        "deltav": "req", "payload_mass": "req", "max_power": "fil",
        "max_duration": "fil", "min_thrust": "fil"
    }

    #for the first version, a full sweep loop is done from -20% variation to 20% variation, in 1% steps. This computes data to solve the Sensitiv. index S and to later polot the graphs in the window.
    #this is done by calling the main design function, feeding the desired variation to each step, computed over the original input parameters.
    #this is the main core logic for the sensitivy analysys. For each percent variatn, we get the new objetive (as relative change). this allows to compute S.)~ absolute values are computed later if necessary;

    delta_pct_range = list(range(-20, 21))
    sensitivity_results = {}

    for param_name, param_type in testing_parameters.items():
        impact_res = {} 
        for step in delta_pct_range:
            if step == 0:
                impact_res[step] = 0.0 
                continue
                
            decimal_step = step / 100.0
            test_reqs = requirements.copy()
            test_filters = filters.copy()
            
            if param_type == "req": test_reqs[param_name] *= (1.0 + decimal_step)
            else: test_filters[param_name] *= (1.0 + decimal_step)

            try:
                test_designer = Designer(test_reqs, test_filters)
                test_designer.design()
                
                if obj == 0: test_value = test_designer.total_mass
                elif obj == 1: test_value = test_designer.trip_time
                elif obj == 2: test_value = test_designer.isp
                    
                impact_res[step] = ((test_value - base_value) / base_value) * 100
            except ValueError:
                impact_res[step] = None 
                
        sensitivity_results[param_name] = impact_res

    #this section below is purely to pritn on terminal relevant data and to ask the user about further actins such as export, view the pltos, save the plot as png,e tc.
    
    print_termcolor("------ About Sensitivity Analysis ------\n", "yellow")
    print_termcolor("Method: Local Sensitivity Analysis (Local Derivative + One-Factor-at-a-Time).\n", "yellow")
    print_termcolor("The Normalized Sensitivity Index [S] measures the relative change", "yellow")
    print_termcolor("of our objective compared to each parameter change:", "yellow")
    
    print_termcolor("\n          % Variation in Objective", "yellow")
    print_termcolor("    S = ---------------------------", "yellow")
    print_termcolor("          % Variation in Parameter\n", "yellow")
    
    print_termcolor("Note: Because this problem is non-linear, [S] can't be assumed constant.", "yellow")
    print_termcolor("It depends on which degree of parameter variation is assumed. [S] is shown below for:", "yellow")
    print_termcolor(" • ±1%: Captures the local sensitivity to changes around the base result.", "yellow")
    print_termcolor(" • ±5%: Captures the objetive response further than base results.", "yellow")
    
    print_termcolor("\nComparing these four results, a simple picture of the non-linearity evolution", "yellow")
    print_termcolor("to parameters change in both directions is possible.", "yellow")
    print_termcolor("A full visualization for (±20% range) is available in the plot window.", "yellow")
    
    print_termcolor("\n------ Normalized Sensitivity Index [S] ------", "green")

    header = f"| {'Parameter':<15} | {'S (at -1%)':<10} | {'S (at +1%)':<10} | {'S (at -5%)':<10} | {'S (at +5%)':<10} |"
    separator = "-" * len(header)
    print_termcolor(separator, "green"); print_termcolor(header, "green"); print_termcolor(separator, "green")
    
    def get_s_str(data, step):
        val = data.get(step)
        return f"{val/step:+10.3f}" if val is not None else "N/D"

    for p_name, data in sensitivity_results.items():
        print(f"| {p_name:<15} | {get_s_str(data, -1)} | {get_s_str(data, 1)} | {get_s_str(data, -5)} | {get_s_str(data, 5)} |")
    print_termcolor(separator + "\n", "green")

    print_termcolor(f"------ Absolute {obj_label} Values at ±5% Variation ------", "cyan")
    header_abs = f"| {'Parameter':<15} | {obj_label + ' at -5%':<15} | {'Reference Result':<15} | {obj_label + ' at +5%':<15} |"
    separator_abs = "-" * len(header_abs)
    
    print_termcolor(separator_abs, "cyan"); print_termcolor(header_abs, "cyan"); print_termcolor(separator_abs, "cyan")

    def get_abs_str(data, step):
        val = data.get(step)
        return f"{base_value * (1 + val/100):>15.2f}" if val is not None else f"{'N/D':>15}"

    for p_name, data in sensitivity_results.items():
        print(f"| {p_name:<15} | {get_abs_str(data, -5)} | {base_value:>15.2f} | {get_abs_str(data, 5)} |")
        
    print_termcolor(separator_abs + "\n", "cyan")

    print_termcolor(f"------ Propellant Comparison ------ [{obj_label} / %] ------\n", "magenta")
    prop_labels = {0: "Xenon (Xe)", 1: "Krypton (Kr)", 2: "Iodine (I)"}
    base_prop = int(filters.get("propellant", 0))
    
    propellant_results = []
    
    for pid, pname in prop_labels.items():
        if pid == base_prop: continue
        f_p = filters.copy(); f_p["propellant"] = pid
        try:
            d_p = Designer(requirements, f_p); d_p.design()
            v_p = d_p.total_mass if obj==0 else (d_p.trip_time if obj==1 else d_p.isp)
            diff = ((v_p - base_value) / base_value) * 100
            print(f" -> {pname}: {v_p:.2f} ({diff:+.2f}%)")
            propellant_results.append({"name": pname, "val": v_p, "diff": diff})
        except ValueError: 
            print(f" -> {pname}: FAILED")
            propellant_results.append({"name": pname, "val": None, "diff": None})
    print_termcolor("------------------------------------------\n", "magenta")

    if input("Export sensitivity report as .TXT file? (y/n): ").lower() in ['y', 's']:
        filename_txt = input("Please specify the path of output file: ")
        
        report_writerdy = {
            "obj_label": obj_label,
            "base_value": base_value,
            "sensitivity_results": sensitivity_results,
            "propellants": propellant_results
        }

        success, result_msg = write_sensitivity(filename_txt, report_writerdy)
        
        if success:
            print_termcolor(f"Report saved successfully as {result_msg}!\n", "green")
        else:
            print_termcolor(f"Failed to save report: {result_msg}\n", "red")

    # optional section using external lib: matplotlib. If the lib is not available, the program skips so it can run on machines without the library.
    if not MATPLOTLIB_AVAILABLE:
        print_termcolor("matplotlib not installed. plot viewing not available", "red")
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        for p_name, data in sensitivity_results.items():
            x_vals = [v for v in delta_pct_range if data.get(v) is not None]
            y_vals = [data[v] for v in delta_pct_range if data.get(v) is not None]
            if x_vals: ax1.plot(x_vals, y_vals, label=p_name, linewidth=2)
                
        ax1.set_title(f"Parameter Variation Influence over {obj_label}", fontweight='bold')
        ax1.set_xlabel("Input Parameter Variation (%)")
        ax1.set_ylabel(f"Variation in {obj_label} (%)")
        ax1.axhline(0, color='black', linewidth=1); ax1.axvline(0, color='black', linewidth=1)
        ax1.grid(True, alpha=0.3); ax1.legend(loc='best')

        valid_params = []
        for p_name, data in sensitivity_results.items():
            if data.get(-5) is not None and data.get(5) is not None:
                amplitude = abs(data[5] - data[-5])
                if amplitude > 1e-6:
                    valid_params.append((p_name, data[-5], data[5], amplitude))
                    
        valid_params.sort(key=lambda x: x[3])
        labels = [x[0] for x in valid_params]
        y_pos = range(len(labels))
        
        ax2.barh(y_pos, [x[1] for x in valid_params], color='tab:blue', label='Parameter change: -5%')
        ax2.barh(y_pos, [x[2] for x in valid_params], color='tab:orange', label='Parameter change: +5%')
        ax2.set_yticks(y_pos); ax2.set_yticklabels(labels)
        ax2.set_title(f"Tornado Diagram: {obj_label} variation", fontweight='bold')
        ax2.set_xlabel(f"Variation in {obj_label} (%)")
        ax2.axvline(0, color='black', linewidth=1)
        ax2.grid(axis='x', alpha=0.3); ax2.legend(loc='best')
        plt.tight_layout()
        
        show_plots = input("\nDisplay plots in floating window? (y/n): ").lower() in ['y', 's']
        export_plots = input("Export plot results as .PNG file? (y/n): ").lower() in ['y', 's']

        if export_plots:
            filename_png = input("Please specify the path of output file: ")
            if not filename_png.endswith(".png"):
                filename_png += ".png"
            
            plt.savefig(filename_png, dpi=300, bbox_inches='tight')
            print_termcolor(f"Plot saved successfully as {filename_png}!\n", "green")
            
        if show_plots:
            plt.show()

    print_termcolor("\n--- End of Sensitivity Analysis ---", "blue")