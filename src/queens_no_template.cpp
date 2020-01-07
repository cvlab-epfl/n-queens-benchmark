
#include <iostream>
#include <fstream>
#include <cstdio>
#include <vector>
#include <array>
#include <string>
#include <cmath>
#include <chrono>
#include <functional>
#include <future>
#include "cxxopts.hpp"
using Clock = std::chrono::high_resolution_clock;

using QueensFunc = std::function<int(int)>;

int const MAX_N_QUEENS = 32;

/*
@param n: number of columns of the chessboard
@param i: how many queens have been placed already
@param col[k]: true if column k has no queen, false if there is a queen placed already in column k
@param dg1: TODO
*/
int allQueensAux(int n, int i, uint8_t* col, uint8_t* dg1, uint8_t* dg2)
{
	if (n == i) {
		// we have placed the n-th queen
		// so we count this one solution
		return 1;
	}

	// otherwise, there are still queens to place
	// for each j in (0 <= j < n), we try placing it on j-th column
	// and add the resulting number of available solutions
	int nsol = 0;

	for (int j = 0; j < n; j++) {
		if (col[j] && dg1[i+j] && dg2[i-j+n]) {
			col[j] = false; // the j-th column is now occupied
			dg1[i+j] = false; // the diagonals are now occupied
			dg2[i-j+n] = false;

			nsol += allQueensAux(n, i+1, col, dg1, dg2);

			// return the tables to previous state, in preparation for next j
			col[j] = true;
			dg1[i+j] = true;
			dg2[i-j+n] = true;
		}
	}

	return nsol;
}


int allQueensCol(int n, int j) {

#ifdef ALLOC_ON_HEAP
	// Allocate the tables on the heap in a usual way using a std::vector

	// We used uint8_t (byte) type instead of bool, because std::vector<bool> is implemented as a dense bit-field,
	// reducing memory size at the expense of speed. Here speed is the priority.
	// https://en.cppreference.com/w/cpp/container/vector_bool
	std::vector<uint8_t> col(n, true);
	std::vector<uint8_t> dg1(2*n, true);
	std::vector<uint8_t> dg2(2*n, true);

	/*
	An easy to make bug: forget that diagonals need 2N size:

	std::vector<uint8_t> col(n, true);
	std::vector<uint8_t> dg1(n, true);
	std::vector<uint8_t> dg2(n, true);
	*/

#else
	/*
	Put the tables on the stack using std::array
	https://en.cppreference.com/w/cpp/container/array
	The size is part of std::array's type and must be known at compile time, so we use a generous max size.
	*/
	std::array<uint8_t, MAX_N_QUEENS> col;
	col.fill(true);
	std::array<uint8_t, 2*MAX_N_QUEENS> dg1;
	dg1.fill(true);
	std::array<uint8_t, 2*MAX_N_QUEENS> dg2;
	dg2.fill(true);
#endif

	// Place the first queen at the j-th column
	col[j] = false;
	dg1[j] = false;
	dg2[n-j] = false;

	return allQueensAux(n, 1, col.data(), dg1.data(), dg2.data());
}


int allQueens_sequential(int n) {
	int nsol = 0;
	for (int j = 0; j < n; j++) {
		nsol += allQueensCol(n, j);
	}
	return nsol;
}


int allQueens_parallel(int n, int num_workers) {

	// we split tasks by the position of first queen
	// there are n such tasks, so we do not use more threads than tasks
	num_workers = std::min(n, num_workers);

	std::vector< std::future<int> > running_tasks;

	/*
	Divide tasks and start threads
	The i-th worker starts with the first queen in column i.
	If there are more columns than workers (n > num_workers),
	the i-th thread will then proceed to column (i + num_workers),
	so that all columns are covered.

	*/
	for(int first_col = 0; first_col < num_workers; first_col++) {
		/*
		Execution on threads using std::async:
		https://en.cppreference.com/w/cpp/thread/async
		It returns a std::future<result type> object from which we later extract the result.
		*/
		running_tasks.push_back(
			std::async(std::launch::async, [=]() {

			/*
			If there are fewer threads than columns, this thread finds its next task at first_col + num_workers.

			For example, with n=8 and 3 threads:
			thread 0 columns: 0 3 6
			thread 1 columns: 1 4 7
			thread 2 columns: 2 5
			*/

			int nsol = 0;
			for(int col = first_col; col < n; col += num_workers) {
				nsol += allQueensCol(n, col);
			}
			return nsol;
		}));
	}

	// wait for results
	int nsol_sum = 0;
	for(auto& f : running_tasks) {
		nsol_sum += f.get();
	}
	
	return nsol_sum;
}


