"""
Test the performance of BNMF for recovering the GDSC dataset, where we vary the 
fraction of entries that are missing.
We repeat this 10 times per fraction and average that.
"""

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)

from HMF.code.models.bnmf_gibbs import bnmf_gibbs
from HMF.code.generate_mask.mask import try_generate_M_from_M
from HMF.drug_sensitivity.load_dataset import load_data_without_empty

import numpy, matplotlib.pyplot as plt, random

''' Settings '''
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
repeats = 20
iterations, burn_in, thinning = 1000, 900, 2

init_UV = 'random'
K = 4

alpha, beta = 1., 1.
lambdaU = 1.
lambdaV = 1.
priors = { 'alpha':alpha, 'beta':beta, 'lambdaU':lambdaU, 'lambdaV':lambdaV }

metrics = ['MSE', 'R^2', 'Rp']

''' Load data '''
location = project_location+"DI_MMTF/data/datasets_drug_sensitivity/overlap/"
location_data = location+"data_row_01/"
R, M_original, _, _ = load_data_without_empty(location_data+"gdsc_ic50_row_01.txt")

#''' Seed all of the methods the same '''
#numpy.random.seed(0)
#random.seed(0)

''' Generate matrices M - one list of (M_train,M_test)'s for each fraction '''
M_attempts = 1000
all_Ms_train_test = [ 
    [try_generate_M_from_M(M=M_original,fraction=fraction,attempts=M_attempts) for r in range(0,repeats)]
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
    
        BNMF = bnmf_gibbs(R,M_train,K,priors)
        BNMF.initialise(init_UV)
        BNMF.run(iterations)
    
        # Measure the performances
        performances = BNMF.predict(M_test,burn_in,thinning)
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
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.5846345522300793, 0.5942845369204632, 0.5967828084841125, 0.575695253016793, 0.544815805245646, 0.6198404010787207, 0.5756607200910788, 0.5554006218554062, 0.5968725914028101, 0.6177972382789085], [0.5848045488077691, 0.5528571632595023, 0.5791212963665022, 0.5832191421562236, 0.583993343354057, 0.5689999266090211, 0.5871910437005814, 0.6207451989438963, 0.5950782498168863, 0.6187414847726322], [0.5953312125837116, 0.5939134205718626, 0.5823924111133445, 0.6032876828049853, 0.5883807060448685, 0.5678237341118515, 0.5954472016308366, 0.57077148779742, 0.5901596061768271, 0.5503170086487094], [0.5648838074552875, 0.5833633437389492, 0.5754860322906525, 0.569870169026388, 0.5689639519895772, 0.57700720913542, 0.5523546378582265, 0.5649454371445362, 0.5823217661149727, 0.5813343998072851], [0.5791535127955474, 0.5587723098629243, 0.5514246094828226, 0.5765186685736767, 0.5658519543990794, 0.5549905823589746, 0.5645006240818444, 0.5769584649696412, 0.5985086556816717, 0.5773754986749559], [0.5704486714303144, 0.5665484630956028, 0.5518884579463543, 0.5671689104588351, 0.5680230128345231, 0.5651978275856776, 0.5539240299017227, 0.5540543414163626, 0.5597465571434659, 0.5629678489377115], [0.555812595652813, 0.5361015272889333, 0.562052743569791, 0.5346868192974649, 0.5508481980926457, 0.5431242969272196, 0.5618237326004156, 0.5514326555148268, 0.5306195645348329, 0.5506720422538041], [0.5276748350983613, 0.5416412852686505, 0.5363537643592209, 0.544598726698976, 0.5337493315875541, 0.5412648077252527, 0.5351989118763438, 0.5368353410029902, 0.5333529945704704, 0.5358146339158685], [0.5253806042705447, 0.5106966545691362, 0.5138607719592024, 0.5156148497105983, 0.5115145656961946, 0.513067334430612, 0.5096015186048631, 0.5356057678016655, 0.5226983654401478, 0.5294301943848521], [0.5103497314192051, 0.521498377234753, 0.5107484151968089, 0.4878350191601686, 0.502061174491781, 0.49310443997340014, 0.4947357919974972, 0.5035924525128428, 0.502164156821484, 0.5180257579408031], [0.4836674773477043, 0.45017660915627555, 0.48354408326392806, 0.4545770241509475, 0.4498748129668815, 0.48286147496938836, 0.47773527508332925, 0.456063643289931, 0.4622365291651098, 0.45502561128619134], [0.43968734830350564, 0.4243162689639731, 0.4318276162775032, 0.4508208048899912, 0.4215516035776887, 0.42918908440280157, 0.4199568628085425, 0.43392453902126593, 0.42111199358927864, 0.4440182816481033], [0.38335516212462817, 0.36213864310641763, 0.362736189461766, 0.40995498394197816, 0.3474867051109478, 0.36392903749187233, 0.36728373475700216, 0.4037044985496594, 0.40361886568035077, 0.3854475647439505]], 'MSE': [[0.081364981348119605, 0.078522116323120658, 0.080209148868228913, 0.084121837103334721, 0.090009299687818359, 0.078007565014955815, 0.084649955297776566, 0.088975926987693604, 0.08039609894165374, 0.074438665045198305], [0.082346570379071213, 0.089912361369804891, 0.084149746543125584, 0.083787146826903053, 0.083323948310340124, 0.085570085884178124, 0.08227642893830095, 0.075368132680844274, 0.081048517126663763, 0.075729809202614073], [0.080385129022992302, 0.082516784470227242, 0.083029373506517484, 0.07875045832554721, 0.082146816262046063, 0.087589312498961985, 0.080827306460122025, 0.085678841146367854, 0.081808937856939809, 0.088858999821109105], [0.087278930116607936, 0.08292627053580591, 0.083901465090280292, 0.086125263505348687, 0.085346529691370951, 0.084010813964591466, 0.08883060670758347, 0.086878846081613267, 0.082896157837946891, 0.083005955639420273], [0.084295817645639232, 0.088312891921503031, 0.08956186765557117, 0.08476496453803041, 0.086492077705349946, 0.088248897761123074, 0.086598136653238733, 0.084566539277739966, 0.079746429145574713, 0.084390533995412798], [0.085543606843626677, 0.086390243926929275, 0.089511681938478596, 0.086772143966176274, 0.086074051601854523, 0.087230057994447552, 0.088315468524597721, 0.089091795632983029, 0.087882437109603653, 0.08667794924923114], [0.08871454164542264, 0.092180941830780655, 0.087111916690036553, 0.092529581739133948, 0.089395762595519804, 0.091501380972042773, 0.087428437264423231, 0.08921739442237106, 0.093997163557297717, 0.089307379967819081], [0.094212982815813029, 0.091739514472933853, 0.092366177416828801, 0.091233957597764176, 0.09285806583390209, 0.091510797247703696, 0.092543777469299121, 0.092790014936696863, 0.093393572687923782, 0.092750184515271672], [0.09445498612493744, 0.098304982988951489, 0.096992789883146829, 0.096985512011493955, 0.097488056885255428, 0.097078077295639109, 0.097346924376941757, 0.092819519999972691, 0.095596950936268521, 0.093561121032465611], [0.09804106992087408, 0.095571050968612403, 0.097355052581156606, 0.1021609657584665, 0.099095277621566794, 0.10033583004854234, 0.10070913192735588, 0.099111400410233863, 0.09943950491597349, 0.095956166629022968], [0.10287884759412361, 0.10956609685643583, 0.10294888780218728, 0.10885098115578558, 0.10960805512113191, 0.10289235396429897, 0.1044097813048164, 0.10839176868708639, 0.10726578674018998, 0.10899584833837676], [0.11192214943398809, 0.11503487895464549, 0.1129759057437926, 0.1093841685093087, 0.1151456997337225, 0.11378414284598436, 0.11577606543740233, 0.1130243808798623, 0.11552054559473154, 0.11100808426430875], [0.12296158690757167, 0.1270295352081294, 0.12690838785745831, 0.11753035483865457, 0.13017913425278108, 0.12694289342867984, 0.12629991572740565, 0.11896182980942632, 0.11897509076280822, 0.12242902234515163]], 'Rp': [[0.76476437931452734, 0.77097947475549422, 0.77263661675526341, 0.75908460441375536, 0.7421714401152234, 0.78755075185068701, 0.7605384231262089, 0.7461119425562226, 0.77474140091897714, 0.78621451407986276], [0.76496255134698599, 0.74420764816633478, 0.76131677234053963, 0.76380128224902355, 0.76426174628415744, 0.7556994345867577, 0.76639633218401593, 0.78865527620937936, 0.77143394466927673, 0.78662050667044392], [0.77233112680802507, 0.7707939510570474, 0.76468390400146269, 0.77718179037570234, 0.76715349425863399, 0.75411044605894317, 0.77171666337323364, 0.75587731024967875, 0.76888050874970804, 0.74324358730657802], [0.75230449803589317, 0.76425019917535875, 0.7594680210134408, 0.75570678865923102, 0.75527548601961347, 0.75988084364100184, 0.7442198776468929, 0.75341591940905905, 0.76334799776923135, 0.76269501022598274], [0.76171770700445796, 0.74879581600480483, 0.74341203322836136, 0.75940853513227213, 0.75320960765003686, 0.74570297278325792, 0.75215936831619712, 0.7601773437606878, 0.77388253686256714, 0.76005918915146531], [0.75551271489481331, 0.75361039296696064, 0.7437329419354054, 0.75342423909068912, 0.75446057801780619, 0.75322803146405404, 0.74515455383659635, 0.74504890651010969, 0.75027193650000035, 0.7507942025164962], [0.74612492060178348, 0.73350302710297854, 0.75069517301240862, 0.73258960440385146, 0.74448268944866969, 0.73723754875991943, 0.75022124103878485, 0.74370803750386516, 0.73066250236026364, 0.74321665504306356], [0.72822868567007237, 0.73758556570105238, 0.73378159290564415, 0.73879602404029809, 0.73223626717491097, 0.73720372979240423, 0.73397396721057617, 0.73348960376861094, 0.73180409826496551, 0.7338948367804532], [0.73021951586101563, 0.71766049752279482, 0.7185353986360915, 0.72074323656237282, 0.71874308078915172, 0.7184598417474376, 0.71805779214177101, 0.73269551744302552, 0.72542842876752545, 0.72892718473810247], [0.71603617016968724, 0.72405592711795164, 0.71677295008700226, 0.70693145150066261, 0.71285759473431853, 0.70812982640779054, 0.7079887403195031, 0.7123777123674917, 0.71302446994431068, 0.72212097597834235], [0.70006376536728032, 0.67929161181227804, 0.70134848737315902, 0.6867790467151057, 0.68000023635116735, 0.70033058133606152, 0.69511972739435035, 0.6837599587549702, 0.6863299436080843, 0.68087626819734204], [0.67711051836399105, 0.66607613447126224, 0.67304473478184801, 0.67976118624770521, 0.66460142294545643, 0.67065974529707173, 0.66083810307959445, 0.66846106566106356, 0.66240057682203846, 0.67501117637551544], [0.65306995219664954, 0.63182597878439306, 0.63657096549245984, 0.65771020223449794, 0.62913174895304957, 0.63272481876287112, 0.63712119751600371, 0.65082171760271357, 0.6516713055838691, 0.64915606869247233]]} 
average_performances = {'R^2': [0.5861784528604019, 0.5874751397787072, 0.5837824471484417, 0.5720530754561295, 0.5704054880881138, 0.561996812075057, 0.5477174175732745, 0.5366484632103689, 0.5187470626867816, 0.5044115316748744, 0.4655762540679687, 0.4316404403482654, 0.37896553849685727], 'MSE': [0.082069559461790037, 0.082351274726184601, 0.083159195937083097, 0.085120083917056916, 0.085697815629918295, 0.08734894367879284, 0.090138450068484754, 0.092539904499413711, 0.096062892153507301, 0.098777545078180484, 0.10658084075644325, 0.11335760213977468, 0.12382177511380665], 'Rp': [0.76647935478862217, 0.76673554947069156, 0.76459727822390133, 0.75705646415957051, 0.75585251098941086, 0.75052384977329312, 0.74124413992755889, 0.73409943713089876, 0.72294704942092891, 0.71402958186270604, 0.68938996269097974, 0.6697964664045547, 0.64298039558189801]}

