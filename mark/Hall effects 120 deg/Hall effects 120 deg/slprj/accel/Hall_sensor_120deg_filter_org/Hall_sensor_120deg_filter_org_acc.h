#ifndef Hall_sensor_120deg_filter_org_acc_h_
#define Hall_sensor_120deg_filter_org_acc_h_
#ifndef Hall_sensor_120deg_filter_org_acc_COMMON_INCLUDES_
#define Hall_sensor_120deg_filter_org_acc_COMMON_INCLUDES_
#include <stdlib.h>
#define S_FUNCTION_NAME simulink_only_sfcn
#define S_FUNCTION_LEVEL 2
#ifndef RTW_GENERATED_S_FUNCTION
#define RTW_GENERATED_S_FUNCTION
#endif
#include "sl_AsyncioQueue/AsyncioQueueCAPI.h"
#include "rtwtypes.h"
#include "simstruc.h"
#include "fixedpoint.h"
#include "rt_nonfinite.h"
#include "math.h"
#endif
#include "Hall_sensor_120deg_filter_org_acc_types.h"
#include <stddef.h>
#include "rt_defines.h"
#include "simstruc_types.h"
typedef struct { real_T B_25_0_0 ; real_T B_25_1_8 ; real_T B_25_2_16 ;
real_T B_25_3_24 ; real_T B_25_4_32 ; real_T B_25_5_40 [ 15 ] ; real_T
B_25_20_160 [ 12 ] ; real_T B_25_32_256 ; real_T B_25_33_264 ; real_T
B_25_34_272 ; real_T B_25_35_280 ; real_T B_25_36_288 ; real_T B_25_37_296 ;
real_T B_25_38_304 ; real_T B_25_39_312 ; real_T B_25_40_320 ; real_T
B_25_41_328 ; real_T B_25_42_336 ; real_T B_25_43_344 ; real_T B_25_44_352 ;
real_T B_25_45_360 ; real_T B_25_46_368 ; real_T B_25_47_376 ; real_T
B_25_48_384 ; real_T B_25_49_392 ; real_T B_25_50_400 ; real_T B_25_51_408 ;
real_T B_25_52_416 ; real_T B_25_53_424 ; real_T B_25_54_432 ; real_T
B_25_55_440 ; real_T B_25_56_448 ; real_T B_25_57_456 ; real_T B_25_58_464 ;
real_T B_25_59_472 ; real_T B_25_60_480 ; real_T B_25_61_488 ; real_T
B_25_62_496 ; real_T B_25_63_504 ; real_T B_25_64_512 ; real_T B_25_65_520 ;
real_T B_25_66_528 ; real_T B_25_67_536 ; real_T B_25_68_544 ; real_T
B_25_69_552 ; real_T B_25_70_560 ; real_T B_25_71_568 ; real_T B_25_72_576 ;
real_T B_25_73_584 ; real_T B_25_74_592 ; real_T B_25_75_600 ; real_T
B_25_76_608 [ 12 ] ; real_T B_25_88_704 ; real_T B_25_89_712 [ 3 ] ; real_T
B_25_92_736 ; real_T B_25_93_744 ; real_T B_25_94_752 ; real_T B_25_95_760 ;
real_T B_25_96_768 ; real_T B_25_97_776 ; real_T B_25_98_784 ; real_T
B_25_99_792 ; real_T B_25_100_800 ; real_T B_25_101_808 ; real_T B_25_102_816
[ 3 ] ; real_T B_25_105_840 ; real_T B_25_106_848 ; real_T B_25_107_856 ;
real_T B_25_108_864 ; real_T B_25_109_872 ; real_T B_25_110_880 ; real_T
B_25_111_888 ; real_T B_25_112_896 ; real_T B_25_113_904 ; real_T
B_25_114_912 ; real_T B_25_115_920 ; real_T B_24_116_928 ; real_T
B_24_117_936 ; real_T B_23_118_944 ; real_T B_23_119_952 ; real_T
B_23_120_960 ; real_T B_21_121_968 ; real_T B_21_122_976 ; real_T
B_21_123_984 ; real_T B_21_124_992 ; real_T B_21_125_1000 ; real_T
B_21_126_1008 ; real_T B_20_127_1016 ; real_T B_19_128_1024 ; real_T
B_19_129_1032 ; real_T B_19_130_1040 ; real_T B_19_131_1048 ; real_T
B_19_132_1056 ; real_T B_19_133_1064 ; real_T B_19_134_1072 ; real_T
B_19_135_1080 ; real_T B_19_136_1088 ; real_T B_18_137_1096 [ 6 ] ; real_T
B_18_143_1144 ; real_T B_18_144_1152 ; real_T B_14_145_1160 ; real_T
B_13_146_1168 ; real_T B_12_147_1176 ; real_T B_11_148_1184 ; real_T
B_10_149_1192 ; real_T B_10_150_1200 ; real_T B_10_151_1208 ; real_T
B_9_152_1216 ; real_T B_9_153_1224 ; real_T B_9_154_1232 ; real_T
B_8_155_1240 ; real_T B_7_156_1248 [ 6 ] ; real_T B_6_162_1296 ; real_T
B_6_163_1304 ; real_T B_6_164_1312 ; real_T B_2_165_1320 ; real_T
B_1_166_1328 ; real_T B_0_167_1336 ; boolean_T B_25_168_1344 ; boolean_T
B_25_169_1345 ; boolean_T B_18_170_1346 ; boolean_T B_18_171_1347 ; char_T
pad_B_18_171_1347 [ 4 ] ; } B_Hall_sensor_120deg_filter_org_T ; typedef
struct { real_T DiscreteTimeIntegrator2_DSTATE ; real_T
DiscreteTimeIntegrator1_DSTATE ; real_T StateSpace_DSTATE ; real_T
Integrator_DSTATE ; real_T Filter_DSTATE ; real_T
DiscreteTimeIntegrator1_DSTATE_n ; real_T DelayInput1_DSTATE ; real_T
UnitDelay_DSTATE ; real_T time_base ; real_T Memory_PreviousInput ; real_T
Memory_PreviousInput_d ; real_T tau_corr_now ; real_T tau_corr_next ; real_T
state_out ; real_T reset_toggle ; real_T first_time ; real_T
Memory_PreviousInput_p ; real_T Memory1_PreviousInput ; real_T
Memory2_PreviousInput ; real_T Memory3_PreviousInput ; real_T
Memory4_PreviousInput ; real_T Memory5_PreviousInput ; real_T t_now ; struct
{ real_T modelTStart ; } VariableTransportDelay_RWORK ; struct { real_T
modelTStart ; } VariableTransportDelay_RWORK_f ; void *
DataStoreMemory4_PWORK ; struct { void * AS ; void * BS ; void * CS ; void *
DS ; void * DX_COL ; void * BD_COL ; void * TMP1 ; void * TMP2 ; void * XTMP
; void * SWITCH_STATUS ; void * SWITCH_STATUS_INIT ; void * SW_CHG ; void *
G_STATE ; void * USWLAST ; void * XKM12 ; void * XKP12 ; void * XLAST ; void
* ULAST ; void * IDX_SW_CHG ; void * Y_SWITCH ; void * SWITCH_TYPES ; void *
IDX_OUT_SW ; void * SWITCH_TOPO_SAVED_IDX ; void * SWITCH_MAP ; }
StateSpace_PWORK ; struct { void * TUbufferPtrs [ 3 ] ; }
VariableTransportDelay_PWORK ; struct { void * TUbufferPtrs [ 3 ] ; }
VariableTransportDelay_PWORK_j ; struct { void * AQHandles ; }
TAQOutportLogging_InsertedFor_Gain1_at_outport_0_PWORK ; struct { void *
AQHandles ; } TAQOutportLogging_InsertedFor_ManualSwitch_at_outport_0_PWORK ;
struct { void * AQHandles ; }
TAQOutportLogging_InsertedFor_MovingAverageVariableFrequency1_at_outport_0_PWORK
; struct { void * AQHandles ; }
TAQOutportLogging_InsertedFor_MovingAverageVariableFrequency_at_outport_0_PWORK
; struct { void * AQHandles ; }
TAQOutportLogging_InsertedFor_PMSM_at_outport_1_PWORK ; struct { void *
AQHandles ; } TAQOutportLogging_InsertedFor_PMSM_at_outport_3_PWORK ; struct
{ void * AQHandles ; }
TAQOutportLogging_InsertedFor_backEMF_at_outport_0_PWORK ; struct { void *
AQHandles ; }
TAQOutportLogging_InsertedFor_converttomechspeed_at_outport_0_PWORK ; struct
{ void * AQHandles ; }
TAQOutportLogging_InsertedFor_qdframetostator_at_outport_0_PWORK ; struct {
void * AQHandles ; }
TAQOutportLogging_InsertedFor_qdframetostator_at_outport_1_PWORK ; struct {
void * AQHandles ; }
TAQOutportLogging_InsertedFor_qdframetostator_at_outport_2_PWORK ; struct {
void * AQHandles ; }
TAQSigLogging_InsertedFor_MATLABFunction2_at_outport_0_PWORK ; struct { void
* AQHandles ; } TAQSigLogging_InsertedFor_MATLABFunction_at_outport_0_PWORK ;
struct { void * AQHandles ; }
TAQSigLogging_InsertedFor_PMSM_at_outport_0_PWORK ; struct { void * AQHandles
; } TAQSigLogging_InsertedFor_PMSM_at_outport_2_PWORK ; struct { void *
AQHandles ; } TAQSigLogging_InsertedFor_Switch3_at_outport_0_PWORK ; void *
speedscope120_PWORK [ 2 ] ; void * torquescope120_PWORK [ 2 ] ; void *
Scope_PWORK ; struct { void * AQHandles ; }
TAQSigLogging_InsertedFor_DetectChange_at_outport_0_PWORK ; struct { void *
AQHandles ; } TAQSigLogging_InsertedFor_MATLABFunction1_at_outport_0_PWORK ;
struct { void * AQHandles ; }
TAQSigLogging_InsertedFor_RelationalOperator_at_outport_0_PWORK ; void *
fil_state_PWORK ; void * Scope1_PWORK ; void * Scope2_PWORK ; void *
DataStoreMemory_PWORK ; void * DataStoreMemory1_PWORK ; void *
DataStoreMemory2_PWORK ; void * DataStoreMemory3_PWORK ; void *
DataStoreMemory5_PWORK ; void * DataStoreMemory_PWORK_i ; int32_T dsmIdx ;
int32_T dsmIdx_n ; int32_T dsmIdx_h ; int32_T dsmIdx_d ; int32_T dsmIdx_m ;
int32_T dsmIdx_l ; int32_T statortoqdframe_sysIdxToRun ; int32_T
qdframetostator_sysIdxToRun ; int32_T
TmpAtomicSubsysAtSwitchInport1_sysIdxToRun ; int32_T
software_ISR_routine_sysIdxToRun ; int32_T ModulobyConstant_sysIdxToRun ;
int32_T hardware_ISR_routine_sysIdxToRun ; int32_T dsmIdx_g ; int32_T
MATLABFunction_sysIdxToRun ; int32_T AtomicSubsystem_sysIdxToRun ; int32_T
Subsystem1_sysIdxToRun ; int32_T Subsystem_sysIdxToRun ; int32_T
MATLABFunction1_sysIdxToRun ; int32_T MATLABFunction_sysIdxToRun_a ; int32_T
Firsttriggerinitialization_sysIdxToRun ; int32_T MATLABFunction_sysIdxToRun_c
; int32_T hallsensors1_sysIdxToRun ; int32_T hallsensors_sysIdxToRun ;
int32_T convertto02pi_sysIdxToRun ; int32_T controller_120_sysIdxToRun ;
int32_T backEMF_sysIdxToRun ; int32_T
TmpAtomicSubsysAtSwitch3Inport1_sysIdxToRun ; int32_T
TmpAtomicSubsysAtSwitchInport1_sysIdxToRun_p ; int32_T
TmpAtomicSubsysAtSwitchInport1_sysIdxToRun_n ; int32_T
MATLABFunction2_sysIdxToRun ; int32_T MATLABFunction1_sysIdxToRun_o ; int32_T
MATLABFunction_sysIdxToRun_e ; int_T StateSpace_IWORK [ 11 ] ; struct { int_T
Tail ; int_T Head ; int_T Last ; int_T CircularBufSize ; int_T MaxNewBufSize
; } VariableTransportDelay_IWORK ; struct { int_T Tail ; int_T Head ; int_T
Last ; int_T CircularBufSize ; int_T MaxNewBufSize ; }
VariableTransportDelay_IWORK_n ; int8_T
DiscreteTimeIntegrator1_PrevResetState ; int8_T
software_ISR_routine_SubsysRanBC ; int8_T hardware_ISR_routine_SubsysRanBC ;
int8_T AtomicSubsystem_SubsysRanBC ; int8_T Subsystem1_SubsysRanBC ; int8_T
Subsystem_SubsysRanBC ; int8_T Firsttriggerinitialization_SubsysRanBC ;
char_T pad_Firsttriggerinitialization_SubsysRanBC [ 5 ] ; }
DW_Hall_sensor_120deg_filter_org_T ; typedef struct { real_T
Integrator_CSTATE ; real_T MechSystem_CSTATE ; real_T Integrator_CSTATE_n ;
real_T VariableTransportDelay_CSTATE ; real_T Integrator_CSTATE_l ; real_T
VariableTransportDelay_CSTATE_g ; real_T Filter_CSTATE ; real_T
Integrator_CSTATE_j ; } X_Hall_sensor_120deg_filter_org_T ; typedef struct {
real_T Integrator_CSTATE ; real_T MechSystem_CSTATE ; real_T
Integrator_CSTATE_n ; real_T VariableTransportDelay_CSTATE ; real_T
Integrator_CSTATE_l ; real_T VariableTransportDelay_CSTATE_g ; real_T
Filter_CSTATE ; real_T Integrator_CSTATE_j ; }
XDot_Hall_sensor_120deg_filter_org_T ; typedef struct { boolean_T
Integrator_CSTATE ; boolean_T MechSystem_CSTATE ; boolean_T
Integrator_CSTATE_n ; boolean_T VariableTransportDelay_CSTATE ; boolean_T
Integrator_CSTATE_l ; boolean_T VariableTransportDelay_CSTATE_g ; boolean_T
Filter_CSTATE ; boolean_T Integrator_CSTATE_j ; }
XDis_Hall_sensor_120deg_filter_org_T ; typedef struct { ZCSigState
software_ISR_routine_Trig_ZCE ; ZCSigState hardware_ISR_routine_Trig_ZCE ;
ZCSigState Firsttriggerinitialization_Trig_ZCE ; }
PrevZCX_Hall_sensor_120deg_filter_org_T ; typedef struct { const real_T
B_25_241_1872 ; } ConstB_Hall_sensor_120deg_filter_org_T ;
#define Hall_sensor_120deg_filter_org_rtC(S) ((ConstB_Hall_sensor_120deg_filter_org_T *) _ssGetConstBlockIO(S))
typedef struct { real_T * B_25_3 ; real_T * B_25_4 ; real_T * B_25_5 ; real_T
* B_25_6 ; real_T * B_25_7 ; real_T * B_25_9 ; real_T * B_25_10 ; real_T *
B_25_14 ; real_T * B_25_15 ; real_T * B_25_16 ; real_T * B_25_19 ; }
ExtY_Hall_sensor_120deg_filter_org_T ; struct
P_Hall_sensor_120deg_filter_org_T_ { real_T P_0 ; real_T P_1 ; real_T P_2 ;
real_T P_3 ; real_T P_4 ; real_T P_5 ; real_T P_6 ; real_T P_7 ; real_T P_8 ;
real_T P_9 ; real_T P_10 ; real_T P_11 ; real_T P_12 ; real_T P_13 ; real_T
P_14 ; real_T P_15 ; real_T P_16 ; real_T P_17 ; real_T P_18 ; real_T P_19 ;
real_T P_20 ; real_T P_21 ; real_T P_22 ; real_T P_23 ; real_T P_24 [ 2 ] ;
real_T P_25 ; real_T P_26 [ 2 ] ; real_T P_27 [ 22 ] ; real_T P_28 [ 2 ] ;
real_T P_29 [ 15 ] ; real_T P_30 [ 2 ] ; real_T P_31 [ 330 ] ; real_T P_32 [
2 ] ; real_T P_33 ; real_T P_34 ; real_T P_35 ; real_T P_36 ; real_T P_37 ;
real_T P_38 ; real_T P_39 ; real_T P_40 ; real_T P_41 ; real_T P_42 ; real_T
P_43 ; real_T P_44 ; real_T P_45 ; real_T P_46 ; real_T P_47 ; real_T P_48 ;
real_T P_49 ; real_T P_50 ; real_T P_51 ; real_T P_52 ; real_T P_53 ; real_T
P_54 ; real_T P_55 ; real_T P_56 ; real_T P_57 ; real_T P_58 ; real_T P_59 ;
real_T P_60 ; real_T P_61 ; real_T P_62 ; real_T P_63 ; real_T P_64 ; real_T
P_65 ; real_T P_66 ; real_T P_67 ; real_T P_68 ; real_T P_69 ; real_T P_70 ;
real_T P_71 ; real_T P_72 ; real_T P_73 ; real_T P_74 ; real_T P_75 ; real_T
P_76 ; real_T P_77 ; real_T P_78 ; real_T P_79 ; real_T P_80 ; real_T P_81 ;
real_T P_82 ; real_T P_83 ; real_T P_84 ; real_T P_85 ; real_T P_86 ; real_T
P_87 ; real_T P_88 ; real_T P_89 ; real_T P_90 ; real_T P_91 ; real_T P_92 ;
real_T P_93 ; real_T P_94 ; real_T P_95 ; real_T P_96 ; real_T P_97 ; real_T
P_98 ; real_T P_99 ; real_T P_100 ; real_T P_101 ; real_T P_102 ; real_T
P_103 ; real_T P_104 ; real_T P_105 [ 12 ] ; real_T P_106 ; real_T P_107 [ 3
] ; real_T P_108 [ 3 ] ; real_T P_109 ; real_T P_110 ; real_T P_111 ; real_T
P_112 ; real_T P_113 ; real_T P_114 ; real_T P_115 ; real_T P_116 ; real_T
P_117 ; real_T P_118 ; real_T P_119 ; real_T P_120 ; real_T P_121 ; real_T
P_122 ; real_T P_123 ; real_T P_124 ; real_T P_125 ; real_T P_126 ; real_T
P_127 ; real_T P_128 ; real_T P_129 ; real_T P_130 ; real_T P_131 ; uint8_T
P_132 ; uint8_T P_133 ; char_T pad_P_133 [ 6 ] ; } ; extern
P_Hall_sensor_120deg_filter_org_T Hall_sensor_120deg_filter_org_rtDefaultP ;
extern const ConstB_Hall_sensor_120deg_filter_org_T
Hall_sensor_120deg_filter_org_rtInvariant ;
#endif
