import scala.math.sqrt

object Main {
	def allQueensRecursive(n : Int, i : Int, col : Array[Boolean], diag1 : Array[Boolean], diag2 : Array[Boolean]) : Int = {
		if( n == i) {
			1
		} else {
			var nsol : Int = 0

			for { 
				j <- 0 to n-1 
				if col(j) && diag1(i+j) && diag2(i-j+n) 
			} { // for each element from the above sequence, create

				col(j) = false
				diag1(i+j) = false
				diag2(i-j+n) = false

				nsol += allQueensRecursive(n, i+1, col, diag1, diag2)

				col(j) = true
				diag1(i+j) = true
				diag2(i-j+n) = true
			}

			nsol
		}
	}

	def allQueensRec(n : Int) : Int = {
		val col = Array.fill[Boolean](n){true}
		val diag1 = Array.fill[Boolean](2*n){true}
		val diag2 = Array.fill[Boolean](2*n){true}

		allQueensRecursive(n, 0, col, diag1, diag2)
	}

	def allQueensClosure(n : Int) : Int = {
		val col = Array.fill[Boolean](n){true}
		val diag1 = Array.fill[Boolean](2*n){true}
		val diag2 = Array.fill[Boolean](2*n){true}

		/*
		Making a recursive internal function in Scala appears to be non-trivial:
		https://stackoverflow.com/questions/5337464/anonymous-recursive-function-in-scala

		The intuitive approach
			val descend : Int => Int = (i) => { ... descend(i+1) }
		fails to compile!
		*/
		
		val descend = new Function1[Int,Int] {
			def apply( i : Int) : Int = {
				if( n == i) {
					1
				} else {
					var nsol : Int = 0

					for { 
						j <- 0 to n-1 
						if col(j) && diag1(i+j) && diag2(i-j+n) 
					} { // for each element from the above sequence, create

						col(j) = false
						diag1(i+j) = false
						diag2(i-j+n) = false

						nsol += apply(i+1)

						col(j) = true
						diag1(i+j) = true
						diag2(i-j+n) = true	
					}

					nsol
				}
			}
		}

		descend(0)
	}


	def timeExecution(func : => Unit, num_queens : Int, num_iter : Int) = {

		val times = for(iter_idx <- 1 to num_iter) yield {
			val t1 = System.currentTimeMillis()
			func
			val t2 = System.currentTimeMillis()
			(t2 - t1) * 0.001
		}

		val t_mean : Double = times.sum / times.length

		val t_var : Double = sqrt(times.map(t => {
			val diff = t-t_mean
			diff*diff
		}).sum / (times.length+1))

		(t_mean, t_var)
	}


	def main(args: Array[String]) : Unit = {

		val func : Int => Int = if (args.length == 0) {
			allQueensRec
		} else args(0)	match  {
			case "recursive" => allQueensRec
			case "closure" => allQueensClosure
			case _ => allQueensRec
		}

		println("n	mean	var")

		for (num_queens <- 8 to 13) {
			val num_iter = if(num_queens <= 10) 1000
				else if (num_queens <= 15) 10
				else 5

			var nsol = 0

			val (t_mean, t_var) = timeExecution({ nsol = func(num_queens) }, num_queens, num_iter)

			// println(s"$num_queens queens, $nsol solutions time $t_mean s per attempt. (var $t_var, nt $num_iter)")
			println(s"$num_queens	$t_mean 	$t_var")
		}
	}
}



