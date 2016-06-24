"""
Test the performance of HMF for recovering the CTRP dataset, where we vary the 
fraction of entries that are missing.
We repeat this 10 times per fraction and average that.

GDSC has 0.7356934001670844 observed entries
"""

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from HMF.code.models.hmf_Gibbs import HMF_Gibbs
from HMF.code.generate_mask.mask import try_generate_M_from_M
from HMF.drug_sensitivity.load_dataset import load_data_without_empty,load_data_filter

import numpy, random


''' Settings '''
metrics = ['MSE', 'R^2', 'Rp']

fractions_unknown = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
repeats = 10

iterations, burn_in, thinning = 500, 450, 2
settings = {
    'priorF'  : 'exponential',
    'orderG'  : 'normal',
    'priorSn' : 'normal',
    'priorSm' : 'normal',
    'orderF'  : 'columns',
    'orderG'  : 'rows',
    'orderSn' : 'rows',
    'orderSm' : 'rows',
    'ARD'     : True
}
hyperparameters = {
    'alphatau' : 1.,
    'betatau'  : 1.,
    'alpha0'   : 0.001,
    'beta0'    : 0.001,
    'lambdaF'  : 0.1,
    'lambdaG'  : 0.1,
    'lambdaSn' : 0.1,
    'lambdaSm' : 0.1,
}
init = {
    'F'       : 'kmeans',
    'Sn'      : 'least',
    'Sm'      : 'least',
    'G'       : 'least',
    'lambdat' : 'exp',
    'tau'     : 'exp'
}

K = {'Cell_lines':10, 'Drugs':10}
alpha_n = [1., 1., 1., 1.] # GDSC, CTRP, CCLE IC, CCLE EC


''' Load data '''
location = project_location+"HMF/drug_sensitivity/data/overlap/"
location_data = location+"data_row_01/"

R_ctrp,     M_ctrp,   cell_lines, drugs   = load_data_without_empty(location_data+"ctrp_ec50_row_01.txt")
R_ccle_ec,  M_ccle_ec                     = load_data_filter(location_data+"ccle_ec50_row_01.txt",cell_lines,drugs)
R_gdsc,     M_gdsc                        = load_data_filter(location_data+"gdsc_ic50_row_01.txt",cell_lines,drugs)
R_ccle_ic,  M_ccle_ic                     = load_data_filter(location_data+"ccle_ic50_row_01.txt",cell_lines,drugs)


''' Seed all of the methods the same '''
numpy.random.seed(0)
random.seed(0)

''' Generate matrices M - one list of (M_train,M_test)'s for each fraction '''
M_attempts = 1000
all_Ms_train_test = [ 
    [try_generate_M_from_M(M=M_ctrp,fraction=fraction,attempts=M_attempts) for r in range(0,repeats)]
    for fraction in fractions_unknown
]

''' Make sure each M has no empty rows or columns '''
def check_empty_rows_columns(M,fraction):
    sums_columns = M.sum(axis=0)
    sums_rows = M.sum(axis=1)
    for i,c in enumerate(sums_rows):
        assert c != 0, "Fully unobserved row in M, row %s. Fraction %s." % (i,fraction)
    for j,c in enumerate(sums_columns):
        assert c != 0, "Fully unobserved column in M, column %s. Fraction %s." % (j,fraction)
        
for Ms_train_test,fraction in zip(all_Ms_train_test,fractions_unknown):
    for (M_train,M_test) in Ms_train_test:
        check_empty_rows_columns(M_train,fraction)

''' Run the method on each of the M's for each fraction '''
all_performances = {metric:[] for metric in metrics} 
average_performances = {metric:[] for metric in metrics} # averaged over repeats
for (fraction,Ms_train_test) in zip(fractions_unknown,all_Ms_train_test):
    print "Trying fraction %s." % fraction
    
    # Run the algorithm <repeats> times and store all the performances
    for metric in metrics:
        all_performances[metric].append([])
    for repeat,(M_train,M_test) in zip(range(0,repeats),Ms_train_test):
        print "Repeat %s of fraction %s." % (repeat+1, fraction)
     
        R = [(R_ctrp,    M_train,   'Cell_lines', 'Drugs', alpha_n[1]),
             (R_gdsc,    M_gdsc,    'Cell_lines', 'Drugs', alpha_n[0]),  
             (R_ccle_ic, M_ccle_ic, 'Cell_lines', 'Drugs', alpha_n[2]),
             (R_ccle_ec, M_ccle_ec, 'Cell_lines', 'Drugs', alpha_n[3])]
        C, D = [], []

        HMF = HMF_Gibbs(R,C,D,K,settings,hyperparameters)
        HMF.initialise(init)
        HMF.run(iterations)
        
        # Measure the performances
        performances = HMF.predict_Rn(n=0,M_pred=M_test,burn_in=burn_in,thinning=thinning)
        for metric in metrics:
            # Add this metric's performance to the list of <repeat> performances for this fraction
            all_performances[metric][-1].append(performances[metric])
            
    # Compute the average across attempts
    for metric in metrics:
        average_performances[metric].append(sum(all_performances[metric][-1])/repeats)
    
 
print "repeats=%s \nfractions_unknown = %s \nall_performances = %s \naverage_performances = %s" % \
    (repeats,fractions_unknown,all_performances,average_performances)

