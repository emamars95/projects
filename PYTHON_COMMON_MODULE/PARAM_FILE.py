class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ev_au_conv = 27.211324570273
#thresh_d1 = 0.075
thresh_d1 = 0.05
# ------------------------------------------------------------------------------------- #
# This section contain general folder definition 
# ------------------------------------------------------------------------------------- #
plot_traj_script = "PLOT_TRAJ.py"
# -------------------------------------------------------------------------------------	#
# This section contain common files definition within the script suite
# Turbomole file containing the d1 diagnostic from dynamics or LIIC
d1_file = "d1_values"
# PLOT_TRAJ.py generate this name
gnuplot_file_traj = "gnuscript_traj.gp"
# These three file are created for trajectories analysis
to_submit_file = "TO_SUBMIT"
dont_analyze_file = "DONT_ANALYZE"
error_dyn = "ERROR"
# These two file are for analysis of dynamics
summary_file = "summary.out"
traj_file = "trajectory.dat"
summary_file_restart = "summary_restart.out"
traj_file_restart = "trajectory_restart.dat"
# These files contains the trajectories in curvilinear coordinates
coordinate_file	= "COORDINATES.out"
coordinate_file_to_use = "COORDINATES_to_use.out"
# General parameter imputs for scripts
input_for_traj = "INPUT_plot_traj.in"
input_for_zoom = "INPUT_plot_zoom.in"
# File for analysis of QY
qy_file	= "QY.dat"
qy_file_restart = "QY_restart.dat"
# ------------------------------------------------------------------------------------- #

viridis = ['#440154', '#472c7a' ,'#3b518b', '#2c718e', '#21908d', '#27ad81', '#5cc863','#aadc32', '#fde725']    # Viridis palette
shadeofblue     = ["#084594","#2171B5","#9ECAE1","#C6DBEF"]
shadeofgreen    = ["#005A32","#238B45","#A1D99B","#C7E9C0"]
shadeofgrey     = ["#808080","#A9A9A9","#C0C0C0","#DCDCDC", "#F5F5F5"]

class BH3NH3:
    # Name of the molecule
    molecule	= "BH3NH3"
    # Reactivity of the molecule
    reactivity	= ["BHDISSBHDISS"	, "NHDISSBHDISS"	, "BHDISS"        	, "NHDISS"  	, "BNDISS"	]
    # Type of distinct (expected) reaction channel. Here BHdiss is expected to give the same result as NHdissBHdiss
    duplicate	= [1    		, 1			, 0		        , 1		, 1		]	
    # Label assigned to each reaction channel 
    labels	= ["2 x B-H diss"	, "B-H + N-H diss"	, ""			, "N-H diss"	, "B-N diss"	]
    # Number or atoms
    natoms	= 8
    # Restart Folder Template
    restart_template = "/ddn/home/fzzq22/CODE_AND_SCRIPT/TEMPLATE_RESTARTs/NX_UMP2"
	
