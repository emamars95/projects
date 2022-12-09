#!/usr/bin/env python3

# -------------------------------------------------------------------------------------	#
def WRITE_QY_FILE(qy_result: dict, molecule_class, name_file: str):
	index_max_channel = MAX_CHANNEL(molecule_class)
	fp = open(name_file, 'w')
	fp.write(f'{"Ewindow (eV)":15}')
	for i in range(0, index_max_channel + 1):
		fp.write(f'{i:<15}')
	fp.write(f"\n")
	for window, reactivity_window in qy_result.items():
		fp.write(f"{window:<15}")
		for i in range(0, index_max_channel + 1):
			if i in reactivity_window.keys():
				fp.write(f"{reactivity_window[i]:<15.2f}")
			else:
				fp.write(f'{0:<15.2f}')
		fp.write(f"\n")

def MAX_CHANNEL(molecule_class) -> int:
	max_channel = max( molecule_class.dic_reactivity, key=lambda k: molecule_class.dic_reactivity[k][0] )
	index_max_channel = molecule_class.dic_reactivity[max_channel][0]
	return index_max_channel