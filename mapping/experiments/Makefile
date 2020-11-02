main.s: main.ll
	llc main.ll -o main.s

main.ll: main.c
	clang-11 -O3 -emit-llvm -S -c main.c -o main.ll

clean:
	rm main.ll main.s