1000 iterations
repeats=10 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.5923533943294081, 0.5991350843196055, 0.6007044498912247, 0.5744902174090325, 0.5501470878750272, 0.6186899830827047, 0.5820741952740597, 0.5565382957700464, 0.592445919147702, 0.6102212540751321], [0.5843584200471561, 0.5577209747229808, 0.5867989811984127, 0.5880021347153404, 0.5870678143732664, 0.5741903317303563, 0.5942733956215251, 0.6213643257799004, 0.6032580528387865, 0.6237180650482266], [0.5982749104309668, 0.6030913585516778, 0.5840712914869829, 0.611932135248803, 0.5952274456558648, 0.5725260293272678, 0.6011691992800176, 0.5729982350891835, 0.600374624877186, 0.557317627952185], [0.5719512931666189, 0.5884006829657022, 0.5851269371092542, 0.5765511168285826, 0.58231337582395, 0.5847597607117514, 0.5561614199833786, 0.5932868088607928, 0.5914669907387123, 0.5867235882178172], [0.5831027017288415, 0.56227589016256, 0.5568972815663149, 0.5869045476656923, 0.5765204541670509, 0.5629303559448242, 0.5797881630253932, 0.5807442736203889, 0.6062434442158906, 0.5857398024770943], [0.5805980010079161, 0.575207716305278, 0.5605719374054928, 0.5780837095027225, 0.5775776592156647, 0.5765878771950708, 0.5631313974080776, 0.5570709572597301, 0.5708044056153928, 0.566630256868627], [0.5658801441299577, 0.5551078793712377, 0.5681087323911298, 0.5517856961448194, 0.5543975658172542, 0.553179178667723, 0.5642047283299937, 0.5571100141228819, 0.540731518648598, 0.5622544836669048], [0.5491022290555071, 0.5525235753375504, 0.5449311684398249, 0.5587562654876947, 0.5470959428284891, 0.5584695000498993, 0.5438336271217057, 0.5527372596151212, 0.5434879943994753, 0.5452329142742753], [0.5360160971503218, 0.525707115705761, 0.5350982402990041, 0.5356828205948614, 0.5256106136094455, 0.5270553724185051, 0.524102670805259, 0.5429055514040031, 0.5371084505738861, 0.5431299134532274], [0.5289388446547849, 0.5336832860000369, 0.5189149004869333, 0.5149555246051865, 0.5116249439284463, 0.5070004243344017, 0.5198758476400127, 0.5190006730196616, 0.5011354537737912, 0.5289367962401653], [0.5015513776943872, 0.4716554627523245, 0.4961481781612942, 0.47355336027117734, 0.4809833940847442, 0.5000891774682077, 0.49197597287519645, 0.4895150790084094, 0.4989098407917405, 0.48014273522670126], [0.4840496017388276, 0.4326627484792339, 0.4494322967868375, 0.4584426795053915, 0.4465913505184592, 0.43959519010410697, 0.452278324729367, 0.46009668986368224, 0.43501290003661597, 0.4646169973079257], [0.4150869435002872, 0.3886654496639256, 0.39577072562226356, 0.4297009623319413, 0.3996643743582582, 0.4149680253058745, 0.400194075326325, 0.4517814299376899, 0.43729084905343696, 0.41118087150880533]], 'MSE': [[0.079852955138879259, 0.077583342029887481, 0.079429044433077398, 0.084360745128334413, 0.088955078075032806, 0.078243627202713911, 0.08337055361792442, 0.088748248776385083, 0.081278914580119932, 0.075914180679865981], [0.082435052016522792, 0.088934336591130717, 0.08261468376359879, 0.082825602427057027, 0.082708147913414562, 0.084539590904184406, 0.080864854369369077, 0.075245095521150385, 0.079411260286265814, 0.074741305445452086], [0.079800380362817322, 0.080651827664149023, 0.082695575967092455, 0.077034467764080988, 0.080780413206896995, 0.086636296709816207, 0.079684084464330993, 0.085234357329332752, 0.079769900605707572, 0.087475651904022261], [0.085861279838203228, 0.081923651709015458, 0.081996024750021698, 0.084787531619543263, 0.082703300655419296, 0.082471075741396574, 0.088075190044350493, 0.081219175131566304, 0.081081114768018367, 0.081937478234228145], [0.083504792603751654, 0.087611641036174623, 0.088469202424206222, 0.082686103895069266, 0.084366672051032862, 0.086674377673125039, 0.083558241627593649, 0.083809751327974025, 0.078210102710325247, 0.082720332523067389], [0.083522404250670659, 0.084664387785429701, 0.087777129760010772, 0.084583991273628062, 0.084170229986160847, 0.084944985032483961, 0.086492566082615144, 0.088489130897835444, 0.085675093388231954, 0.08595157246437847], [0.08670381837884196, 0.088404202870043747, 0.085907322333217406, 0.089129394535096593, 0.088689323406974038, 0.089487626336856849, 0.086953361932284243, 0.088088201340352515, 0.091972164360700381, 0.087005280847561192], [0.089938938473728011, 0.089561447436814226, 0.090657413350212449, 0.088397671514995849, 0.090199966684167646, 0.08807871892115815, 0.090824570723455761, 0.089604238049623766, 0.09136517899374158, 0.090868291407722762], [0.092338394722583844, 0.095289260451038207, 0.09275556485476566, 0.092967423451018549, 0.094674879205182291, 0.094289330659766676, 0.094468362105267364, 0.091360495828063354, 0.092710809130389815, 0.090837272076216766], [0.094319032647660991, 0.093137361130895491, 0.095730022372735049, 0.096751269407151078, 0.09719198280122876, 0.097585233603922655, 0.095698222505585351, 0.096035036402492807, 0.099644981727596796, 0.093783889943289483], [0.099315494565916471, 0.10528589671824491, 0.10043642253770242, 0.10506384182192544, 0.10340991848918447, 0.099464647890002464, 0.10156281869918748, 0.10172580448388654, 0.09995069035052373, 0.10397237881685086], [0.10306081327964041, 0.11336705996138068, 0.10947537530118041, 0.10786606217041005, 0.11016129801269951, 0.11170981352740612, 0.10932473199262316, 0.10779876813179515, 0.11274653701401414, 0.10689531600552432], [0.11663413558762122, 0.12174674472217376, 0.12032969994450937, 0.11359717722737113, 0.11976947078209615, 0.11675686518234596, 0.11973050465201732, 0.10937041126672135, 0.11225769638622908, 0.11730252148340431]], 'Rp': [[0.76978818999819942, 0.77418322299977649, 0.77512000934701486, 0.75824463203399994, 0.74612936676431174, 0.78682627886802581, 0.76441821017553047, 0.7470059190320224, 0.77203795875798231, 0.78135134075136958], [0.76474205576364407, 0.74721527739896154, 0.76622351022162871, 0.76699802956663143, 0.76625127176749408, 0.75882806754243237, 0.77091007200076656, 0.78920942816202655, 0.77675031750472878, 0.78981480432890605], [0.77422917968603322, 0.77676953903346546, 0.76546693907398511, 0.78261267704885784, 0.77168655608717396, 0.75715843764408775, 0.77545933944388556, 0.7572798571261049, 0.7756154980479335, 0.7477675770679304], [0.75660548028061791, 0.76758434809676879, 0.76587767123507156, 0.76009843635278351, 0.76367440463408975, 0.76481270707151872, 0.74660825896239913, 0.77124563296908055, 0.7691954705012698, 0.76611652797066865], [0.76441583784042355, 0.750932108450866, 0.74680254058915163, 0.76614090320645434, 0.76026410934947553, 0.75071729221909289, 0.76177200748695284, 0.76249402819933487, 0.77893372874086741, 0.76542678088324789], [0.76213286556481408, 0.75909129240504747, 0.74917061454460265, 0.76046059571736657, 0.76073900084542478, 0.76016347222171043, 0.75118220932124458, 0.7469941554069095, 0.75763291623944218, 0.75301962564125402], [0.75265056720158108, 0.74592561555851999, 0.75468733106531394, 0.74350405277597387, 0.7467011937434036, 0.74396887697459713, 0.75164164334504535, 0.74726927401446719, 0.73719475752002894, 0.7504683348430965], [0.74181541796304884, 0.74405963054750113, 0.73916294461731724, 0.74779927999884821, 0.74066837963424803, 0.74849513661424705, 0.73933806982543016, 0.7439066615316221, 0.73799781983427637, 0.73935311909117829], [0.73551762941742471, 0.72632605611831114, 0.73226013065303519, 0.73283704081901935, 0.72709722990795855, 0.72698186105774187, 0.7265171854800988, 0.73764160037607884, 0.73417085597847365, 0.73749633088253796], [0.72807375058215651, 0.73240494428804737, 0.72105277431038084, 0.72169650680681274, 0.71880505465620292, 0.71634423473219633, 0.72268765963910775, 0.72181570615749258, 0.71208716436466712, 0.72840023745625249], [0.7121358264919494, 0.69141912079910095, 0.70827945201841525, 0.69561110810939719, 0.69693750711151181, 0.71105115244602457, 0.70359899992735819, 0.70299447946037219, 0.70800257960340751, 0.69609156763467273], [0.7011077562079765, 0.67117224960623878, 0.68112015246844215, 0.68490883826420601, 0.68118868817967815, 0.67473072239543097, 0.67994682139467499, 0.68354169493301153, 0.67249602304764866, 0.68679050108907247], [0.66509722088394363, 0.64905893855434382, 0.6545135485967537, 0.67042849395764947, 0.65313568766361918, 0.65924106679421379, 0.65419563038120332, 0.67678802544474737, 0.67205575810274776, 0.66337126615297015]]} 
average_performances = {'R^2': [0.5876799881173943, 0.5920752496075952, 0.5896982857900135, 0.581674197440656, 0.578114691457405, 0.5706263917783972, 0.55727599412905, 0.5496170476609543, 0.5332416846014273, 0.518406669468342, 0.4884524578334183, 0.45227787790704477, 0.4144303706608807], 'MSE': [0.081773668966222082, 0.081431992923814561, 0.081976295597824655, 0.083205582249176291, 0.084161121787232007, 0.0856271490921445, 0.088234069634192891, 0.089949643555562037, 0.09316917924842924, 0.095987703254255846, 0.10201879143734247, 0.1092405775396674, 0.11674952272344896], 'Rp': [0.76751051287282324, 0.7696942834257221, 0.7684045600259457, 0.76318189380742674, 0.76078993369658665, 0.75605867479078159, 0.74740116470420281, 0.74225964596577165, 0.731684592069068, 0.72233680329933159, 0.70261217936022091, 0.68170034475863805, 0.66178856365321936]}


'''