'''
200 iterations
repeats=10 
fractions_unknown = [0.15, 0.2, 0.25] 
all_performances = {'R^2': [[0.4348838455724032, 0.39280427769291393, 0.49981285974004575, 0.3995359659498341, 0.4103630592421885, 0.43197303040323, 0.4636584549080546, 0.38047528466072356, 0.45365415640913587, 0.5665722003461124], [0.4158178298081997, 0.4154050039413044, 0.4184830617955204, 0.42716249044621724, 0.417637201103524, 0.4684707855915281, 0.4527882823772993, 0.4324113501827117, 0.4668693588480235, 0.47895861228418024], [0.444240525429635, 0.42871156041485536, 0.41071114649657914, 0.42105277411145414, 0.4530864021756983, 0.45986337235193353, 0.4011303136753993, 0.41356060180387866, 0.41462281979130633, 0.45258414802328395]], 'MSE': [[0.093740803618279245, 0.086956920276219318, 0.078354905600301353, 0.098656405431336996, 0.10159021917901406, 0.093697352070783252, 0.08458563056171374, 0.10533086265492582, 0.087659853755237993, 0.067160966313441595], [0.090653077877469443, 0.093087723876182471, 0.092530911955070266, 0.093978933142721044, 0.094272568678299209, 0.085336684469607502, 0.083086276945172802, 0.092109804031501208, 0.088059063445565924, 0.083906886237739439], [0.089885872740905037, 0.092453575564495891, 0.093556602744979692, 0.090847772114902942, 0.086101215230863615, 0.085064649915824145, 0.097114482613302799, 0.090947661738193811, 0.092541266597027952, 0.088315085938224042]], 'Rp': [[0.66152495841011427, 0.62884415004343364, 0.70793169576828974, 0.63381542793603385, 0.65272321558543234, 0.66095321081923031, 0.68174182984289389, 0.6283031075625698, 0.67433817512765126, 0.75283125252352423], [0.6472899505843388, 0.64665055295855234, 0.64880681961443287, 0.65478690407171181, 0.64844743600795629, 0.68477960517413428, 0.6760862886636132, 0.65884137826859102, 0.68404650363728725, 0.69221422899373752], [0.66721437360783475, 0.65660524518837249, 0.64291953536030422, 0.6503683810639409, 0.67372829815685109, 0.67945021222837954, 0.63840355425700535, 0.64645193942770807, 0.64669239110458399, 0.67387116239107636]]} 
average_performances = {'R^2': [0.4433733134924642, 0.4394003976378508, 0.4299563664274024], 'MSE': [0.089773391946125353, 0.089702193065932939, 0.090682818519871991], 'Rp': [0.66830070236191741, 0.6641949667974355, 0.65757050927860572]}

repeats=10 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.4298985215867027, 0.40120090124287267, 0.4287727074555263, 0.42963566997518077, 0.4113212996793446, 0.4248287457666431, 0.41863849828416144, 0.44102025475427, 0.42919706302104543, 0.413934194077224], [0.3977820712795713, 0.41731541825894836, 0.4101011376020167, 0.43756902746341053, 0.42524683219254156, 0.4207520048989396, 0.425098109729786, 0.4174863716171996, 0.42244244658953956, 0.42606266805221904], [0.3950443898328099, 0.42738500916252686, 0.3966797347025943, 0.41439399314928316, 0.43850399680194163, 0.4287483354154187, 0.44361393942933336, 0.41053936977777095, 0.4226217787223804, 0.43557940156370134], [0.40656560700696454, 0.3946162910054022, 0.42849660707229087, 0.3859442297047396, 0.4101501817037284, 0.4031999156716515, 0.4081738325104154, 0.43888617773490657, 0.4037483827716105, 0.4049407250691833], [0.3929053076553586, 0.40487497591524524, 0.3999704182537148, 0.39471901868473547, 0.40778044323203577, 0.4217434851890527, 0.40805741467758894, 0.4121232770171245, 0.41096068132100694, 0.3973926901011401], [0.4012685444519395, 0.39851899418686143, 0.3974583225918492, 0.3887811180870915, 0.40580338264099947, 0.3943919112465569, 0.37852230749796845, 0.38472438327742675, 0.4148158456906499, 0.4030166209630337], [0.3957779779219397, 0.4085341843702597, 0.3725301223100581, 0.39899575760973105, 0.39276316843884906, 0.39559120514244706, 0.4061732319135327, 0.395308492692204, 0.40208618138083263, 0.3892990218631789], [0.3986860643002045, 0.37510244983789487, 0.39451863028611134, 0.40261999340654364, 0.3849112083465792, 0.378570324156551, 0.38477600564300296, 0.39930374180820627, 0.3834290958672416, 0.4024989683680692], [0.37567993220396045, 0.3744587066879014, 0.379561994268645, 0.3702784235016202, 0.38729951080897107, 0.3498409542163323, 0.39595419974948287, 0.3665262644077528, 0.36637462629309214, 0.35533489767052684], [0.36334328573720487, 0.3841405591035625, 0.37467548254989624, 0.3919818825838618, 0.31844869369707096, 0.35066509450698, 0.3597812861668287, 0.3484517906864363, 0.34320477254857895, 0.3372156804211772], [0.3395274780729248, 0.3473147684360762, 0.33878379962596217, 0.3544887127349987, 0.35308900005075383, 0.34612423145291116, 0.335711004072783, 0.34331454056076416, 0.3466552455775028, 0.3351117677951977], [0.3218623676566237, 0.3289991320184671, 0.31482678454979474, 0.32239071251515383, 0.3178535089411534, 0.33292464920369835, 0.345188899207164, 0.33085581980566137, 0.3357980541818355, 0.3532345857659054], [0.2944763688181272, 0.24507204195582433, 0.24550287922981462, 0.29819251760783083, 0.25581347146251543, 0.2483696209302121, 0.30699853610355887, 0.25178778218776066, 0.305151098187856, 0.28338173266479094]], 'MSE': [[0.092204211981031223, 0.092906402938007157, 0.093948984375797684, 0.089962831393878243, 0.094556957783272999, 0.092074339659319687, 0.093255004899740021, 0.090782736154643051, 0.091628624729205285, 0.093999836486715241], [0.09398350048387151, 0.091772876254994043, 0.09283418701093854, 0.08936778717317849, 0.09316706177055295, 0.091235886053510837, 0.090334991495466893, 0.092171905806052737, 0.093585054140232798, 0.089521350428656138], [0.095872432048009923, 0.091402791824648999, 0.095463105302865947, 0.093469840916536526, 0.088763681021598331, 0.090275623558997348, 0.090113885784498651, 0.092909449484114476, 0.092729851704582353, 0.089828135347543414], [0.094414255231798361, 0.095576199859404895, 0.090633342266345798, 0.097512435213297582, 0.09423787339733343, 0.094458086949740769, 0.094865245667124273, 0.089356687544596386, 0.092994996998658624, 0.095175129229998476], [0.097147454484010604, 0.094193353429102428, 0.095812351735781703, 0.094613236998251332, 0.09369527650261468, 0.092066275544816611, 0.094268791712219122, 0.093059712574892955, 0.093171747539587416, 0.095538605012336381], [0.094923641607187109, 0.094394870345691925, 0.096522447922582133, 0.09729244905408535, 0.094093004281424281, 0.096479562209925887, 0.099297768334007205, 0.097314049698701097, 0.094629370752967304, 0.094935786650729437], [0.096529210990591002, 0.094612784735601085, 0.099001515618990371, 0.09567521284648299, 0.097441949106714068, 0.095416628572339318, 0.093775083701538725, 0.096716098402094372, 0.095100329325456395, 0.097405802668649191], [0.095981043941685065, 0.099742031946966764, 0.096109818475576661, 0.09496276749922021, 0.097658365510379694, 0.099019421079990178, 0.097218840091803899, 0.096291207538155968, 0.098199363748963972, 0.09579438372553041], [0.099004330009538524, 0.098476792931279131, 0.098871927152978142, 0.099325195784164544, 0.098242953065129923, 0.10267052613473869, 0.096206993014429004, 0.10158704924880188, 0.10088207078534552, 0.10190008540599775], [0.10171475361439489, 0.097491811154939073, 0.098957034573899871, 0.096699673733968886, 0.1078342462248597, 0.10239248320950384, 0.10312134521159806, 0.10300208985838097, 0.10425600940055117, 0.10509095686209194], [0.10567500062276904, 0.1040186268270752, 0.10555878942096462, 0.10278155881596877, 0.10346510127592763, 0.10437174729821384, 0.10553052848519526, 0.10493725534647794, 0.10362381029333542, 0.10611967189817388], [0.10726114464003141, 0.10621889103961753, 0.10845242673963479, 0.10822900617556776, 0.10845936662269409, 0.10593174800567819, 0.10406519313204322, 0.10618118337277836, 0.10626414481054534, 0.10242180248203976], [0.11219491365263118, 0.12044515216646356, 0.11976879153288084, 0.11167978950525774, 0.11812010556965073, 0.11942815802516744, 0.11047931821427397, 0.11911243829554678, 0.11046310740183422, 0.11369526585283549]], 'Rp': [[0.6567387074594917, 0.63783651276107478, 0.65817351265165658, 0.65806625049360234, 0.6449760616284681, 0.65588528771100096, 0.6492639301232882, 0.6663407803390532, 0.65677678018463648, 0.64527754636174084], [0.63530983869675195, 0.64973035882886587, 0.64258966758969061, 0.66271592326936801, 0.65353917619136914, 0.6517520238706459, 0.65348009389462236, 0.64758445087454775, 0.65169576189835321, 0.65464183940848053], [0.63375577659687687, 0.6557387923626864, 0.63501262429034455, 0.64586547173517217, 0.66285544020858622, 0.65549469724162113, 0.66692778302379663, 0.64274636893045645, 0.65149718166764148, 0.66185110308825612], [0.64194937354954684, 0.63223218023936778, 0.65576382079492646, 0.62583071288200642, 0.64298605036064782, 0.6387869677063498, 0.64079611070534404, 0.66335587344955982, 0.63908783789781198, 0.63960481760914756], [0.6321318516126333, 0.63904248123381424, 0.63532918152910467, 0.63486207378558834, 0.64145473977143797, 0.65173433946175496, 0.64141851632427294, 0.6450133341934019, 0.64293878946377481, 0.63463878260585371], [0.6357470392052138, 0.63541186834233987, 0.63307813469844731, 0.62927283391469413, 0.64043625306445051, 0.63207781527047324, 0.62111424604207288, 0.62540279714879965, 0.64554150084791628, 0.63747145992705834], [0.63201930016003827, 0.64102067069848667, 0.61689812496053231, 0.63494829504234218, 0.63052458708286141, 0.63296389189263613, 0.6397385442862501, 0.63064623014431964, 0.63666093647630839, 0.6273041814872341], [0.63478853525447143, 0.61738585092483633, 0.63076655487066091, 0.63554813787156894, 0.62450915318850675, 0.61968288310209063, 0.62342622864118569, 0.63321707406973604, 0.62633205484170518, 0.63596228828008816], [0.61892685792612501, 0.61576220649992675, 0.62006284582684601, 0.6145894267833697, 0.62518255854600557, 0.60398778266394404, 0.63174454362314347, 0.60946631470590085, 0.61237019279956295, 0.6068877565322478], [0.61018391855335796, 0.62457948182292389, 0.61784068053165064, 0.62740411996721357, 0.58318349291545502, 0.60290474420453566, 0.6066187015611042, 0.60105570885696002, 0.59791026688527948, 0.59438115137963576], [0.59338149537836538, 0.59879081435920634, 0.59005858097142427, 0.60063169715242704, 0.60106461470606964, 0.5973501776979101, 0.5915434920726661, 0.59369557411484908, 0.59894951294720689, 0.58935384663441481], [0.58419621649696818, 0.58710516827753401, 0.57794400121461353, 0.58595013996228329, 0.57975329359231331, 0.5850058974078135, 0.59343003891511448, 0.59007200166350771, 0.59031482615515274, 0.60013532660659241], [0.56367378783029409, 0.54158544449638624, 0.54197226995666947, 0.57049080454188461, 0.54162946265357714, 0.53948300394662196, 0.57113227966397995, 0.52750878538105106, 0.57391742945579383, 0.55561283725207244]]} 
average_performances = {'R^2': [0.42284478558429717, 0.41998560876841723, 0.42131099485577606, 0.4084721950250893, 0.40505277120470035, 0.3967301430634377, 0.39570593436430335, 0.3904416482020405, 0.37213095098082855, 0.3571908528001597, 0.3440120548379874, 0.3303934513845458, 0.2734746049148291], 'MSE': [0.092531993040161062, 0.091797460061745481, 0.092082879699339606, 0.093922425235829859, 0.094356680553361327, 0.095988295085730174, 0.096167461596845763, 0.097097724355827295, 0.099716792353240311, 0.10205604038441884, 0.10460820902841017, 0.10634849070206305, 0.11553870402165418], 'Rp': [0.65293353697140133, 0.65030391345226946, 0.65117452391454389, 0.64203937451947091, 0.63985640899816376, 0.63355539484614665, 0.63227247622310079, 0.62816187610448504, 0.61589804859070729, 0.60660622666781183, 0.59548198060345403, 0.58739069102918928, 0.55270061051783304]}

Combined:
repeats=10 
fractions_unknown = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.4348838455724032, 0.39280427769291393, 0.49981285974004575, 0.3995359659498341, 0.4103630592421885, 0.43197303040323, 0.4636584549080546, 0.38047528466072356, 0.45365415640913587, 0.5665722003461124], [0.4158178298081997, 0.4154050039413044, 0.4184830617955204, 0.42716249044621724, 0.417637201103524, 0.4684707855915281, 0.4527882823772993, 0.4324113501827117, 0.4668693588480235, 0.47895861228418024], [0.444240525429635, 0.42871156041485536, 0.41071114649657914, 0.42105277411145414, 0.4530864021756983, 0.45986337235193353, 0.4011303136753993, 0.41356060180387866, 0.41462281979130633, 0.45258414802328395], [0.4298985215867027, 0.40120090124287267, 0.4287727074555263, 0.42963566997518077, 0.4113212996793446, 0.4248287457666431, 0.41863849828416144, 0.44102025475427, 0.42919706302104543, 0.413934194077224], [0.3977820712795713, 0.41731541825894836, 0.4101011376020167, 0.43756902746341053, 0.42524683219254156, 0.4207520048989396, 0.425098109729786, 0.4174863716171996, 0.42244244658953956, 0.42606266805221904], [0.3950443898328099, 0.42738500916252686, 0.3966797347025943, 0.41439399314928316, 0.43850399680194163, 0.4287483354154187, 0.44361393942933336, 0.41053936977777095, 0.4226217787223804, 0.43557940156370134], [0.40656560700696454, 0.3946162910054022, 0.42849660707229087, 0.3859442297047396, 0.4101501817037284, 0.4031999156716515, 0.4081738325104154, 0.43888617773490657, 0.4037483827716105, 0.4049407250691833], [0.3929053076553586, 0.40487497591524524, 0.3999704182537148, 0.39471901868473547, 0.40778044323203577, 0.4217434851890527, 0.40805741467758894, 0.4121232770171245, 0.41096068132100694, 0.3973926901011401], [0.4012685444519395, 0.39851899418686143, 0.3974583225918492, 0.3887811180870915, 0.40580338264099947, 0.3943919112465569, 0.37852230749796845, 0.38472438327742675, 0.4148158456906499, 0.4030166209630337], [0.3957779779219397, 0.4085341843702597, 0.3725301223100581, 0.39899575760973105, 0.39276316843884906, 0.39559120514244706, 0.4061732319135327, 0.395308492692204, 0.40208618138083263, 0.3892990218631789], [0.3986860643002045, 0.37510244983789487, 0.39451863028611134, 0.40261999340654364, 0.3849112083465792, 0.378570324156551, 0.38477600564300296, 0.39930374180820627, 0.3834290958672416, 0.4024989683680692], [0.37567993220396045, 0.3744587066879014, 0.379561994268645, 0.3702784235016202, 0.38729951080897107, 0.3498409542163323, 0.39595419974948287, 0.3665262644077528, 0.36637462629309214, 0.35533489767052684], [0.36334328573720487, 0.3841405591035625, 0.37467548254989624, 0.3919818825838618, 0.31844869369707096, 0.35066509450698, 0.3597812861668287, 0.3484517906864363, 0.34320477254857895, 0.3372156804211772], [0.3395274780729248, 0.3473147684360762, 0.33878379962596217, 0.3544887127349987, 0.35308900005075383, 0.34612423145291116, 0.335711004072783, 0.34331454056076416, 0.3466552455775028, 0.3351117677951977], [0.3218623676566237, 0.3289991320184671, 0.31482678454979474, 0.32239071251515383, 0.3178535089411534, 0.33292464920369835, 0.345188899207164, 0.33085581980566137, 0.3357980541818355, 0.3532345857659054], [0.2944763688181272, 0.24507204195582433, 0.24550287922981462, 0.29819251760783083, 0.25581347146251543, 0.2483696209302121, 0.30699853610355887, 0.25178778218776066, 0.305151098187856, 0.28338173266479094]], 'MSE': [[0.093740803618279245, 0.086956920276219318, 0.078354905600301353, 0.098656405431336996, 0.10159021917901406, 0.093697352070783252, 0.08458563056171374, 0.10533086265492582, 0.087659853755237993, 0.067160966313441595], [0.090653077877469443, 0.093087723876182471, 0.092530911955070266, 0.093978933142721044, 0.094272568678299209, 0.085336684469607502, 0.083086276945172802, 0.092109804031501208, 0.088059063445565924, 0.083906886237739439], [0.089885872740905037, 0.092453575564495891, 0.093556602744979692, 0.090847772114902942, 0.086101215230863615, 0.085064649915824145, 0.097114482613302799, 0.090947661738193811, 0.092541266597027952, 0.088315085938224042], [0.092204211981031223, 0.092906402938007157, 0.093948984375797684, 0.089962831393878243, 0.094556957783272999, 0.092074339659319687, 0.093255004899740021, 0.090782736154643051, 0.091628624729205285, 0.093999836486715241], [0.09398350048387151, 0.091772876254994043, 0.09283418701093854, 0.08936778717317849, 0.09316706177055295, 0.091235886053510837, 0.090334991495466893, 0.092171905806052737, 0.093585054140232798, 0.089521350428656138], [0.095872432048009923, 0.091402791824648999, 0.095463105302865947, 0.093469840916536526, 0.088763681021598331, 0.090275623558997348, 0.090113885784498651, 0.092909449484114476, 0.092729851704582353, 0.089828135347543414], [0.094414255231798361, 0.095576199859404895, 0.090633342266345798, 0.097512435213297582, 0.09423787339733343, 0.094458086949740769, 0.094865245667124273, 0.089356687544596386, 0.092994996998658624, 0.095175129229998476], [0.097147454484010604, 0.094193353429102428, 0.095812351735781703, 0.094613236998251332, 0.09369527650261468, 0.092066275544816611, 0.094268791712219122, 0.093059712574892955, 0.093171747539587416, 0.095538605012336381], [0.094923641607187109, 0.094394870345691925, 0.096522447922582133, 0.09729244905408535, 0.094093004281424281, 0.096479562209925887, 0.099297768334007205, 0.097314049698701097, 0.094629370752967304, 0.094935786650729437], [0.096529210990591002, 0.094612784735601085, 0.099001515618990371, 0.09567521284648299, 0.097441949106714068, 0.095416628572339318, 0.093775083701538725, 0.096716098402094372, 0.095100329325456395, 0.097405802668649191], [0.095981043941685065, 0.099742031946966764, 0.096109818475576661, 0.09496276749922021, 0.097658365510379694, 0.099019421079990178, 0.097218840091803899, 0.096291207538155968, 0.098199363748963972, 0.09579438372553041], [0.099004330009538524, 0.098476792931279131, 0.098871927152978142, 0.099325195784164544, 0.098242953065129923, 0.10267052613473869, 0.096206993014429004, 0.10158704924880188, 0.10088207078534552, 0.10190008540599775], [0.10171475361439489, 0.097491811154939073, 0.098957034573899871, 0.096699673733968886, 0.1078342462248597, 0.10239248320950384, 0.10312134521159806, 0.10300208985838097, 0.10425600940055117, 0.10509095686209194], [0.10567500062276904, 0.1040186268270752, 0.10555878942096462, 0.10278155881596877, 0.10346510127592763, 0.10437174729821384, 0.10553052848519526, 0.10493725534647794, 0.10362381029333542, 0.10611967189817388], [0.10726114464003141, 0.10621889103961753, 0.10845242673963479, 0.10822900617556776, 0.10845936662269409, 0.10593174800567819, 0.10406519313204322, 0.10618118337277836, 0.10626414481054534, 0.10242180248203976], [0.11219491365263118, 0.12044515216646356, 0.11976879153288084, 0.11167978950525774, 0.11812010556965073, 0.11942815802516744, 0.11047931821427397, 0.11911243829554678, 0.11046310740183422, 0.11369526585283549]], 'Rp': [[0.66152495841011427, 0.62884415004343364, 0.70793169576828974, 0.63381542793603385, 0.65272321558543234, 0.66095321081923031, 0.68174182984289389, 0.6283031075625698, 0.67433817512765126, 0.75283125252352423], [0.6472899505843388, 0.64665055295855234, 0.64880681961443287, 0.65478690407171181, 0.64844743600795629, 0.68477960517413428, 0.6760862886636132, 0.65884137826859102, 0.68404650363728725, 0.69221422899373752], [0.66721437360783475, 0.65660524518837249, 0.64291953536030422, 0.6503683810639409, 0.67372829815685109, 0.67945021222837954, 0.63840355425700535, 0.64645193942770807, 0.64669239110458399, 0.67387116239107636], [0.6567387074594917, 0.63783651276107478, 0.65817351265165658, 0.65806625049360234, 0.6449760616284681, 0.65588528771100096, 0.6492639301232882, 0.6663407803390532, 0.65677678018463648, 0.64527754636174084], [0.63530983869675195, 0.64973035882886587, 0.64258966758969061, 0.66271592326936801, 0.65353917619136914, 0.6517520238706459, 0.65348009389462236, 0.64758445087454775, 0.65169576189835321, 0.65464183940848053], [0.63375577659687687, 0.6557387923626864, 0.63501262429034455, 0.64586547173517217, 0.66285544020858622, 0.65549469724162113, 0.66692778302379663, 0.64274636893045645, 0.65149718166764148, 0.66185110308825612], [0.64194937354954684, 0.63223218023936778, 0.65576382079492646, 0.62583071288200642, 0.64298605036064782, 0.6387869677063498, 0.64079611070534404, 0.66335587344955982, 0.63908783789781198, 0.63960481760914756], [0.6321318516126333, 0.63904248123381424, 0.63532918152910467, 0.63486207378558834, 0.64145473977143797, 0.65173433946175496, 0.64141851632427294, 0.6450133341934019, 0.64293878946377481, 0.63463878260585371], [0.6357470392052138, 0.63541186834233987, 0.63307813469844731, 0.62927283391469413, 0.64043625306445051, 0.63207781527047324, 0.62111424604207288, 0.62540279714879965, 0.64554150084791628, 0.63747145992705834], [0.63201930016003827, 0.64102067069848667, 0.61689812496053231, 0.63494829504234218, 0.63052458708286141, 0.63296389189263613, 0.6397385442862501, 0.63064623014431964, 0.63666093647630839, 0.6273041814872341], [0.63478853525447143, 0.61738585092483633, 0.63076655487066091, 0.63554813787156894, 0.62450915318850675, 0.61968288310209063, 0.62342622864118569, 0.63321707406973604, 0.62633205484170518, 0.63596228828008816], [0.61892685792612501, 0.61576220649992675, 0.62006284582684601, 0.6145894267833697, 0.62518255854600557, 0.60398778266394404, 0.63174454362314347, 0.60946631470590085, 0.61237019279956295, 0.6068877565322478], [0.61018391855335796, 0.62457948182292389, 0.61784068053165064, 0.62740411996721357, 0.58318349291545502, 0.60290474420453566, 0.6066187015611042, 0.60105570885696002, 0.59791026688527948, 0.59438115137963576], [0.59338149537836538, 0.59879081435920634, 0.59005858097142427, 0.60063169715242704, 0.60106461470606964, 0.5973501776979101, 0.5915434920726661, 0.59369557411484908, 0.59894951294720689, 0.58935384663441481], [0.58419621649696818, 0.58710516827753401, 0.57794400121461353, 0.58595013996228329, 0.57975329359231331, 0.5850058974078135, 0.59343003891511448, 0.59007200166350771, 0.59031482615515274, 0.60013532660659241], [0.56367378783029409, 0.54158544449638624, 0.54197226995666947, 0.57049080454188461, 0.54162946265357714, 0.53948300394662196, 0.57113227966397995, 0.52750878538105106, 0.57391742945579383, 0.55561283725207244]]} 
average_performances = {'R^2': [0.4433733134924642, 0.4394003976378508, 0.4299563664274024, 0.42284478558429717, 0.41998560876841723, 0.42131099485577606, 0.4084721950250893, 0.40505277120470035, 0.3967301430634377, 0.39570593436430335, 0.3904416482020405, 0.37213095098082855, 0.3571908528001597, 0.3440120548379874, 0.3303934513845458, 0.2734746049148291], 'MSE': [0.089773391946125353, 0.089702193065932939, 0.090682818519871991, 0.092531993040161062, 0.091797460061745481, 0.092082879699339606, 0.093922425235829859, 0.094356680553361327, 0.095988295085730174, 0.096167461596845763, 0.097097724355827295, 0.099716792353240311, 0.10205604038441884, 0.10460820902841017, 0.10634849070206305, 0.11553870402165418], 'Rp': [0.66830070236191741, 0.6641949667974355, 0.65757050927860572, 0.65293353697140133, 0.65030391345226946, 0.65117452391454389, 0.64203937451947091, 0.63985640899816376, 0.63355539484614665, 0.63227247622310079, 0.62816187610448504, 0.61589804859070729, 0.60660622666781183, 0.59548198060345403, 0.58739069102918928, 0.55270061051783304]}

500 iterations
repeats=10 
fractions_unknown = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.44666411292583896, 0.3569268323782062, 0.49727472898668157, 0.4256723156335023, 0.43368343981009794, 0.4420646160174174, 0.46576980593608985, 0.3674768250521945, 0.45309240658704064, 0.5436865560044363], [0.4148062114474824, 0.40171046447878445, 0.4214964997875331, 0.4425690615222688, 0.4480854964736951, 0.47706227121873934, 0.43765718160971323, 0.4570894231701833, 0.4908996319247385, 0.4953294914946087], [0.4446060865732253, 0.4269390415341572, 0.4050814189104537, 0.4270961304222616, 0.4768919832732804, 0.46650782736168783, 0.4117590695241169, 0.4268365626227274, 0.4166913502513906, 0.4659703116839987], [0.4126353550067694, 0.402810129479792, 0.45620805338615134, 0.4229655208021802, 0.4206329169504843, 0.42400272977972975, 0.41870970079191483, 0.4499909343659787, 0.43342069667681027, 0.40091245902491135], [0.42624817024463235, 0.4249567603608069, 0.4088920436014195, 0.40889427090300157, 0.42478491152523057, 0.4451788027446656, 0.43817908660934546, 0.43749973624905725, 0.4159548506508509, 0.43133364606254543], [0.4414919091353853, 0.4118209757967227, 0.43574296862181194, 0.3990166188527088, 0.434349875797828, 0.4238687097258814, 0.43968346984748874, 0.4432025166066601, 0.4478114901912754, 0.42252613884107626], [0.42767853228657127, 0.4493517586426278, 0.41768178231145037, 0.43617081643533895, 0.4346332298931307, 0.41323234116543217, 0.4200788408655436, 0.4206260521533055, 0.42586816236874214, 0.41880750249812093], [0.3980234870477777, 0.416749378875115, 0.42213199096363996, 0.4163493744042559, 0.4173315534426455, 0.4354154646470565, 0.4199063907048629, 0.4110086303162457, 0.39094774393911824, 0.4217262202440454], [0.39025740149226296, 0.3920975605109591, 0.427428656023238, 0.40538822308037425, 0.4117290514559565, 0.41173148055572595, 0.4309251689085085, 0.4261843984112219, 0.38882381833294277, 0.4185288572351754], [0.4066292024052721, 0.3859241253741593, 0.3842781527375978, 0.4063057996294913, 0.4085948205823652, 0.402202557675981, 0.41006321607144725, 0.41071307822888203, 0.37235284465385676, 0.37900802838655967], [0.3953310408272743, 0.38924594879832564, 0.39534018765111545, 0.3970570063428286, 0.38978976705920276, 0.39200688163075237, 0.3962373006364631, 0.39360266757416573, 0.3842624916320361, 0.38672085893730634], [0.36584674701686215, 0.4065798418028287, 0.3814027526076196, 0.39160942322457193, 0.3861050238160266, 0.3907551032476634, 0.38888249002273256, 0.41279445202118437, 0.35925666183702554, 0.40020415867653525], [0.3820364618686696, 0.38163013092341136, 0.3790876344388725, 0.38993243668790345, 0.38657612412055553, 0.3806895872068118, 0.3690537803832161, 0.3717692387712902, 0.3701199608025222, 0.36514720793427713], [0.36433394509399153, 0.3652658547813066, 0.337181868643857, 0.3717714286724251, 0.350379164282172, 0.3640607634685432, 0.3752532566146102, 0.3794858869532226, 0.36955408491894737, 0.3268618796720938], [0.3163854950281626, 0.3591850914456757, 0.37050228414763664, 0.3514317839998321, 0.3400023892379602, 0.3343368789640725, 0.32831108868757375, 0.3403742744557984, 0.34932092475828813, 0.3459490343522862], [0.30310932392144807, 0.32908148970638673, 0.33479570650292045, 0.31753658459426004, 0.3049266412176277, 0.31249527609491057, 0.3439759893637775, 0.2874563565797027, 0.2770890516571235, 0.3368524907974504]], 'MSE': [[0.091786706712895627, 0.092094954088597927, 0.078752506777088338, 0.094362196012173452, 0.097572284735851292, 0.092032721866840278, 0.08425265251875258, 0.10754084545279012, 0.087749985139652403, 0.070707167064570378], [0.09081006027562491, 0.095268367769293288, 0.092051414029555065, 0.091451352303535627, 0.089343615417787348, 0.083957326800790696, 0.085383718298078531, 0.088104980348922612, 0.084089898707811722, 0.081270570712896006], [0.08982674863428107, 0.092740428399107983, 0.094450388847001271, 0.089899455183094917, 0.082353476154832864, 0.08401823274958363, 0.095390892074923392, 0.088888765972465658, 0.092214256192040017, 0.086155484257325984], [0.094445878626026186, 0.095247206715547206, 0.085881850404157883, 0.09101593584049239, 0.091636638633960446, 0.09155751601532254, 0.093983757755320016, 0.087429248436800888, 0.087950008371607116, 0.095845039286449593], [0.090779702454010916, 0.091492508869438327, 0.094450904854762999, 0.092975481017688336, 0.091211480693384375, 0.088259693133346015, 0.090948925998186977, 0.088861741727470453, 0.091219618040380535, 0.089736797185467065], [0.088307220766652553, 0.092468767975393787, 0.090368086085111529, 0.094668626985711782, 0.089997578840120274, 0.093028945687906581, 0.089048392459352546, 0.089035220500900444, 0.090153481120019058, 0.092401570030628447], [0.092041567813241409, 0.087963446095462305, 0.092776738596182518, 0.090045941506973939, 0.090970884656150025, 0.092568537814025409, 0.090938181974204987, 0.093441205670442271, 0.091348628208193977, 0.093039377135250359], [0.096166194199857988, 0.093269579868619987, 0.092765363545432453, 0.092130451095094545, 0.092780322960131001, 0.089546856852567053, 0.092239852163003816, 0.093368266163361885, 0.096251775387114172, 0.092135550131945673], [0.09708595261107382, 0.096671536202352082, 0.091906782698267991, 0.095265465943914163, 0.092495041410463455, 0.093732524694874406, 0.090277766399941714, 0.092713574933508652, 0.096009846117314918, 0.09248234365380395], [0.094779771408056546, 0.097226159995966857, 0.09637013215931077, 0.094688280367036859, 0.093575471573426675, 0.096122159534292331, 0.093168054937352932, 0.093078714927431638, 0.10013026770633467, 0.098917642607153522], [0.096070712650261611, 0.095944858566372637, 0.097572138857718108, 0.095696071910121416, 0.096328035240161994, 0.095888102737070324, 0.096503912185436191, 0.09589027780081906, 0.098629359273761819, 0.097309684621058504], [0.1014951907953113, 0.093574656723958344, 0.099177667549853202, 0.096661365988395143, 0.097188980256077737, 0.096401984067169558, 0.097314114091611045, 0.093412803400275773, 0.10153345044555921, 0.095764450090634723], [0.09842129058461184, 0.097771175962679688, 0.098832742523638148, 0.096758634881165637, 0.09825766594174247, 0.099057983413916972, 0.099931131074731033, 0.099807729407747889, 0.10046178521115595, 0.10162719240198176], [0.10145183207203078, 0.10138586777140621, 0.10499010045829929, 0.09957052793117846, 0.10316002071278577, 0.1010798691148764, 0.099459438216906365, 0.09839301253987888, 0.10025562473519069, 0.10720732891113395], [0.10847736445622889, 0.10252250639749756, 0.099687288925733572, 0.1031862862251, 0.10545862967872213, 0.10537097798408253, 0.1062495458655254, 0.10526085375171267, 0.10343089717269507, 0.10393367819233464], [0.11082206998081597, 0.10704184578481681, 0.10559445776718365, 0.10860153601919299, 0.11032467717384925, 0.10923909556609682, 0.10458431793170657, 0.11343414173047188, 0.11492425118684321, 0.10521184819750289]], 'Rp': [[0.66948765797074483, 0.60933363965341969, 0.70769464909276658, 0.65401524195771188, 0.66597403406093902, 0.66726753791953552, 0.68313228762680023, 0.62080865189666301, 0.67466102342138656, 0.73787276042431016], [0.64689703613110794, 0.63687430254854938, 0.65123997949484658, 0.6661346246953187, 0.67025584527187754, 0.69121730802793147, 0.66601383415945892, 0.67658472497916733, 0.70126318606554217, 0.70403424956083882], [0.66760719077344965, 0.65615338870588891, 0.6397899995695967, 0.65465556125401003, 0.69060128406253907, 0.68339498181046843, 0.64502426035331373, 0.65496921961346233, 0.64786210919479514, 0.6829585882823449], [0.6453957611978226, 0.6376064493280782, 0.67590075238285252, 0.65212518701869282, 0.64994488838501197, 0.6524311358146172, 0.64890091662895333, 0.67158767832435184, 0.66003936356008019, 0.63747273361872692], [0.65626171589704363, 0.65299279959604561, 0.6411425666577476, 0.64231802801475413, 0.65357582739288766, 0.66779037327857083, 0.66264694174307015, 0.6632159219207705, 0.64733900164643443, 0.65732723964790019], [0.66477777211542977, 0.64356874739402126, 0.66066289715501247, 0.63699668242071594, 0.66104624244482113, 0.65199455178730503, 0.66413257977139528, 0.66631119001020045, 0.669545170556055, 0.65157878178294326], [0.65537943377828145, 0.67049425182115663, 0.64973774422082553, 0.66074449954751546, 0.66041708967704138, 0.64501399382026481, 0.65136958220165653, 0.65073159253409341, 0.65420059765476279, 0.64906196317328824], [0.63373991851200118, 0.64731256559526895, 0.65110511963882067, 0.64640044153386234, 0.64741221324769838, 0.66026411008002506, 0.64919660920007982, 0.64317112738328552, 0.62855393842722496, 0.64982886793314321], [0.62904951158355704, 0.6284697619657853, 0.65405129644840376, 0.63828861028065109, 0.64357408689555395, 0.64308171603649122, 0.65723381485056154, 0.65362253004186666, 0.62976295383494185, 0.64804561858310816], [0.63938353888813704, 0.62445153754256155, 0.62497263749548893, 0.64045105955687953, 0.64046789607610499, 0.63786019073006761, 0.64247462906905939, 0.64305557511226874, 0.61765578867332638, 0.62095179783788979], [0.63182531739788783, 0.62945053248458149, 0.6311508321297048, 0.63274852301144313, 0.62883567853666689, 0.63062992797721906, 0.63163787602126997, 0.6297608094469398, 0.62390115350874364, 0.62585454962117748], [0.60987608282631312, 0.63847511542090152, 0.62177696768794111, 0.62909128741680487, 0.62541644136928476, 0.62850801692035185, 0.62662931200893068, 0.6430832548707871, 0.60772164565706621, 0.63368170707494731], [0.6200060813033873, 0.62124291345895677, 0.62085590509110722, 0.62568799202616221, 0.6237690099750236, 0.62277698928276293, 0.61277286808242204, 0.61378227517826045, 0.61314977529284509, 0.61141915953374981], [0.61121391064913178, 0.61021372868294477, 0.5938687005597082, 0.61544778958134083, 0.59978719924149759, 0.607624545811145, 0.61699706695589263, 0.6183985546889551, 0.61282956666005683, 0.58588782411798235], [0.5801171105546753, 0.60226817044394931, 0.6127319344698986, 0.59777166394726544, 0.58879129676974273, 0.59291963681164483, 0.58403598856934791, 0.5958317617290424, 0.59889169802140108, 0.59449514746946353], [0.56787314250188792, 0.58353349990534431, 0.58871539314095545, 0.58021194425473133, 0.5698291947472317, 0.57332995396364028, 0.59350215235813653, 0.55019545880353615, 0.56024242679643177, 0.58709762480767691]]} 
average_performances = {'R^2': [0.44323116393315054, 0.44867057331277466, 0.43683797821573, 0.4242288496264722, 0.42619222789515554, 0.4299514673416838, 0.4264129018620263, 0.4149590234584763, 0.4103094616006365, 0.3966071825745612, 0.391959415108947, 0.388343665427305, 0.37760425631375305, 0.360414813310117, 0.3435799245077287, 0.3147318910435608], 'MSE': [0.089685202036921235, 0.088173130466429578, 0.08959381284646567, 0.091499308008568425, 0.090993685397413565, 0.090947789045179694, 0.091513450947012714, 0.093065421236712853, 0.093864083466551507, 0.095805665521636288, 0.096583315384278168, 0.097252466340884608, 0.099092733140337133, 0.10169536224636869, 0.10435780286496325, 0.108977824133848], 'Rp': [0.66902474840242787, 0.67105150909346389, 0.66230165836198673, 0.65314048662591873, 0.65446104157952245, 0.65706146154378986, 0.6547150748428886, 0.64569849115514111, 0.64251799005209209, 0.63317246509817837, 0.62957952001356332, 0.62642598312533282, 0.61854629692246765, 0.60722688869486552, 0.59478544087864305, 0.57545307912795718]}
'''