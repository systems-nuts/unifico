#!/bin/sh

##### FIXME #####
#benchmarks = "dc ft mg cg lu bt is ep sp ua"
benchmarks="cg is" # TODO: give this as an argument
LLVM_SOURCE=~/llvm-project
#################

E_XCD=86 # Can't change directory?

short_hash=$1
class=$2
arch=$3
version=$4
iterations=$5

# Find experiment name from git commit/hash
cd "$LLVM_SOURCE" || {
	echo "Cannot change to llvm source tree." 
	exit $E_XCD;
}

experiment_name=`git log -n 1 --pretty=format:%s $short_hash 2>/dev/null`
ret_code=$?
if [ $ret_code != 0 ]; then
	echo "NOTE: Commit hash does not exist. Using \"test\" as experiment name."
	echo
	experiment_name=test
fi

# Return to working directory inside NPB
cd -

# Create result directories
mkdir -p bin
mkdir -p result/$short_hash

# Create info.json
info="{
	\"experiment\": {
			\"name\":\"$experiment_name\",
			\"hash\":\"$short_hash\"
		},
	\"class\":\"$class\",
	\"arch\":\"$arch\",
	\"iterations\":$iterations,
	\"other_info\":\"$version\"
}"
echo $info >result/${short_hash}/info.json

for benchmark in $benchmarks; do

	bin=${benchmark}/${benchmark}_${arch}_${version}.out

	for iteration in `seq 1 $iterations`; do

		out_file=${benchmark}.${arch}.${class}.${iteration}.out
		echo "Running ${bin}, result to ${out_file}"	
		${bin} >result/${short_hash}/${out_file}

	done
done

echo "Done.\n"
