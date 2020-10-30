main.s: main.ll
	llc-11 main.ll -o main.s

main.ll: main.c
	clang-11 -emit-llvm -S -c main.c -o main.ll

clean:
	rm main.ll main.s
