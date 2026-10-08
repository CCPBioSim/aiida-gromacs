#!/bin/bash

gmx_grompp -f MDstep_1.0_minimization.mdp -c solvated_ions.gro -r solvated_ions.gro -p system.top -o MDstep_1.0_minimization.tpr -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.0_minimization.tpr -c MDstep_1.0_minimization.gro -e MDstep_1.0_minimization.edr -g MDstep_1.0_minimization.log -o MDstep_1.0_minimization.trr


gmx_grompp -f MDstep_1.1_minimization.mdp -o MDstep_1.1_minimization.tpr -c MDstep_1.0_minimization.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.1_minimization.tpr -c MDstep_1.1_minimization.gro -e MDstep_1.0_minimization.edr -g MDstep_1.1_minimization.log -o MDstep_1.1_minimization.trr


 gmx_grompp -f MDstep_1.2_equilibration.mdp -o MDstep_1.2_equilibration.tpr -c MDstep_1.1_minimization.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.2_equilibration.tpr -c MDstep_1.2_equilibration.gro -e MDstep_1.1_minimization.edr -g MDstep_1.2_equilibration.log -o MDstep_1.2_equilibration.trr -x MDstep_1.2_equilibration.xtc


gmx_grompp -f MDstep_1.3_equilibration.mdp -o MDstep_1.3_equilibration.tpr -c MDstep_1.2_equilibration.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.3_equilibration.tpr -c MDstep_1.3_equilibration.gro -e MDstep_1.2_equilibration.edr -g MDstep_1.3_equilibration.log -o MDstep_1.3_equilibration.trr


gmx_grompp -f MDstep_1.4_equilibration.mdp -o MDstep_1.4_equilibration.tpr -c MDstep_1.3_equilibration.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.4_equilibration.tpr -c MDstep_1.4_equilibration.gro -e MDstep_1.3_equilibration.edr -g MDstep_1.4_equilibration.log -o MDstep_1.4_equilibration.trr


gmx_grompp -f MDstep_1.5_equilibration.mdp -o MDstep_1.5_equilibration.tpr -c MDstep_1.4_equilibration.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.5_equilibration.tpr -c MDstep_1.5_equilibration.gro -e MDstep_1.4_equilibration.edr -g MDstep_1.5_equilibration.log -o MDstep_1.5_equilibration.trr


gmx_grompp -f MDstep_1.6_equilibration.mdp -o MDstep_1.6_equilibration.tpr -c MDstep_1.5_equilibration.gro -r solvated_ions.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_1.6_equilibration.tpr -c MDstep_1.6_equilibration.gro -e MDstep_1.5_equilibration.edr -g MDstep_1.6_equilibration.log -o MDstep_1.6_equilibration.trr


gmx_grompp -f MDstep_2.0_production.mdp -o MDstep_2.0_production.tpr -c MDstep_1.6_equilibration.gro -p system.top -n index.ndx -maxwarn 1
gmx_mdrun -s MDstep_2.0_production.tpr -c MDstep_2.0_production.gro -e MDstep_1.6_equilibration.edr -g MDstep_2.0_production.log -o MDstep_2.0_production.trr

