import numpy
import matplotlib

matplotlib.use("Agg")
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv("../pin-tools/heap-accesses/heap_accesses.csv", sep=",")

    df["address"] = df["address"].apply(lambda x: int(x, 16))

    figure(figsize=(10, 8), dpi=80)

    fig = plt.plot(df["step"], df["address"], "r,")
    plt.grid(True)
    plt.title("Memory Accesses")
    plt.xlabel("Time Step")
    plt.ylabel("Memory Address")
    plt.savefig("memory_accesses.png")
