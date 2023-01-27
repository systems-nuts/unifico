import numpy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv("../pin-tools/heap-accesses/heap_accesses.out", sep=",")

    plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.title("Signal-Diagram")
    plt.xlabel("Sample")
    plt.ylabel("In-Phase")
    plt.savefig("foo2.png")
