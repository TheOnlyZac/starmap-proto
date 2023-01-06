import struct
import pygame

QTY_STARS = 42010
SCREEN_SIZE = 800

class Vector3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = -y
        self.z = z

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return f'Vector3({self.x!r}, {self.y!r}, {self.z!r})'

class cStarRecord:
    def __init__(self, key, name, unk, flags, position, type, planet_count):
        self.key = key
        self.name = name
        self.unk = unk
        self.flags = flags
        self.position = position
        self.type = type
        self.planet_count = planet_count
    
    def csv(self):
        csv = '{},{},{},{},{},{},{}\n'.format(
            self.key,
            self.name,
            self.unk,
            self.flags,
            self.position.x, self.position.y, self.position.z,
            self.type,
            self.planet_count
        )

class ViewMatrix:
    def __init__(self, x=0.0, y=0.0, scale=0.5, translation_factor=100):
        self.x = x
        self.y = y
        self.scale = scale
        self.translation_factor = translation_factor

    def translate(self, dx, dy):
        # Increase the translation amount as the zoom increases
        self.x += dx * self.translation_factor
        self.y += dy * self.translation_factor

    def zoom(self, factor):
        # Translate the view matrix so that the center of the screen is at the origin
        center_x = SCREEN_SIZE / self.scale / 2 + self.x
        center_y = SCREEN_SIZE / self.scale / 2 + self.y
        self.translate(-center_x, -center_y)

        # Perform the zoom
        self.scale *= factor

        # Translate the view matrix back
        self.translate(center_x, center_y)

        # Adjust the translation factor as the zoom level changes
        self.translation_factor /= factor
    
    def set_offset(self, x, y):
        self.x = x
        self.y = y
    

def read_stars_from_file(filename):
    # Init empty stars array
    star_list = []

    # Read all stars from file into star list
    with open(filename, 'rb') as star_file:
        for i in range(QTY_STARS):
            key_bytes = star_file.read(4)
            mKey = int.from_bytes(key_bytes, 'big')
            mKey = key_bytes  # temp

            # Skip 156 bytes
            star_file.read(132)

            # Read star position (3 floats)
            float_bytes = star_file.read(3 * 4)
            # Unpack the floats using the struct module
            # <-- '<fff' specifies little-endian, 3 floats
            x, y, z = struct.unpack('>fff', float_bytes)
            mPosition = Vector3(x, y, z)

            # Read unknown value
            unk = star_file.read(4)

            # Read star flags (4 bytes)
            flag_bytes = star_file.read(4)
            mFlags = int.from_bytes(flag_bytes, 'big')

            # Read name length (4-byte int)
            name_len_bytes = star_file.read(4)
            name_len = int.from_bytes(name_len_bytes, 'big')

            # Initialize empty string for star name
            mName = ''

            # Read the specified number of bytes for the name
            string_bytes = star_file.read(name_len*2)

            # Decode the bytes to a string and add it to the result string
            mName += string_bytes.decode('utf-16le')

            # Skip more bytes
            star_file.read(20)

            # Read star type (4 byte int)
            type_bytes = star_file.read(4)
            mType = int.from_bytes(type_bytes, 'big')

            # Skip more bytes
            star_file.read(52)

            # Read planet count (1 byte)
            planet_count_byte = star_file.read(1)
            mPlanetCount = int.from_bytes(planet_count_byte, 'big')

            # Print the star data
            star_list.append(cStarRecord(mKey, mName, unk, mFlags, mPosition, mType, mPlanetCount))

    return star_list

def write_stars_to_csv(stars, ofilename="stars.csv"):
    csv = "key,name,unk,flags,position,type,planet_count\n"
    for star in stars:
        csv += star.csv()
    
    with open(ofilename, 'w+') as ofile:
        ofile.write(csv)

def draw_stars(screen, stars, view=ViewMatrix()):
    # Init empty list of stars to draw laset
    deferred = []

    # Iterate over the array of stars
    for star in stars:
        # Defer drawing special stars until the end
        if (star.name in ['Sol', 'Galactic Core', 'Treus-8']):
            deferred.append(star)
        
        # Draw star on screen
        draw_star(screen, star, view)
    
    # Finally, draw all deferred stars
    for star in deferred:
        draw_star(screen, star, view)

