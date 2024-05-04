import numpy as np
import matplotlib.pyplot as plt

N = 1000
probs = np.linspace(0, 1, 100, endpoint=False)
plot_data = np.zeros(probs.shape)

for i_p, p in enumerate(probs):
    #print(f"p={p}")
    for n in range(N):
        information = np.random.choice([0,1], 2)
        encoded = np.append(information, np.array(np.sum(information)%2))

        count_errors = 0
        #print(f"encoded before {encoded}")
        for i in range(len(encoded)):
            p_flip = np.random.random(1)[0]
            #print(f"p_flip         {p_flip}")
            if p_flip < p:
                encoded[i] = not encoded[i]
                count_errors += 1
        #print(f"encoded after  {encoded}")
        error_count_calculated = np.sum(encoded)%2
        #print(f"count errors   {count_errors}")
        #print(f"error detected {error_count_calculated}")
        if error_count_calculated == count_errors:
            plot_data[i_p] += 1

plt.plot(probs, plot_data*100/N, label="With Error Correction")
plt.plot(probs, np.linspace(100, 0, probs.shape[0]), linestyle='dashed', label="Without Error Correction")
plt.ylabel("% times where correct errors detected")
plt.xlabel("p")
plt.grid()
plt.legend()
plt.title("Effectiveness of parity-bit error correction on 2-bit information")
plt.savefig("plots/plot1.svg")
