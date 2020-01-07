
from pathlib import Path
from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
import pandas

Row = namedtuple('PlotRow', ['name', 'file_path', 'color'])

FORMATS = ['.pdf', '.svg', '.png']

def draw_benchmarks_plots(out_path, rows):
	out_path = Path(out_path)
	fig, plot = plt.subplots(1, figsize=(8, 6))

	for row in rows:
		d = pandas.read_csv(row.file_path, sep='\t')
		plot.errorbar(d['n'], d['mean'], d['var'], label=row.name, color=row.color, capsize=2)

	plot.legend()
	plot.set_xlabel('number of queens')
	plot.set_ylabel('time [s]')
	fig.tight_layout()

	# Save plot
	for ext in FORMATS:
		fig.savefig(out_path.with_suffix(ext))

	# Save plot in logarithmic scale
	plot.set_yscale('log')

	out_path_log = out_path.parent / f'{out_path.stem}_log'
	for ext in FORMATS:
		fig.savefig(out_path_log.with_suffix(ext))


draw_benchmarks_plots('../data/plots/sequential', [
	Row('Python', '../data/python_pure.csv', 'r'),
	Row('Numba', '../data/python_numba_seq.csv', 'g'),
	Row('C++ stack', '../data/cplus_at_stack.csv', 'm'),
	Row('C++ heap', '../data/cplus_at_new.csv', 'b'),
])

draw_benchmarks_plots('../data/plots/parallel', [
	Row('Numba Para', '../data/python_numba_para.csv', 'r'),
	Row('Numba Pool', '../data/python_numba_pool.csv', 'b'),
	Row('C++ stack', '../data/cplus_para_stack.csv', 'm'),
	Row('C++ heap', '../data/cplus_para_new.csv', '#ff00ff'),
])

draw_benchmarks_plots('../data/plots/sequential_cpp_array_types', [
	Row('vector<uint8_t>', '../data/cplus_at_vbyte.csv', 'r'),
	Row('vector<bool>', '../data/cplus_at_vbool.csv', 'b'),
	Row('new bool[n]', '../data/cplus_at_new.csv', 'g'),
	Row('array<bool, 32>', '../data/cplus_at_stack.csv', 'm'),
])

draw_benchmarks_plots('../data/plots/sequential_with_julia', [
	Row('Python', '../data/python_pure.csv', 'r'),
	Row('Numba', '../data/python_numba_seq.csv', 'g'),
	Row('C++ stack', '../data/cplus_at_stack.csv', 'm'),
	Row('C++ heap', '../data/cplus_at_new.csv', 'b'),
	Row('Julia', '../data/julia_seq.csv', 'k'),
])

draw_benchmarks_plots('../data/plots/parallel_with_julia', [
	Row('Numba Para', '../data/python_numba_para.csv', 'r'),
	Row('Numba Pool', '../data/python_numba_pool.csv', 'b'),
	Row('C++ stack', '../data/cplus_para_stack.csv', 'm'),
	Row('C++ heap', '../data/cplus_para_new.csv', '#ff00ff'),
	Row('Julia', '../data/julia_para.csv', 'k'),
])