def draw_star(screen, star, view=ViewMatrix()):
    # Get the name and position of the star
    name = star.name
    pos = star.position

    # Get the size of the screen
    screen_width, screen_height = screen.get_size()

    # Calculate the screen position of the star
    x = int((pos.x - view.x) * view.scale + screen_width / 2)
    y = int((pos.y - view.y) * view.scale + screen_width / 2)

    # Determine if star is off screen, and if so, skip
    if x < 0 or y < 0 or x > screen_width or y > screen_height:
        return

    # Set default the color and size of the star to draw
    color = (255, 255, 255)
    color2 = (255, 255, 255)
    size = 1

    # Set color based on star type
    if (star.type == 1): # galactic core
        color = (255, 255, 255)
    elif (star.type == 2): # black hole
        color = (0, 0, 255)
    elif (star.type == 3): # proto-planetary disks
        color = (143, 143, 255)
    elif (star.type == 6): # red
        color = (211, 105, 86)
    elif (star.type == 5): # blue
        color = (100, 179, 252)
    elif (star.type == 4): # yellow
        color = (229, 189, 114)  
    elif (star.type == 12): # red-red
        color = (242, 80, 48)
        color2 = (242, 80, 48)
    elif (star.type == 7): # blue-blue
        color = (143, 255, 255)
        color2 = (143, 255, 255)
    elif (star.type == 10): # yellow-yellow
        color = (215, 178, 56)
        color2 = (215, 178, 56)
    elif (star.type == 8): # blue-red
        color = (143, 255, 255)
        color2 = (242, 80, 48)
    elif (star.type == 9): # blue-yellow
        color = (143, 255, 255)
        color2 = (215, 178, 56)
    elif (star.type == 11): # yellow-red
        color = (215, 178, 56)
        color2 = (242, 80, 48)
        

    # Draw star at it's screen position with varying detail based on viewport scale
    if view.scale >= 8:
        # Draw primary star
        pygame.draw.circle(screen, color, (x, y), int(size * view.scale / 8))
        
        if (view.scale >= 16):
            # Draw secondary star if binary system
            if star.type in [12, 7, 10, 8, 9, 11]:
                pygame.draw.circle(screen, color2, (x-6, y), int(size * view.scale / 8))
                
            if (view.scale >= 32):
                font = pygame.font.Font(None, int(4 * view.scale/10))
                # Draw star name to bottom-right of circle
                text = font.render(name, 1, (255, 255, 255))
                screen.blit(text, (x, y))
    else:
        screen.set_at((x, y), color)

    # Prominently redraw special star systems
    if (view.scale < 32):
        if (star.name in ['Sol', 'Treus-8']):
            color = (255, 255, 255)
            size = 2
            pygame.draw.circle(screen, color, (x, y), size)
            font = pygame.font.Font(None, 14)
            text = font.render(star.name, 1, color)
            screen.blit(text, (x+2, y+2))
        elif (star.name == 'Galactic Core'):
            size = 3
            pygame.draw.circle(screen, color, (x, y), size)
            font = pygame.font.Font(None, 14)
            text = font.render(star.name, 1, color)
            screen.blit(text, (x+3, y+3))

    #pygame.display.flip()


def main(stars_file="stars.bin"):
    stars = read_stars_from_file(stars_file)

    # Initialize view matrix
    view = ViewMatrix()
    
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Star Map Prototype")

    # Create a Pygame screen
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    
    # Set the screen background color
    screen.fill((0, 0, 0))

    # Draw background image
    image = pygame.image.load('bg.png')
    
    # Run the game loop
    running = True
    do_redraw = True
    while running:
        if do_redraw:
            # Clear the display
            screen.fill((0, 0, 0))

            # Blit the bg image onto the screen only if it will fit perfectly
            if ((0.45 < view.scale < 0.55) and (-1 < view.x < 1) and (-1 < view.y < 1)):
                screen.blit(pygame.transform.scale(image, screen.get_size()), (0, 0))

            # Draw the stars on the screen
            draw_stars(screen, stars, view)

            # Draw UI
            font = pygame.font.Font(None, 16)
            text = 'Position: ({}, {})  Zoom: {}x'.format(
                round(view.x, 2), round(view.y, 2), round(view.scale, 2))
            blot = font.render(text, 1, (255, 255, 255))
            screen.blit(blot, (10, 10))
            blot = font.render('Prototype', 1, (255, 255, 255))
            screen.blit(blot, (10, 26))

            # Update the display
            pygame.display.flip()

            # Done updating
            do_redraw = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_EQUALS:
                    view.zoom(1.1)
                    do_redraw = True
                elif event.key == pygame.K_MINUS:
                    view.zoom(1/1.1)
                    do_redraw = True
                elif event.key == pygame.K_UP:
                    view.translate(0, -1)
                    do_redraw = True
                elif event.key == pygame.K_DOWN:
                    view.translate(0, 1)
                    do_redraw = True
                elif event.key == pygame.K_LEFT:
                    view.translate(-1, 0)
                    do_redraw = True
                elif event.key == pygame.K_RIGHT:
                    view.translate(1, 0)
                    do_redraw = True
                elif event.key == pygame.K_SPACE:
                    view.scale = 0.5
                    view.x = 0
                    view.y = 0
                    do_redraw = True
            if event.type == pygame.MOUSEWHEEL:
                #todo not working?
                if event.y == 1:
                    view.zoom(1.1)
                elif event.y == -1:
                    view.zoom(1/1.1)

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    main()
