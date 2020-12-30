fact.out: fact.c
	clang -g -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer fact.c -o fact.out

fact.s: fact.c
	clang -S -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer fact.c -o fact.s

link_register.s: link_register.c
	clang -S link_register.c -o link_register.s

ret_call.s: ret_call.c
	clang -S ret_call.c -o ret_call.s

two_calls: two_calls.c
	clang -g -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer two_calls.c -o two_calls

two_calls.s: two_calls.c
	clang -S -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer two_calls.c -o two_calls.s

call_leaf.out: call_leaf.c
	clang -g -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer call_leaf.c -o call_leaf.out

call_leaf.s: call_leaf.c
	clang -S -mno-omit-leaf-frame-pointer -fno-omit-frame-pointer call_leaf.c -o call_leaf.s

main.s: main.ll
	llc main.ll -o main.s

main.ll: main.c
	clang -emit-llvm -S -c main.c -o main.ll

clean:
	rm *.ll *.s fact link_register ret_call two_calls call_leaf main
