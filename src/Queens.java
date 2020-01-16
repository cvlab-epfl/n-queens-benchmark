
class Queens {
	
	public static void main(String[] args){
		
		// b.col = new boolean[n];
		// b.dg1 = new boolean[2*n];
		// b.dg2 = new boolean[2*n];
		
		// for (int i=0;i<2*n;i++){
		// 	b.dg1[i] = true;
		// 	b.dg2[i] = true;	
		// }
		// for (int i=0;i<n;i++){
		// 	b.col[i] = true;	
		// }
		
		//System.out.print("n= " + n + ", found " + nsol + " solutions.\n");

		System.out.println("n	mean	var");

		for (int num_queens = 8; num_queens <= 16; num_queens++) {
			int num_iter = 5;
			if(num_queens <= 10) {
				num_iter = 1000;
			} else if (num_queens <= 15) {
				num_iter = 10;
			}

			int nsol = 0;
			double mean = 0;
			double var = 0;


			for (int iter_idx = 0; iter_idx < num_iter; iter_idx++) {

				double t1 = System.nanoTime();

				Board b = new Board(num_queens);
				nsol = b.allQueensRec();

				double t2 = System.nanoTime();
				double dt = (t2 - t1) * 1e-9;

				mean += dt;
				var += dt*dt;
			}

			mean /= num_iter;

			if(num_iter > 1){
				double num_iter_d = num_iter;
				var = var  / num_iter_d  - mean*mean;
				var *= (num_iter_d / (num_iter_d - 1.0));
				var = Math.sqrt(var);
			} else {
				var = 0;
			}

			//System.out.println(String.format("%d %d", num_queens, nsol));

		
			// println(s"$num_queens queens, $nsol solutions time $t_mean s per attempt. (var $t_var, nt $num_iter)")
			System.out.println(String.format("%d	%f	%f", num_queens, mean, var));
		}



	}
	
}


class Board {

	protected int n;
	protected boolean col[],dg1[],dg2[];

	public Board(int n) {
		this.n = n;
		col = new boolean[n];
		dg1 = new boolean[2*n];
		dg2 = new boolean[2*n];
	}

	int addQueensRecursive(int n, int i) {

		if (n == i) {
			return 1;
		}

		int nsol = 0;
		for (int j = 0; j < n; j++) {
			if (col[j] && dg1[i+j] && dg2[i-j+n]) {
				col[j] = false;
				dg1[i+j] = false;
				dg2[i-j+n] = false;

				nsol += addQueensRecursive(n, i+1);

				col[j] = true;
				dg1[i+j] = true;
				dg2[i-j+n] = true;
			}
		}
		return nsol;
	}

	public int allQueensRec() {
		for (int i=0;i<2*n;i++){
			dg1[i] = true;
			dg2[i] = true;	
		}
		for (int i=0;i<n;i++){
			col[i] = true;	
		}
		return addQueensRecursive(n, 0);
	}
}

