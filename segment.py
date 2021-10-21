import matplotlib.image as img
import matplotlib.pyplot as plt
from filter import *
from segment_graph import *
import time
import os,glob


# --------------------------------------------------------------------------------
# Segment an image:
# Returns a color image representing the segmentation.
#
# Inputs:
#           in_image: image to segment.
#           sigma: to smooth the image.
#           k: constant for threshold function.
#           min_size: minimum component size (enforced by post-processing stage).
#
# Returns:
#           num_ccs: number of connected components in the segmentation.
# --------------------------------------------------------------------------------
def segment(in_image, sigma, k, min_size):
    start_time = time.time()
    height, width, band = in_image.shape
    print("Height:  " + str(height))
    print("Width:   " + str(width))
    smooth_blue_band = smooth(in_image[:, :, 0], sigma)
    smooth_green_band = smooth(in_image[:, :, 1], sigma)
    smooth_red_band = smooth(in_image[:, :, 2], sigma)
    smooth_NIR_band = smooth(in_image[:, :, 3], sigma)
    smooth_red_edge_band = smooth(in_image[:, :, 4], sigma)

    # build graph
    edges_size = width * height * 4
    edges = np.zeros(shape=(edges_size, 3), dtype=object)
    num = 0
    # 4-corner graph
    for y in range(height):
        for x in range(width):
            if x < width - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int(y * width + (x + 1))
                edges[num, 2] = diff(smooth_blue_band, smooth_green_band, smooth_red_band, smooth_NIR_band, smooth_red_edge_band, x, y, x + 1, y)
                num += 1
            if y < height - 1:
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + x)
                edges[num, 2] = diff(smooth_blue_band, smooth_green_band, smooth_red_band, smooth_NIR_band, smooth_red_edge_band, x, y, x, y + 1)
                num += 1

            if (x < width - 1) and (y < height - 2):
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y + 1) * width + (x + 1))
                edges[num, 2] = diff(smooth_blue_band, smooth_green_band, smooth_red_band, smooth_NIR_band, smooth_red_edge_band, x, y, x + 1, y + 1)
                num += 1

            if (x < width - 1) and (y > 0):
                edges[num, 0] = int(y * width + x)
                edges[num, 1] = int((y - 1) * width + (x + 1))
                edges[num, 2] = diff(smooth_blue_band, smooth_green_band, smooth_red_band, smooth_NIR_band, smooth_red_edge_band, x, y, x + 1, y - 1)
                num += 1
    # Segment
    u = segment_graph(width * height, num, edges, k)

    # post process small components
    for i in range(num):
        a = u.find(edges[i, 0])
        b = u.find(edges[i, 1])
        if (a != b) and ((u.size(a) < min_size) or (u.size(b) < min_size)):
            u.join(a, b)

    num_cc = u.num_sets()
    img_output = np.zeros(shape=(height, width, 3))
    output = np.zeros(shape=(height, width))

    # pick random colors for each component
    colors = np.zeros(shape=(height * width, 3))
    for i in range(height * width):
        colors[i, :] = random_rgb()


    for y in range(height):
        for x in range(width):
            comp = u.find(y * width + x)
            img_output[y, x, :] = colors[comp, :]
            output[y, x] = comp
            

    # displaying the result
    fig = plt.figure()
    a = fig.add_subplot(1, 2, 1)
    plt.imshow(in_image[:,:,0])
    a.set_title('Original Image')
    a = fig.add_subplot(1, 2, 2)
    plt.imshow((img_output * 255).astype(np.uint8))
    a.set_title('Segmented Image')
    plt.show()

    elapsed_time = time.time() - start_time
    print(
        "Execution time: " + str(int(elapsed_time / 60)) + " minute(s) and " + str(
            int(elapsed_time % 60)) + " seconds")

    return output, u


"""
if __name__ == "__main__":
    sigma = 0.5
    k = 500
    min = 50

    imagePath = os.path.join('.','data','MISTSET','000')
    imageNames = glob.glob(os.path.join(imagePath,'IMG_0096_*.tif'))

    # Read raw image DN values
    # reads 16 bit tif - this will likely not work for 12 bit images
    index = 0
    imageRaws = np.ndarray(shape = (960,1280,5))
    for names in imageNames:
        imageRaws[:,:,index] = plt.imread(names)
        index = index + 1
    # Loading the image
    input_image = imageRaws
    print("Loading is done.")
    print("processing...")
    segment(input_image, sigma, k, min)
"""