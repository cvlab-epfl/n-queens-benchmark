using Base.Threads
using Printf, Statistics

function allQueensAux(n, i, col, dg1, dg2)
	# All rows are filled. Increment the counter and stop the recursion
	if n == i
		return 1
	end

	# Try putting a queen in each cell of row i
	nsol = 0

	for j = 0:n-1
		if (col[j+1] && dg1[i+j+1] && dg2[i-j+n+1])

			col[j+1]     = false  # Mark column j as occupied
			dg1[i+j+1]   = false  # Mark diagonal i+j as occupied
			dg2[i-j+n+1] = false  # Mark diagonal i-j as occupied

			nsol += allQueensAux(n,i+1,col,dg1,dg2)
			
			col[j+1]     = true   # Unmark column j
			dg1[i+j+1]   = true   # Unmark diagonal i+j
			dg2[i-j+n+1] = true   # Unmark diagonal i-j
		end
	end
	return nsol
end

function allQueens(n)
    col = ones(Bool, n)
    dg1 = ones(Bool, 2*n)
    dg2 = ones(Bool, 2*n)
    
    # Fills the rest of the board starting with the second row
	return allQueensAux(n,0,col,dg1,dg2)
end


function allQueensCol(n, j)
    col = ones(Bool, n)
    dg1 = ones(Bool, 2*n)
    dg2 = ones(Bool, 2*n)
    # Put a queen in cell j of the first row
    col[j+1] = false
    dg1[j+1] = false
    dg2[n-j+1] = false
    # Fills the rest of the board starting with the second row
	return allQueensAux(n,1,col,dg1,dg2)
end

function allQueensCoroutine(n)
	jobs = Channel{Int}(n);
	results = Channel{Int}(n);

	function worker() 
		for first_queen in jobs
			nsol = allQueensCol(n, first_queen)
			put!(results, nsol)
		end
	end

	for j in 0:n-1
		@async put!(jobs, j)
	end

	# for j in 0:1
		@async worker()
	# end

	nsol = 0
	for nsol_part in results
		nsol += nsol_part
	end
	return nsol
end

function allQueensThreads(n)
	nsols = zeros(Int, n)
	Threads.@threads for j = 0:n-1
		nsols[j+1] = allQueensCol(n, j)
	end
	return sum(nsols)
end


function benchmark(func, n0=8, n1=14, out_file_path="")
	out_file = if (length(out_file_path) > 0) open(out_file_path, "w") else nothing end

	if out_file != nothing
		write(out_file, "n	mean	var\n")
	end

	for n = n0:n1

		if n <= 10
			num_iter = 1000
		elseif n <= 15
			num_iter = 10
		else
			num_iter = 5
		end

		times = zeros(Float64, num_iter)
		nsol = 0

		for iter = 1:num_iter
			times[iter] = @elapsed nsol =  func(n)
		end

		times_mean = Statistics.mean(times)
		times_var = Statistics.std(times, mean=times_mean)

		println("$n queens, $nsol solutions time $times_mean s per attempt. (var $times_var, nt $num_iter)")

		if out_file != nothing
			write(out_file, "$n	$times_mean	$times_var\n")
			flush(out_file)
		end
	end
end


n0, n1, variant, out_file_path = ARGS
n0 = parse(Int, n0)
n1 = parse(Int, n1)

if variant == "seq"
	println("sequential")
	benchmark(allQueens, n0, n1, out_file_path)

elseif variant == "thread"
	println("threads ", Threads.nthreads())
	benchmark(allQueensThreads, n0, n1, out_file_path)

else
	println("No variant $variant")
end
