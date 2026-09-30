# Electric Propulsion Systems & Ion Thruster Sizing Tool

This repository contains the project report, mathematical models, and a custom **Python optimization tool** developed for the **Lançadores Espaciais (Space Launchers)** course at **Instituto Superior Técnico, Universidade de Lisboa** (Academic Year 2025/2026).

## 📌 Project Overview

The project provides a comparative analysis of five main electric propulsion technologies across physical principles, performance metrics, and application trade-offs:

1. **Electrothermal:** Resistojets & Arcjets

2. **Electrostatic:** Gridded Ion Thrusters

3. **Electromagnetic:** Hall-Effect Thrusters (HET) & Pulsed Plasma Thrusters (PPT)

### Key Features

* Comprehensive review of specific impulse ($I_{sp}$), thrust range, power requirements, and efficiency trade-offs.

* **Sizing & Optimization Software:** A dedicated Python tool designed to size and optimize an **Ion Thruster** based on user-defined mission constraints.

## 💻 Python Optimization & Sizing Software

The Python tool allows users to input spacecraft mission parameters and component constraints via a text configuration file, automatically searching for an optimal motor design (minimized for total mass) and evaluating parameter sensitivity.

### Features

* **Custom Mission Input:** Define required $\Delta v$, payload mass, power availability, component efficiencies, and thrust constraints.

* **Mass Optimization:** Computes optimal thruster geometry, grid parameters, mass utilization, and power allocation.

* **Sweep & Configuration Table:** Outputs all valid candidate engine configurations explored during search space iteration.

* **Sensitivity Analysis:** Analyzes the sensitivity of the overall system mass against mission parameters to assess trade-offs.

## 🚀 How to Run the Software

To execute the sizing and optimization tool:

1. **Clone the repository:**

   ```
   git clone https://github.com/YOUR_USERNAME/Electric-Propulsion-Space-Launchers.git
   cd Electric-Propulsion-Space-Launchers
   
   ```

2. **Configure Mission Input:**
   Edit the input configuration text file (e.g., `config.txt` or `input_mission.txt`) to specify desired payload, required $\Delta v$, and thruster parameters.

3. **Run the Python script:**
   Open and execute the main Python entry point:

   ```
   python main.py
   
   ```

   *(or open and run `main.py` directly in your Python IDE / Jupyter environment)*

4. **Review Outputs:**

   * An output summary file containing the optimized thruster parameters.

   * A configuration log detailing all explored designs.

   * Sensitivity plots and trade-off tables.

## 🛠️ Requirements

* **Python 3.8+**

* Standard scientific packages (`numpy`, `scipy`, `matplotlib`, `pandas`)

## 👥 Authors & Academic Context

Developed by **Group #5** — Lançadores Espaciais (MEAer, 1st Year)

**Instituto Superior Técnico, Universidade de Lisboa** (A.Y. 2025/2026):

* Simone Binotto

* Marco Azevedo

* Philippe Quichaud

* Corentin Ouisse

* André Matos

* Théo Demesy
