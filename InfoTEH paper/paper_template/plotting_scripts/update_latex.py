
fn = r"d:\Repository\ELEC_499B\InfoTEH paper\paper_template\latex\IEEE-conference-template-062824.tex"
new_content = r"""\section{Detailed Machine Simulations}
\label{sec:simulation}

The proposed Look-Up Table (LUT) based control strategy is verified using a detailed Simulink simulation of a typical industrial Brushless DC (BLDC) motor. The motor parameters are summarized in Appendix A. This section analyzes the steady-state efficiency and dynamic performance of the proposed method compared to conventional Hall-sensor control techniques.

\subsection{Control Stages and Current Transients}
The operation of the proposed control scheme evolves through distinct stages to achieve optimal performance, as illustrated in Fig.~\ref{fig:current_transient}.
Initially, in the \textbf{Uncompensated} stage, the Hall-sensor misalignment causes uneven commutation intervals, resulting in significant distortions in the phase current ($i_{as}$) and large low-frequency oscillations in the synchronous frame $d$-axis current ($i_{ds}$).
When the calibration is activated (labeled \textbf{LUT Only}), the LUT-based correction equalizes the switching intervals. As seen in the middle section of Fig.~\ref{fig:current_transient}(a) and (b), this eliminates the heavy firing angle oscillations, stabilizing the current waveforms. However, a static phase shift remains due to the inherent delay of the position calculation or physical sensor offset.
Finally, the \textbf{MTPA} control loop is enabled. This stage adjusts the commutation angle to drive the average $d$-axis current ($\bar{i}_{ds}$) to zero. As shown in the right section, the $i_{ds}$ oscillation is suppressed, and the average value settles at zero, ensuring Maximum Torque per Ampere (MTPA) operation.

\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{figures/current_transient_stacked_inset.png}}
\caption{Evolution of phase current ($i_{as}$) and $d$-axis current ($i_{ds}$) through control stages: Uncompensated, LUT/Filter Only, and LUT + MTPA.}
\label{fig:current_transient}
\end{figure}

\subsection{Phase Alignment Verification}
The correction of the phase misalignment is explicitly verified in Fig.~\ref{fig:phase_alignment}.
In the \textbf{Uncompensated} case (a), there is a significant phase lag between the fundamental component of the phase current ($i_{as}^{fund}$) and the Back-EMF ($e_{as}$), leading to inefficient torque production.
Applying the \textbf{LUT Correction} (b) addresses the commutation inequality but may still leave a residual phase error ($\Delta \phi$).
The effect of the combined \textbf{LUT + MTPA} strategy is evident in (c), where the phase current is perfectly aligned with the Back-EMF. This alignment confirms that the resistive torque is minimized and the electromagnetic torque generation is maximized for the given current.

\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{figures/1_phase_alignment.png}}
\caption{Phase alignment comparison: (a) Uncompensated, (b) LUT Only, and (c) LUT + MTPA. The proposed method (c) achieves near-perfect alignment between current and Back-EMF.}
\label{fig:phase_alignment}
\end{figure}

\subsection{Torque Efficiency}
The improvement in energy conversion efficiency is quantified by the Torque Constant ($K_t$), defined here as the ratio of average electromagnetic torque to the RMS phase current ($T_{e,avg} / I_{rms}$).
Figure~\ref{fig:tpa_comparison} presents the steady-state $K_t$ for the different operating modes. The uncompensated operation yields the lowest torque-per-ampere ratio due to the misaligned current vector. The LUT Correction provides a marginal improvement, but the combined \textbf{LUT + MTPA} strategy achieves the highest $K_t$, demonstrating that the proposed method effectively extracts the maximum possible torque from the machine winding.

\begin{figure}[htbp]
\centerline{\includegraphics[width=0.8\columnwidth]{figures/2_tpa_comparison.png}}
\caption{Comparison of Torque Constant ($K_t$) across control strategies. The proposed LUT + MTPA method maximizes the torque-per-ampere ratio.}
\label{fig:tpa_comparison}
\end{figure}

\subsection{Transient Analysis}
The dynamic robustness of the proposed method is evaluated under startup and load disturbance conditions.

\subsubsection{Startup Response}
Figure~\ref{fig:startup} compares the rotor speed startup transient from standstill to steady state. The proposed LUT method (Red/Orange) tracks the "No Misalignment" ideal reference (Black dashed) very closely, exhibiting a fast rise time and minimal overshoot. In contrast, the conventional 3-step and 6-step averaging filters introduce computation delays, resulting in a slower response and noticeable oscillations during the speed ramp-up.

\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{figures/3_startup.png}}
\caption{Rotor speed startup transient comparison (0-200ms). The proposed LUT method closely tracks the ideal reference with minimal delay.}
\label{fig:startup}
\end{figure}

\subsubsection{Load Step Response}
The system's response to a sudden load torque step is shown in Fig.~\ref{fig:torque_step}. At $t \approx 1.0$s, a nominal load is applied.
The electrical speed ($\omega_e$) drops momentarily before recovering. The proposed LUT method demonstrates a recovery profile similar to the filtered methods but with visibly reduced high-frequency ripple in the electromagnetic torque ($T_e$) (bottom plot) compared to the 3-step averaging method. This confirms that the LUT strategy maintains the high dynamic bandwidth of the Hall sensors while effectively rejecting the misalignment-induced disturbances.

\begin{figure}[htbp]
\centerline{\includegraphics[width=\columnwidth]{figures/4_torque_step.png}}
\caption{System response to a load torque step. Top: Electrical speed drop and recovery. Bottom: Electromagnetic torque response showing stable disturbance rejection.}
\label{fig:torque_step}
\end{figure}
"""

with open(fn, 'r') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if r"\section{Detailed Machine Simulations}" in line:
        start_idx = i
        break

for i in range(len(lines)-1, -1, -1):
    if r"\begin{thebibliography}" in lines[i]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    print(f"Replacing lines {start_idx+1} to {end_idx}")
    # Keep start and end section? 
    # Logic: Replace everything from Start Section header UP TO (but not including) Bibliography
    final_lines = lines[:start_idx] + [new_content + "\n\n"] + lines[end_idx:]
    
    with open(fn, 'w') as f:
        f.writelines(final_lines)
    print("Success")
else:
    print(f"Could not find markers. Start: {start_idx}, End: {end_idx}")
