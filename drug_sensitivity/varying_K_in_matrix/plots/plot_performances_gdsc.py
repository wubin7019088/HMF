'''
Plot the performances of HMF D-MF and D-MTF, with varying values for Kt, on
the GDSC dataset.
'''

import matplotlib.pyplot as plt

MSE_max, MSE_min = 0.12, 0.07
fraction_min, fraction_max = 0.25, 0.95

values_K = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30]

perf_hmf_mf_gdsc_ARD = {'R^2': [0.5378895897404576, 0.5588179784583696, 0.5775754357991849, 0.5873917418246475, 0.5967456327721383, 0.6095091882778506, 0.6074754829120068, 0.6050982525383638, 0.6098315847434679, 0.611131820078387, 0.6082729251853476, 0.6140249635786372, 0.6069252831431039, 0.6083592162220847, 0.6019826370374308, 0.5917142836519045, 0.5739435402252778], 'MSE': [0.092136703486547483, 0.087905642199881034, 0.084164693137332741, 0.082259050400168274, 0.080401058765981775, 0.077825310883253979, 0.078174668859023189, 0.078696435988965113, 0.077705288040566881, 0.077498733288756283, 0.07804560567351479, 0.076928521167593494, 0.078374012701426674, 0.0780458543346009, 0.079341708581703488, 0.081416782601892793, 0.084949076252284456], 'Rp': [0.73356781208514232, 0.74800716339225581, 0.76044620352630921, 0.76679009228605166, 0.77298798892714338, 0.78126235797111454, 0.78032086351937813, 0.77899753778874326, 0.78209406846316987, 0.78295799672380328, 0.78134473535901727, 0.78535239371595467, 0.78142139740958672, 0.78250240626119072, 0.779086954732916, 0.77393268283739303, 0.76480257894949644]}
perf_hmf_mf_gdsc_no_ARD = {'R^2': [0.5363060417340935, 0.5614975454009382, 0.5791607097910151, 0.5868235238467349, 0.5948259587638552, 0.6055236879704063, 0.602006153186475, 0.6038681652766151, 0.6038486571826207, 0.6029574355307981, 0.5934197217857531, 0.5948126746691593, 0.5935278744198079, 0.5790847651634309, 0.5790906673749082, 0.5594027022281074, 0.5242266045833859], 'MSE': [0.092428563410528339, 0.087388634628372958, 0.083799369125948139, 0.082339345177863094, 0.080699584354268897, 0.078621891227560053, 0.079340555083425413, 0.078957528972110003, 0.078975654330226089, 0.079119037550295784, 0.080999147730606277, 0.080781475508719183, 0.080999020442368175, 0.083870073938298512, 0.083870826059296771, 0.087821360529603515, 0.094849007932430535], 'Rp': [0.7326684385887976, 0.74973170381131715, 0.76165930546992955, 0.76674695090264211, 0.77239877140582169, 0.77918775821311015, 0.77734384558978054, 0.77888754337254507, 0.77910536600665758, 0.77898878506090585, 0.77418628571332992, 0.77616794075932372, 0.77630781168525664, 0.76830027371813125, 0.76975722287856208, 0.76114635861732816, 0.74501999039888989]}

perf_hmf_mtf_gdsc_ARD = {'R^2': [0.5087871046603342, 0.5405982951199403, 0.5652606999681304, 0.5778745352237907, 0.5841729768645889, 0.5973615852417401, 0.6014992078098289, 0.6071197087358132, 0.6088170003967341, 0.6099720127546693, 0.6107244132760659, 0.6101133521196453, 0.6062368475380094, 0.6030565777712709, 0.6075537720283692, 0.5921403839514018, 0.5786920017302524], 'MSE': [0.097880852148347935, 0.091581028077929935, 0.086649408529322486, 0.084123504489505632, 0.08292821255114842, 0.080240212610094536, 0.079378349411783566, 0.078319419448748456, 0.077979735413061579, 0.077722877667606285, 0.077560494615294323, 0.077677077066387684, 0.078495354932438505, 0.079098908232854565, 0.078247431685996668, 0.081315327001849652, 0.08393351100768523], 'Rp': [0.71343352870722698, 0.73566640734330024, 0.7522106707838242, 0.76055351020782291, 0.76468840716568309, 0.77353682263301038, 0.77639316548043169, 0.78014484167757081, 0.78123252238557783, 0.78192009582992472, 0.78295303586020326, 0.78290172828340754, 0.78089948492215089, 0.77982497886089797, 0.78250326212486931, 0.77476445436477592, 0.76809996564793226]}
perf_hmf_mtf_gdsc_no_ARD = {'R^2': [0.5084157621428307, 0.5403638252030959, 0.5651194119339944, 0.5774662109212993, 0.5794649408627909, 0.5868785787961086, 0.5883374762968328, 0.5952588776588243, 0.5935662920709083, 0.5934768619981077, 0.5892755921509203, 0.5819142550599491, 0.5774149932937953, 0.566217514944143, 0.5478738958508538, 0.5329529878963819, 0.47753873671748004], 'MSE': [0.097999354426903898, 0.091577996918977403, 0.086673318951935155, 0.084246832655848564, 0.083840197160398186, 0.082384375620752737, 0.082022896390710268, 0.08065393903753966, 0.081017452247734198, 0.080933849063874991, 0.081882681554151279, 0.083330401984145902, 0.084223525383876063, 0.086468356936769478, 0.090109863647932262, 0.093120959444953272, 0.10408610144845129], 'Rp': [0.71330422066813837, 0.73578479067725422, 0.75239492148233345, 0.76051158538330754, 0.76183125514560479, 0.76666803526575611, 0.76801692224259244, 0.77229090455971183, 0.77153349809404448, 0.77196012324580665, 0.76999048018581107, 0.76685931821413322, 0.76555242646280541, 0.75965877272033344, 0.75177149948928645, 0.74602871524520997, 0.72407130438754963]}


''' Plot '''
fig = plt.figure(figsize=(3.8,3.0))
fig.subplots_adjust(left=0.16, right=0.965, bottom=0.12, top=0.97)
plt.xlabel("Kt", fontsize=12, labelpad=1) #fontsize=8
plt.ylabel("MSE", fontsize=12, labelpad=3) #fontsize=8, labelpad=-1
plt.yticks(fontsize=8) #fontsize=6
plt.xticks(fontsize=8) #fontsize=6

plt.plot(values_K, perf_hmf_mf_gdsc_ARD['MSE'], linestyle='-', linewidth=1.2, marker='o', label='HMF D-MF (ARD)', c='red', markersize=5)
plt.plot(values_K, perf_hmf_mf_gdsc_no_ARD['MSE'], linestyle='-', linewidth=1.2, marker='x', label='HMF D-MF (no ARD)', c='red', markersize=5)

plt.plot(values_K, perf_hmf_mtf_gdsc_ARD['MSE'], linestyle='-', linewidth=1.2, marker='o', label='HMF D-MTF (ARD)', c='blue', markersize=5)
plt.plot(values_K, perf_hmf_mtf_gdsc_no_ARD['MSE'], linestyle='-', linewidth=1.2, marker='x', label='HMF D-MTF (no ARD)', c='blue', markersize=5)
 
plt.xlim(0,values_K[-1]+1)
plt.ylim(MSE_min,MSE_max)
plt.legend(loc='upper left',fontsize=10)
    
plt.savefig("./varying_K_gdsc.png", dpi=600)