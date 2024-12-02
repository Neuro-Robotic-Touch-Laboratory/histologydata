import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px

import logging

# Set up matplotlib
matplotlib.use('TkAgg')

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_data_us(data, verbose = False):
    """
    Plots ultrasound data alongside corresponding images in a side-by-side layout. 
    For each column of the ultrasound data (stored in a DataFrame), the function 
    displays an ultrasound signal plot and an associated image. 

    Args:
        - data (dict): A dictionary containing the ultrasound data:
            - 'data' (pd.DataFrame): A DataFrame where each column represents a series of ultrasound signal samples.
            - 'images' (list): A list of images corresponding to the ultrasound data.
        - verbose (bool, optional): If True, enables debug-level logging. Defaults to False, which sets the logging level to info.

    Returns:
        - None: Displays a plot with ultrasound images and signal data.
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    for col, img in zip(data['data'].index[:], data['images'][:]):
        fig = plt.figure(figsize=(15, 5))
    
        gs = fig.add_gridspec(1, 2, width_ratios=[1, 1], wspace=0) 
        
        axsLeft = fig.add_subplot(gs[0, 0])
        axsRight = fig.add_subplot(gs[0, 1])
        
        # Plot the image on the left
        axsLeft.imshow(img)
        axsLeft.axis('off')  # Hide axis
        
        # Plot the ultrasound signal on the right
        axsRight.plot(data['data'].loc[col])
        axsRight.set_xlabel('Samples')  # Label x-axis
        axsRight.set_ylabel('US signal')  # Label y-axis
        
        # Add a title for the figure indicating the current signal
        fig.suptitle('Indented point ' + str(col), fontsize=16)

    plt.show(block = False) 
    
def plot_data_us_oneSignal(data):
    """
    Plots a line chart for a selected ultrasound signal ID.

    Args:
        - data (dict): A dictionary containing 'UltrasoundPlatform' with 'metadata' and 'data' as keys.

    Returns:
        - None
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    # Extract unique IDs
    us_ids = data['metadata']['file_id'].unique()

    # Prompt user for ID selection
    selected_us_id = input('Select an ID from the following list:\n' + str(us_ids) + '\n')

    # Fetch data and create x, y values for plotting
    yy = data['data'].loc[selected_us_id].values
    
    SAMPLING_Fr = 80_000_000 #digitalization-uskey
    dt = 1/SAMPLING_Fr
    N = len(yy)
    
    xx = np.linspace(0.0, N * dt, N)

    # Create the line plot
    fig = px.line(x=xx, y=yy)

    # Update layout with titles and styles
    fig.update_layout(
        title=dict(text="Point ID: " + selected_us_id),
        xaxis=dict(title=dict(text="Samples")),
        yaxis=dict(title=dict(text="US signal [a.u.]")),
        font=dict(size=18)
    )

    # Display the plot
    fig.show()

def aggregate_data(data):
    """
    Aggregates data from a nested dictionary structure into a structured DataFrame.

    Args:
        - data (dict) : A dictionary containing:
            - 'data': A DataFrame where the index represents `file_id` and columns contain arrays of `hf` signals.
            - 'metadata': A DataFrame where each row corresponds to a `file_id`, with labels associated with each signal.

    Returns:
        - df (pd.DataFrame) : A DataFrame with the following columns:
            - `file_id`: Unique identifiers for each data entry.
            - `hf`: Array-like objects representing the signal data.
            - `label`: Labels associated with each signal.
        
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """ 
   
    df = pd.DataFrame(columns=['file_id', 'hf'])

    file_id, hf = [], []
    for idx in data['data'].index:
        file_id.append(idx)
        hf.append(np.array(data['data'].loc[idx]))

    df['file_id'] = file_id
    df['hf'] = hf
    df['label'] = data['metadata']['label']
    
    SAMPLING_Fr = 80_000_000 #digitalization-uskey
    dt = 1/SAMPLING_Fr
    time_vectors = []

    for index, row in df.iterrows():
        #Calculate N based on the length of hf_mean
        N = len(row['hf'])
        # Calculate time vector
        time = np.linspace(0.0, N * dt, N)
        time_vectors.append(time)
    
    df['time'] = time_vectors
    
    return df 

def norm(data, G, factor):
    """
    Normalizes a signal array by removing an offset and scaling the values based on a gain factor.

    Args:
        - data (array-like): The input signal array to be normalized.
        - G (float or int): The gain factor used in the normalization calculation, i.e., the amplification level.
        - factor (float or int): A divisor applied to the gain factor in the normalization formula.

    Returns:
        - (np.ndarray) : A normalized array where the offset has been removed, 
        and the values are scaled by the specified gain and voltage range.
        
    Author:
        - Name: Ilaria Benedetti
        - Date: 20/10/2024
        - Contact: ilaria.benedetti@santannapisa.it
    """

    V = 40  # Fixed voltage range
    G_float = float(G)  # Convert gain to float for precision
    return (np.copy(data) - 2048) / (V * (10 ** (G_float / factor)))

def plot_data_us_aggregated(data, datatype = 'hf'):
    """
    Plots an interactive visualization of the datatype variable colored by 'label'.
    
    Args:
        - data (dict): A dictionary with keys 'UltrasoundPlatform' containing 'data' and 'metadata'.

    Returns:
        - None
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    df = aggregate_data(data)
    
    if 'norm' in datatype: 
        df['Gain'] = data['metadata']['Gain']
        df['hf_norm'] = df.apply(lambda row: norm(row['hf'], row['Gain'], 20), axis=1)
    
    # Expand datatype arrays into separate rows for plotting
    data_expanded = []
    for _, row in df.iterrows():
        file_id = row['file_id']
        label = row['label']
        hf_values = row[datatype]
        t_values = row['time']
        for t, value in zip(t_values, hf_values):
            data_expanded.append({'Sample': t, 'Value': value, 'Label': label, 'File ID': file_id})

    # Convert to a new DataFrame
    expanded_df = pd.DataFrame(data_expanded)

    # Step 3: Create the interactive plot
    fig = px.line(
        expanded_df,
        x='Sample',
        y='Value',
        color='Label',
        line_group='File ID',
        hover_data={'File ID': True, 'Label': True}
    )
    
    if 'norm' in datatype:
        ylabel = 'Standardized US signal [a.u.]' 
    else:
        ylabel = 'US signal [a.u.]'
        

    # Update layout
    fig.update_layout(
        title="Aggregated plot",
        xaxis=dict(title="Time [s]"),
        yaxis=dict(title=ylabel),
        legend_title="Label",
        font=dict(size=16)
    )

    # Show the plot
    fig.show()
