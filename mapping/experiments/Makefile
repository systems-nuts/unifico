main.s: main.ll
	llc-3.9 main.ll -o main.s

main.ll: main.c
	clang-3.9 -emit-llvm -S -c main.c -o main.ll

clean:
	rm main.ll main.s
