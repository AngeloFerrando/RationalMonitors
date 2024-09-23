# RationalMonitors

This repository contains an implementation of **rational monitors** for **Linear Temporal Logic (LTL) properties**. The goal is to generate rational multi-monitors based on given input arguments and execute them on specified traces.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Arguments](#arguments)
- [License](#license)

## Description

RationalMonitors is a Python-based tool that generates rational multi-monitors for monitoring **LTL properties**. It takes input arguments to configure the monitors and processes traces accordingly. The project is designed for researchers or practitioners interested in temporal logic and rational monitoring for reactive systems.

## Installation

To run this project locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/AngeloFerrando/RationalMonitors.git
   ```

2. Install the required dependencies. You can use `pip` to install packages listed in a `requirements.txt` file if it exists. Currently, there doesn't seem to be one, so ensure you have Python 3.x installed.

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the project dependencies are installed, and the main script is executable.

## Usage

The `main.py` script is used to generate rational multi-monitors for monitoring LTL formulas over a set of atomic propositions (APs). It monitors these formulas within a specified time window, under resource constraints. The script requires input arguments such as LTL formulas, visibility, and resource bounds.

### Required Arguments:

1. **ltl**: A string containing one or more LTL formulas separated by commas.
2. **ap**: A set of atomic propositions for the LTL formulas.
3. **visibility**: A list defining the visibility of each monitor.
4. **resource_bound**: An integer specifying the resource limit for the monitoring.
5. **time_window**: An integer representing the time window for monitoring.
6. **filename**: The file containing the trace of events to be monitored.

### Example Argument Format:

- `ltl`: `"G(p -> Fq), G(q -> Fr)"` (two LTL formulas)
- `ap`: `"[p, q, r]"` (atomic propositions)
- `visibility`: `"[p, r], [q]"` (defining what each monitor can "see")
- `resource_bound`: `10` (resource bound for knapsack problem)
- `time_window`: `5` (monitor over a 5-time-step window)
- `filename`: `"trace1.txt"` (input trace file)

## Example

Below is an example command for running the `main.py` script:

```bash
python main.py "G(p -> Fq),G(q -> Fr)" "[p, q, r]" "[p], [q]" 10 5 trace1.txt
```

### Input Details:

- **LTL Formula**: `"G(p -> Fq), G(q -> Fr)"` – This formula monitors for the eventual truth of `q` and `r` after `p` and `q`, respectively.
- **Atomic Propositions**: `[p, q, r]` – These are the atomic propositions involved in the formulas.
- **Visibility**: `[p], [q]` – Each monitor only has partial visibility: one sees `p`, the other sees `q`.
- **Resource Bound**: `10.0` – The resource constraint for monitoring.
- **Time Window**: `5` – The number of time steps over which monitoring is performed.
- **Trace File**: The events to be monitored are contained in `trace1.txt`.

### Trace File Format:

The trace file (e.g., `trace1.txt`) should consist of a sequence of events, with each line representing a set of propositions that are true at a specific time step. Example:

```
p, q
q
p, r
```

This file would represent a sequence of events where both `p` and `q` are true at the first time step, only `q` is true at the second time step, and `p` and `r` are true at the third time step.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
