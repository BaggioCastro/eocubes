import matplotlib.pyplot as plt
from ipywidgets import interact, IntSlider, fixed
import numpy as np
import re

def plot_cube(cubo):
    def plot_data(band, time_index):
        plt.clf()
        
       
        if 'band' in cubo.dims:
            data = cubo.isel(band=band, time=time_index)
            title = f'BANDA: {cubo.band.values[band]} - Tempo: {cubo.time.values[time_index]}'
        else:
            data = cubo.isel(time=time_index)
            title = f'Tempo: {cubo.time.values[time_index]}'
        
    
        reshaped_data = data.values.reshape(cubo.attrs['y_dim'], cubo.attrs['x_dim'])
        
        # Plotar a imagem
        plt.figure(figsize=(14, 10))
        img = plt.imshow(reshaped_data, cmap='Greens')
        cbar = plt.colorbar(img, fraction=0.046, pad=0.04)
        cbar.set_label('Value', rotation=270, labelpad=15)
        plt.title(title)
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.show()

    if 'band' in cubo.dims:
        band_slider = IntSlider(
            min=0, max=len(cubo.band.values)-1, step=1, value=0, description='Band:', continuous_update=False)
        time_slider = IntSlider(
            min=0, max=len(cubo.time.values)-1, step=1, value=0, description='Date:', continuous_update=False)
        interact(plot_data, band=band_slider, time_index=time_slider)
    else:
        time_slider = IntSlider(
            min=0, max=len(cubo.time.values)-1, step=1, value=15, description='Date:', continuous_update=False)
        interact(plot_data, band=fixed(0), time_index=time_slider)  # Passa um valor fixo para band

def get_band_slice(train, band, bands):
    """
    Returns a slice of the input data matrix corresponding to the given band.

    Parameters:
    -----------
    train : ndarray
        The input data matrix of shape (n_samples, n_features).
    band : str
        The name of the band to be extracted.
    bands : list of str
        The list of all band names in the input data.

    Returns:
    --------
    band_slice : ndarray
        The slice of the input data matrix corresponding to the given band.
    """
    n_bands = len(bands)
    step = len(train[0]) // n_bands
    band_indices = dict(zip(bands, range(n_bands)))
    start, end = band_indices[band] * step, (band_indices[band] + 1) * step
    return train[:, start:end]

def plot_codebooks(cubo, neurons, predictions, band, n):
    """
    Analisar e plotar a banda específica dos dados de cubo e os pesos dos neurônios.

    Parameters:
    -----------
    cubo : xarray.DataArray
        O cubo de dados contendo dimensões 'band', 'time', e 'pixel'.
    neurons : ndarray
        A matriz de pesos dos neurônios de forma (n_samples, n_features).
    predictions : ndarray
        Array contendo as predições ou índices dos clusters.
    band : str
        A banda específica a ser analisada.
    bands : list of str
        Lista de todas as bandas no cubo.
    n : int
        Número de clusters ou neurônios a serem plotados.
    """
    # Obter a fatia da banda específica dos pesos dos neurônios
    array = get_band_slice(neurons.astype("int16"), band, cubo.band.values) / 10000

    # Obter os valores únicos de predições e suas contagens
    unique_predictions, counts = np.unique(predictions, return_counts=True)

    # Formatar os timestamps
    formatted_timestamps = [str(ts)[:10] for ts in np.unique(cubo.time.values)]
    
    # Criar subplots
    fig, axs = plt.subplots(n, n, figsize=(16, 8), sharex=True, sharey=True)
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(wspace=0.5)

    for idx, ax in enumerate(axs.flat):
        if idx >= len(unique_predictions):
            ax.axis('off')
            continue
        
        # Obter os índices das predições do cluster atual
        indices = np.where(predictions == idx)[0]

        # Extrair a série temporal do cubo para a banda específica e normalizar
        cluster_series = cubo.sel(band=band).values[indices] / 10000
        
        # Calcular a média e o desvio padrão da série temporal
        ts_mean = np.mean(cluster_series, axis=0)
        std_devs = np.std(cluster_series, axis=0)

        # Calcular os limites superior e inferior
        upper_limit = ts_mean + std_devs
        lower_limit = ts_mean - std_devs

        # Plotar a média e os pesos dos neurônios (codebook)
        ax.plot(ts_mean, color='red', linewidth=0.8, label="mean")
        ax.plot(array[idx], color='white', linewidth=2, label="codebook")

        # Configurar o estilo do gráfico
        ax.set_facecolor(plt.cm.viridis(idx / (n*n-1)))
        ax.set_xticks(np.arange(0, len(array[idx]), 2))
        ax.set_xticklabels(formatted_timestamps[::2], rotation=45, ha='right', weight='light')
        ax.set_yticks(np.arange(-1, 1.2, 0.2))
        ax.grid(True, linestyle='--', color='white', linewidth=0.3)
        ax.axhline(0, color='white', linestyle='--', linewidth=0.3)
        ax.set_title(f"N° de séries temporais: {counts[idx]}", color='black', fontsize=12, fontweight='bold')
        ax.text(0.5, 0.5, str(idx), color='white', fontsize=12, fontweight='bold', ha='center', va='center')
        ax.fill_between(range(len(array[idx])), lower_limit, upper_limit, color='gray', alpha=0.9, linewidth=0, label="std")

        ax.legend()

    plt.tight_layout()
    plt.show()

def plot_cluster_map(labels, n, th=None):
    """
    Plota um mapa de clusters com coloração viridis e rótulos sobrepostos.

    Parâmetros:
    -----------
    labels : ndarray
        Array 1D de rótulos que será remodelado para formar a matriz n x n.
    n : int
        O tamanho da matriz (n x n).
    th : float, opcional
        Threshold para exibir no título, se fornecido.
    """
    # Remodelar os rótulos para formar uma matriz n x n
    mlabels = labels.reshape(n, n)

    # Criação da figura e eixos
    fig, ax = plt.subplots(figsize=(9, 9), sharey=True)

    # Adicionar texto para cada rótulo na matriz
    for i in range(n):
        for j in range(n):
            ax.text(j, i, str(mlabels[i][j]), va='center', ha='center', color='red')

    # Exibir a imagem sem transposição
    ax.imshow(mlabels, cmap='viridis', interpolation='none')

    # Adicionar a grade
    ax.grid(True, which='both', color='grey', linestyle='-', linewidth=0.5)

    # Ajustar os ticks
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_xticks(np.arange(0, n, 1))
    ax.set_yticks(np.arange(0, n, 1))

    # Exibir a grade apenas nos ticks menores
    ax.grid(which='minor', color='black', linestyle='-', linewidth=1.5)

    # Remover a grade nos ticks principais
    ax.grid(which='major', color='none')

    # Ajustar os limites para garantir que a grade e a imagem se alinhem corretamente
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(n - 0.5, -0.5)

    # Personalização do gráfico
    ax.spines['left'].set_lw(1.5)
    ax.spines['bottom'].set_lw(1.5)
    ax.spines['right'].set_lw(1.5)
    ax.spines['top'].set_lw(1.5)

    # Adicionar o título
    title = f"Número de grupos finais {len(np.unique(labels))}"
    if th is not None:
        title += f" - Distância: {th}"
    plt.title(title)

    # Mostrar a figura
    plt.show()