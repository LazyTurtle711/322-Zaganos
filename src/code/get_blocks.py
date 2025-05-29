from __future__ import print_function  # Ensures compatibility with Python 2 and 3 for print function
import pixy  # Import the Pixy2 camera library
from ctypes import *  # Import C types for working with the C-based Pixy library
from pixy import *  # Import all symbols from pixy module
import math

class PixyCam():
    def __init__(self, max_blocks=3):
        """
        Initialize the Pixy2 camera wrapper class.

        Parameters:
        - max_blocks: Maximum number of color blocks to detect at once (default: 5)
                     Higher values may impact performance but allow tracking more objects
        """
        print("İnitializing Pixy2...")

        # Initialize the Pixy2 camera hardware and communication
        # This establishes the connection between Raspberry Pi and Pixy2
        pixy.init()

        # Set Pixy2 to run the color_connected_components program
        # This program detects colored objects that have been taught to the camera
        pixy.change_prog("color_connected_components")

        # Create a block array to store detected objects
        # BlockArray is a C-compatible structure defined in the pixy library
        self.blocks = BlockArray(max_blocks)

        # Store the maximum number of blocks to detect
        self.max_count = max_blocks

    def merge_close_blocks(self, blocks, max_distance=50):
        merged = []
        # signature’a göre grupla
        sig_groups = {}
        for b in blocks:
            sig_groups.setdefault(b['signature'], []).append(b)
        
        for sig, grp in sig_groups.items():
            clusters = []
            for blk in grp:
                placed = False
                for cluster in clusters:
                    cx = sum(b['x'] for b in cluster) / len(cluster)
                    cy = sum(b['y'] for b in cluster) / len(cluster)
                    dist = math.hypot(blk['x'] - cx, blk['y'] - cy)
                    if dist <= max_distance:
                        cluster.append(blk)
                        placed = True
                        break
                if not placed:
                    clusters.append([blk])

            for cluster in clusters:
                count = len(cluster)
                merged.append({
                    'signature': sig,

                    'x': sum(b['x'] for b in cluster) / count,
                    'y': sum(b['y'] for b in cluster) / count,

                    'width': max(b['x'] + b['width']/2 for b in cluster) - min(b['x'] - b['width']/2 for b in cluster),
                    'height': max(b['y'] + b['height']/2 for b in cluster) - min(b['y'] - b['height']/2 for b in cluster),
                    'count': count  
                })
        return merged

    def get_blocks(self):
        """
        Capture and process the current frame from Pixy2 camera.

        Returns a list of dictionaries, each containing information about a detected block:
        - signature: The color signature ID (1-7) that was detected
        - x, y: The center coordinates of the detected object
        - width, height: The dimensions of the detected object
        - angle: The rotation angle of the object (if available)
        - index: A tracking index assigned by Pixy2
        - age: How many frames this object has been tracked continuously
        """
        # Request the current blocks/objects from the Pixy2 camera
        # This function fills the self.blocks array with detected objects
        self.count = pixy.ccc_get_blocks(self.max_count, self.blocks)

        # Create an empty list to store the processed block data in Python-friendly format
        self.block_data = []

        # Process each detected block and convert it to a Python dictionary
        for index in range(self.count):
            # Extract all properties of the current block into a dictionary
            block_info = {
                'signature': self.blocks[index].m_signature,  # Color ID (1-7)
                'x': self.blocks[index].m_x,  # X-coordinate of center (0-315)
                'y': self.blocks[index].m_y,  # Y-coordinate of center (0-207)
                'width': self.blocks[index].m_width,  # Width of the detected object
                'height': self.blocks[index].m_height,  # Height of the detected object
                'angle': self.blocks[index].m_angle,  # Rotation angle if available
                'index': self.blocks[index].m_index,  # Tracking index assigned by Pixy2
                'age': self.blocks[index].m_age  # Number of frames this object has been tracked
            }
            # Add the current block's information to our result list
            self.block_data.append(block_info)

        # Sort blocks by their signature (color ID) for easier processing
        # This makes it easier to find all blocks of a specific color
        self.block_data.sort(key=lambda b: b['signature'])
        
        merged = self.merge_close_blocks(self.block_data, 10)

        return merged

        # The calling code can access self.block_data to get the detected objects

if __name__ == '__main__':
    import time

    # Create a new PixyCam object with a maximum block detection limit of 5
    # This means the camera will track up to 5 colored objects at once
    # You can increase this number if you need to track more objects simultaneously
    cam = PixyCam(5)

    # Start an infinite loop to continuously get camera data
    while True:
        # Call the get_blocks method to capture the current frame from the Pixy2 camera
        # This updates the cam.blocks and cam.block_data with the latest detected objects
        # cam.block_data will contain a list of dictionaries with properties of each detected object
        cam.get_blocks()

        # Check if any objects were detected
        # cam.count will be greater than 0 if at least one object was detected
        if cam.count > 0:
            # Loop through each detected object and print its information
            for i in range(len(cam.block_data)):
                # Print the block number (starting from 1) and all the block's information
                # Each block_data entry contains: signature, x, y, width, height, angle, index, age
                # - signature: Color ID (1-7) that corresponds to trained colors in Pixy2
                # - x, y: Center coordinates of the object in the camera frame
                # - width, height: Size of the detected object
                # - angle: Rotation if available
                # - index, age: Tracking information from Pixy2
                print(f"{i + 1}. block data: {cam.block_data[i]}")
            # Print a blank line for better readability between frames
            print()

        # If no objects were detected in the current frame
        else:
            print("No targets detected!"),
            # Wait for 1 second before checking again
            time.sleep(1)