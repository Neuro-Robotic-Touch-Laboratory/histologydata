import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from matplotlib.widgets import Slider

# Set up matplotlib
matplotlib.use('TkAgg')

def show_data_scan(data, data_path = '', save_gif = False):
    """
    Displays an animated sequence of images from the provided data, and optionally saves the animation as a GIF. 
    The function generates an animation, where each frame corresponds to an image in the data. If specified, 
    the animation can also be saved as a GIF file.

    Args:
        - data (list of ndarray or list of Image): A list of images (as numpy arrays or PIL Image objects) to be animated.
        - save_gif (bool, optional): If True, saves the animation as a GIF file. Defaults to False.
        - verbose (bool, optional): If True, enables debug-level logging. Defaults to False, which sets the logging level to INFO.

    Returns:
        - None: Displays the animation and optionally saves it as a GIF file.
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    
    # Create figure and axis
    fig, ax = plt.subplots()
    ax.axis('off')  # Turn off the axis
    im = ax.imshow(data[0], animated=True)  # Initial image

    # # Set up animation
    animation_fig = anim.FuncAnimation(
        fig, lambda i: update(i, im, data),  # Lambda allows us to pass im and data to update
        frames=len(data), interval=200, blit=True, repeat_delay=1000
    )

    plt.pause(5)
    
    # Show the animation
    plt.show(block = False)
    
    # # Save the animation as a GIF (requires Pillow or ImageMagick)
    if save_gif:
        animation_fig.save(data_path + "/animated_IMAGES.gif", dpi=150, writer='pillow')

def update(i, im, data):
    """
    Updates the image for a given frame in the animation. This function is used in conjunction with `matplotlib.animation.FuncAnimation` to modify the image displayed in the animation based on the frame index.

    Args:
        - i (int): The index of the current frame in the animation sequence. This determines which image in `data` is displayed.
        - im (matplotlib.image.AxesImage): The image artist object that is being animated. It is updated in place with a new image for the current frame.
        - data (list of ndarray or list of Image): A list of images (as numpy arrays or PIL Image objects) to be used in the animation.

    Returns:
        - list: A list containing the updated image artist (`im`). This is required by `FuncAnimation` to know which artist(s) need updating.
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    im.set_array(data[i])  # Update image for frame i
    return [im]  # Return updated artist 

def plot_data_scan_aggregated (data):
    """
    Visualizes color and depth data for a sequence of frames with an interactive slider.
    
    Args:
        - data (dict): A nested dictionary containing 'color' and 'depth' data
                     in 'original' and 'segmented' formats.
                     
    Returns: 
        - None
    
    Author:
        - Name: Fabrizia Auletta
        - Date: 21/11/2024
        - Contact: fabrizia.auletta@santannapisa.it
    """
    

    # Extract data
    color_original = data['color']['original']
    color_segmented = data['color']['segmented']
    depth_original = data['depth']['original']
    depth_segmented = data['depth']['segmented']

    # Initial frame
    current_frame = 0

    # Set up the plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Function to plot the frame
    def plot_frame(frame):
        """
        Updates the plots with data from the specified frame.

        Args:
            frame (int): The frame index to display.
        """
        axes[0, 0].imshow(color_original[frame])
        axes[0, 0].set_title("Color Original")
        axes[0, 0].axis("off")
        axes[0, 1].imshow(color_segmented[frame])
        axes[0, 1].set_title("Color Segmented")
        axes[0, 1].axis("off")
        axes[1, 0].imshow(depth_original[frame])
        axes[1, 0].set_title("Depth Original")
        axes[1, 0].axis("off")
        axes[1, 1].imshow(depth_segmented[frame])
        axes[1, 1].set_title("Depth Segmented")
        axes[1, 1].axis("off")

        fig.canvas.draw_idle()

    #  Plot the initial frame
    plot_frame(current_frame)

    # Add slider
    ax_slider = plt.axes([0.2, 0.95, 0.6, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Frame', 0, len(color_original) - 1, valinit=current_frame, valstep=1)

    # Update function for slider
    def update_agg(val):
        """
        Callback for slider interaction to update plots.

        Args:
            val (float): Current value of the slider.
        """
        frame = int(slider.val)
        plot_frame(frame)

    slider.on_changed(update_agg)

    # Show the plot
    plt.show()