struct BenchmarkResult {
	int num_queens;
	double mean, var;
	int num_sol; // number of solutions
	int num_iter;
};

BenchmarkResult run_benchmark(QueensFunc const& f, int num_queens, int num_iter) {

	std::vector<double> times;
	int nsol = 0;

	double mean = 0;
	double var = 0;

	for(int iter_idx = 0; iter_idx < num_iter; iter_idx++) {
		auto const t1 = Clock::now();

		nsol = f(num_queens);

		auto const t2 = Clock::now();
		double const dt = (double)(t2-t1).count()/1e9;
		
		mean += dt;
		var += dt*dt;
	}

	// Calulcate mean and variance
	mean /= num_iter;

	if(num_iter > 1){
		double num_iter_d = num_iter;
		var = var  / num_iter_d  - mean*mean;
		var *= (num_iter_d / (num_iter_d - 1.0));
		var = std::sqrt(var);
	} else {
		var = 0;
	}

	BenchmarkResult r;
	r.num_queens = num_queens;
	r.mean = mean;
	r.var = var;
	r.num_sol = nsol;
	r.num_iter = num_iter;
	return r;
}

void write_results_to_file(std::vector<BenchmarkResult> const& results, std::string const& file_path) {
	std::ofstream out_file;
	out_file.open(file_path, std::ios::out | std::ios::trunc);

	if(!out_file.is_open()) {
		std::cerr << "Error opening file " << file_path << "\n";
	}

	out_file << "n	mean	var\n";

	for(auto const& r : results) {
		out_file << r.num_queens << "	" << r.mean << "	" << r.var << "\n";
		out_file.flush(); //write after every row in case we abort in the middle
	}

	out_file.close();
}

int main(int arg_count, char** arg_values) {
	cxxopts::Options option_parser(
		"N Queens Benchmark", 
		"Run the benchmark, choose number of queens N and execution mode."
	);

	option_parser.add_options()
		("num_from", "Number of queens, beginning range", cxxopts::value<int>()->default_value("8"))
		("num_to", "Number of queens, end of range", cxxopts::value<int>()->default_value("14"))
 		("w,workers", "Number of threads", cxxopts::value<int>()->default_value("0"), "0 or 1 means sequential execution")
		("i,iterations", "Number of iterations", cxxopts::value<int>(), "repeat the algorithm i times")
		("o,output", "Output file", cxxopts::value<std::string>())
	;

	auto const options = option_parser.parse(arg_count, arg_values);
	int const n0 = options["num_from"].as<int>();
	int const n1 = options["num_to"].as<int>();
	int const num_workers = options["workers"].as<int>();
	int const num_iter_override = options.count("iterations") ? options["iterations"].as<int>() : 0 ;
	

	/*
	Select the function to be benchmarked: sequential or parallel
	*/
	QueensFunc func_to_run;

	if (num_workers <= 1) {
		std::cout << "Sequential \n";
		func_to_run = allQueens_sequential;
	} else {
		std::cout << "Parallel \n";

		func_to_run = [=](int n) {
			return allQueens_parallel(n, num_workers);
		};
	}

	/*
	Run benchmark
	*/
	std::vector<BenchmarkResult> results;

	for(int num_queens = n0; num_queens <= n1; num_queens++) {
		
		/* 
		If not specified, the number of iterations is adaptive to current board size
		The complexity of the task is exponential.
		We want 5 iters at n=19 and scale the num_iter for other n accordingly. 
		*/
		// num_iter =  5 * std::max(std::exp(17 - num_queens), 1.);

		int num_iter = num_iter_override;
		if(num_iter_override == 0) {
			if(num_queens <= 10) {
				num_iter = 1000;
			} else if (num_queens <= 15) {
				num_iter = 10;
			} else {
				num_iter = 5;
			}
		}

		auto result = run_benchmark(func_to_run, num_queens, num_iter);
		results.push_back(result);

		printf("%2d queens, %5d solutions time %f s per attempt. (var %f, np %d, nt %d)\n",
			result.num_queens, result.num_sol, result.mean, result.var, num_workers, result.num_iter);
	}

	/*
	Write to file if requested
	*/
	if(options.count("output")) {
		std::string const out_file_path = options["output"].as<std::string>();
		write_results_to_file(results, out_file_path);
	}
}
