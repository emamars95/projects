#!/usr/bin/env python3

def MAX_CHANNEL(molecule_class) -> int:
	max_channel = max( molecule_class.dic_reactivity, key=lambda k: molecule_class.dic_reactivity[k][0] )
	index_max_channel = molecule_class.dic_reactivity[max_channel][0]
	return index_max_channel

def WRITE_HEADER(fp, index_max_channel: int) -> None:
	fp.write(f'{"Ewindow (eV)":15}')
	for i in range(0, index_max_channel + 1):
		fp.write(f'{"QY:":<3}{i:<9}{"Err:":<4}{i:<8}')
	fp.write(f"\n")

# -------------------------------------------------------------------------------------	#
def WRITE_QY_FILE(qy_result: dict, molecule_class, name_file: str) -> None:
	index_max_channel = MAX_CHANNEL(molecule_class)
	# We double because we have for each channel QY, Number of trajectories
	fp = open(name_file, 'w')
	WRITE_HEADER(fp, index_max_channel)
	for window, reactivity_window in qy_result.items():
		fp.write(f"{window:<15.1f}")
		for i in range(0, index_max_channel + 1):
			if i in reactivity_window.keys():
				fp.write(f"{reactivity_window[i][0]:<12.2f}{reactivity_window[i][1]:<12.2f}")
			else:
				fp.write(f'{0:<12.2f}{0:<12.2f}')		
		fp.write(f"\n")
