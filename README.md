## Disclaimer
This python project is part of my (Yannick Wiest) Bachelorthesis 
"From Monthly to Daily: Analyzing the Effect of Data Frequency on Portfolio Strategy Performances".
For any questions, please contact yannick.wiest@tum.de.

I acknowledge, that I used ChatGPT to enhance the performance of this code.
I want to emphasize, that I did NOT use it to come up with the solution itself.
It was used solely to generate a syntactically improved version of the code to 
ensure fast computation of the results, so the end user does not have to wait long.
I achieved a speedup of around 4x with that, mainly through vectorization.

## Installation
To run this script please first install the modules specified in
requirements.txt. I suggest doing this in a venv to ensure proper setup.
The project was written in Python 3.12.

Also, a GUROBI solver license needs to be properly installed on the
system.  
A license can be obtained here:  
https://www.gurobi.com/academia/academic-program-and-licenses/  
To do this, use eduVPN as described here:  
https://doku.lrz.de/vpn-eduvpn-konfiguration-fuer-tum-11497326.html  
Important: Use "Sicheres Internet" instead of "Zugang zum Institut".

## Tutorial
There are two files that can be executed.

main.py:  
This allows the user to run the analysis while using one dataset only.
This means using either monthly data & rebalancing or
daily data & rebalancing.

main_monthly_daily.py:  
This allows the user to tun the analysis for daily data & monthly rebalancing.