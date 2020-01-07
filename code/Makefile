all:
	make c+1
	make c+2
	make gol

c++:
	make clean
	clang++  queens.cpp -Ofast -stdlib=libc++ -pthread -std=gnu++14
	time ./a.out -n0 8  -n1 15 > cplu1.log
	time ./a.out -n0 15 -n1 18 > cplu2.log
	time ./a.out -n0 18 -n1 19 > cplu3.log

c+1:
	make clean
	clang++  queens1.cpp -Ofast -stdlib=libc++ -pthread -std=gnu++14
	time ./a.out -n0 8  -n1 15 > cplu1.log
	time ./a.out -n0 15 -n1 18 > cplu2.log
	time ./a.out -n0 18 -n1 19 > cplu3.log

c+2:
	make clean
	clang++  queens2.cpp -Ofast -stdlib=libc++ -pthread -std=gnu++14
	time ./a.out -n0 8  -n1 15 > cplu1.log
	time ./a.out -n0 15 -n1 18 > cplu2.log
	time ./a.out -n0 18 -n1 19 > cplu3.log

c+3:
	make clean
	clang++  queens2.cpp -Ofast -stdlib=libc++ -pthread -std=gnu++14
	time ./a.out -n0 8  -n1 15 > cplu1.log
	time ./a.out -n0 15 -n1 18 > cplu2.log
	time ./a.out -n0 18 -n1 19 > cplu3.log

gol:
	rm -f queens
	go build queens.go
	time ./queens -n0 8  -n1 14 > gola1.log
	time ./queens -n0 15 -n1 17 > gola2.log
	time ./queens -n0 18 -n1 18 > gola3.log

pyt: 
	python queens.py > queens.log

foo:
	make clean
	clang++  queens.cpp -Ofast -stdlib=libc++ -pthread -std=gnu++14
	time ./a.out -n0 17 -n1 19 > cplu4.log
	go build queens.go
	time ./queens -n0 18 -n1 18 > gola4.log

clean:
	rm -f *.o a.out queens


