Title: Combined LUT Hall-Sensor Calibration and MTPA Control for BLDC Drives

Abstract
Brushless DC (BLDC) drives with misaligned Hall sensors and large stator inductance suffer efficiency loss and torque ripple. We combine a lookup-table (LUT) based Hall-sensor calibration with a maximum-torque-per-ampere (MTPA) PI controller that compensates the commutation advance angle. A calibration stage records conduction-interval corrections into a LUT; runtime blends the LUT correction with an MTPA PI loop that drives the average d-axis current to zero. Simulations and experiments on an industrial BLDC show improved torque-per-ampere and transient response versus averaging-filter-only and uncompensated baselines.

I. Introduction
- Misaligned Hall sensors cause uneven 120° conduction intervals, torque ripple, and rotor-angle estimation errors. Large winding time constants further delay phase currents, breaking MTPA alignment.
- Prior work: (1) MTPA PI that adjusts the advance firing angle v to force the averaged d-axis current dsi → 0; (2) Averaging filters to balance Hall intervals, and a two-stage LUT method that removes filter delay after calibration.
- Contribution: unify the LUT calibration with the MTPA PI loop so that Hall timing is corrected without filter-induced delay while current-phase alignment is restored online.

II. BLDC Model (round-rotor PMSM, sinusoidal back-EMF)
Parks transform:
    f_qd = K_r * f_abc ,  K_r = [[cos θ_r, cos(θ_r-2π/3), cos(θ_r+2π/3)],
                                [2/3 sin θ_r, 2/3 sin(θ_r-2π/3), 2/3 sin(θ_r+2π/3)]]
Voltage equations:
    v_q = R_s i_q + L_s di_q/dt + ω_r L_s i_d + ω_r ψ_m
    v_d = R_s i_d + L_s di_d/dt - ω_r L_s i_q
Electromagnetic torque (P poles):
    T_e = 3P/4 · ψ_m · i_q
For round rotor, i_d only adds loss; MTPA target is i_d,avg = 0 under six-step 120° commutation.

III. LUT Hall-Sensor Calibration
Define n as the nth conduction interval; the next commutation time is
    t_out[n+1] = t_int[n] + Δt_corr[n]                           (1)
Three- and six-step averaging filters (from prior work) generate Δt_corr[n]:
    Δt_corr[n] = (1/3)(2Δt[n-1] + Δt[n-2] - Δt[n-3])            (2a)
    Δt_corr[n] = (1/6)(Δt[n-1]+3Δt[n-2]+4Δt[n-3]-Δt[n-4]-n-5)   (2b)  (6-step example)
Calibration mode (steady speed ω_o): convert time correction to angle
    δθ_corr = ω_o · Δt_corr                                     (3)
Store δθ_corr for each Hall state in a 6-entry LUT: LUT[state] = δθ_corr,state.
Runtime reconstruction (filter-free):
    Δt_corr,LUT = δθ_corr / ω̂_r                                (4)
    t_out[n+1] = t_int[n] + Δt_corr,LUT                         (5)
This removes filter memory/delay and permits near-instant activation after one conduction interval.

IV. MTPA PI Controller (advance-angle compensation)
Compute instantaneous and averaged d-axis current using estimated rotor angle θ̂_r from filtered Hall states:
    i_d = (2/3)(i_a sin θ̂_r + i_b sin(θ̂_r - 2π/3) + i_c sin(θ̂_r + 2π/3))      (6)
    ī_d = (1/T_sw) ∫_t^{t+T_sw} i_d(τ) dτ                                      (7)
PI loop adjusts advance angle v to enforce ī_d → 0:
    v[k] = v[k-1] + K_p (0 - ī_d[k]) + K_i ∑ (0 - ī_d)                         (8)
Effective commutation angle = 30° + v. This aligns the phase current fundamental with back-EMF, restoring MTPA despite inductance and Hall error.

V. Combined Algorithm
1) Calibration stage at a representative speed/load: run averaging filter → compute δθ_corr via (3) → populate LUT[state].
2) Runtime: 
   - Use LUT-based Δt_corr,LUT (4)–(5) to schedule software Hall transitions (balanced conduction).
   - Estimate θ̂_r via linear interpolation between LUT-corrected Hall transitions.
   - Compute ī_d via (6)–(7); update v with PI (8); add v to commutation logic.
   - Optionally refresh LUT online by re-enabling filter briefly if speed/load change significantly.

VI. Results to Target (simulation/experiment)
- Steady-state torque-per-ampere: compare uncompensated, LUT-only, MTPA-only, combined (expect highest T_e/|i| and minimal torque ripple).
- Transients: voltage-step and load-step profiles showing reduced overshoot and faster settling vs averaging-filter methods; startup with LUT active after 1 conduction interval.
- Compensation angle vs speed: v_comp (including LUT effect) vs ω_r to show >10° variation around 1000 rpm.

Figure/Graph Guide
- Block diagram: Hall signals → LUT timing correction → interpolated θ̂_r → i_d PI → advance angle v → VSI; show calibration path.
- Waveform alignment: fundamental i_a and e_a before/after combined method (demonstrate phase alignment and ripple reduction).
- Torque-per-ampere bar/line plot: rms(T_e)/|i| for four cases (none, LUT, MTPA, combined).
- Compensation angle vs speed: plot v_total(ω_r) (use eqs. 4–8; sample speeds 500–2500 rpm).
- Transient plots: (a) speed and torque for DC bus step (20→35 V); (b) speed for startup with LUT on after first interval.

Notes for DOCX Template
- Use standard IEEE sections: Abstract, Introduction, Methodology (model + LUT + MTPA), Experimental/Simulation Setup, Results, Conclusion.
- Put equations (1)–(8) inline with proper numbering; ensure symbols list (ω_r, θ̂_r, ī_d, v, δθ_corr, LUT[state]).
- When filling results, reuse data/figures from your experiments or simulations; place figure captions matching the above graph guide.
