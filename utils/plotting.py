import numpy as np
import csv
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
plt.ion()

def senoide(t, A, w, phi, offset):
    return A * np.sin(w * t + phi) + offset

# A = amplitude
# w = frequência angular
# phi = fase
# offset = deslocamento vertical

def save_and_plot(positions, periods):
    if not positions:
        return

    pos_x_data = [(t, pos[0]) for t, pos in positions if pos is not None]
    with open("_csv/pendulo_posicao_x_tempo.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Tempo (s)", "Posição X (px)"])
        for t, x in pos_x_data:
            writer.writerow([round(t, 3), x])

    print("CSV salvo como pendulo_posicao_x.csv")

    tempos, posicoes_x = zip(*pos_x_data)
    tempos = np.array(tempos)
    posicoes_x = np.array(posicoes_x)

    fig = plt.figure(figsize=(10, 4))
    fig.canvas.manager.set_window_title("Posição Lateral do Pêndulo ao Longo do Tempo")
    plt.plot(tempos, posicoes_x, label="Posição X do Pêndulo", color='blue')
    plt.title("Posição Lateral do Pêndulo ao Longo do Tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Posição X (pixels)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.pause(0.1)

    try:
        A_guess = (max(posicoes_x) - min(posicoes_x)) / 2
        w_guess = 2 * np.pi / (periods[0] if periods else 2)
        phi_guess = 0
        offset_guess = np.mean(posicoes_x)
        popt, _ = curve_fit(senoide, tempos, posicoes_x, p0=[A_guess, w_guess, phi_guess, offset_guess])
        fitted = senoide(tempos, *popt)
        peaks, _ = find_peaks(fitted)

        fig = plt.figure(figsize=(10, 4))
        fig.canvas.manager.set_window_title("Ajuste Senoidal da Posição X do Pêndulo")
        plt.plot(tempos, posicoes_x, 'b.', label="Dados observados")
        plt.plot(tempos, fitted, 'r-', label=f"Ajuste senoide")
        plt.plot(tempos[peaks], fitted[peaks], 'ro', label="Picos")
        plt.title("Ajuste Senoidal da Posição X do Pêndulo")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Posição X (px)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.pause(0.1)

        print(f"Ajuste: A={popt[0]:.1f}, w={popt[1]:.2f}, phi={popt[2]:.2f}, offset={popt[3]:.1f}\n")
        print("A = Amplitude, w = Frequência Angular, phi = Fase, offset = Deslocamento Vertical")

    except Exception as e:
        print("Erro ao ajustar curva senoide:", e)
