import re
import colorsys
import os
import math
import json
import zipfile

def is_hex_color(s):
    return bool(re.match(r'^#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', s))

def hex_to_rgb(hex_color):
    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex string into integer values and return the RGB tuple
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    elif len(hex_color) == 3:
        return tuple(int(hex_color[i]*2, 16) for i in range(3))
    else:
        raise ValueError("Invalid hex color format")
    
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def color_with_lightness(color, lightness):
    r, g, b = color
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
    new_r, new_g, new_b = colorsys.hls_to_rgb(h, lightness, s)
    return int(new_r * 255), int(new_g * 255), int(new_b * 255)

def hex_ref(hex:str):
    hex = '#' + hex.lstrip('#')
    if len(hex.lstrip('#')) == 3:
        hex += hex.lstrip('#')
    return hex

def rgb_ref(hex:str):
    hex_ref(hex)
    return ','.join([str(v) for v in hex_to_rgb(hex)])

def color_ref(hex:str):
    hex = hex_ref(hex).upper()
    rgb = rgb_ref(hex)
    cv = f'{hex} : {rgb}'
    return cv + ' ' * (21 - len(cv))

colors = {}

def colors_to_text():
    global colors
    text = ''

    color_names = list(colors.keys())
    text += '     | '
    for i in range(len(colors)):
        color = color_names[i]
        if i < len(colors) - 1:
            text += color
            if len(color) < 21:
                text += ' ' * (21 - len(color))
            text += ' | '
        else:
            text += color + '\n'
    
    text += 'main | '
    for i in range(len(colors)):
        color = color_names[i]
        if i < len(colors) - 1:
            text += color_ref(colors[color]['main']) + ' | '
        else:
            text += color_ref(colors[color]['main']) + '\n'

    text += 'base | '
    for i in range(len(colors)):
        color = color_names[i]
        if i < len(colors) - 1:
            text += color_ref(colors[color]['base']) + ' | '
        else:
            text += color_ref(colors[color]['base']) + '\n'
        
    for sh in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        if sh == 0.05 or sh == 0.95: text += f'{sh} | '
        else: text += f'{sh}  | '
        for i in range(len(colors)):
            color = color_names[i]
            if i < len(colors) - 1:
                text += color_ref(colors[color]['shades'][sh]) + ' | '
            else:
                text += color_ref(colors[color]['shades'][sh]) + '\n'
    return text

def colors_to_csv():
    global colors
    csv = []

    color_names = list(colors.keys())
    row1 = ['']
    row2 = ['']
    for i in range(len(colors)):
        color = color_names[i]
        row1.extend([color, '', '', ''])
        row2.extend(['HEX', 'R', 'G', 'B'])
    csv.append(row1)
    csv.append(row2)

    row1 = ['main']
    for i in range(len(colors)):
        color = color_names[i]
        rgb = rgb_ref(colors[color]['main'])
        row1.extend([hex_ref(colors[color]['main']), rgb])
    csv.append(row1)

    row1 = ['base']
    for i in range(len(colors)):
        color = color_names[i]
        rgb = rgb_ref(colors[color]['base'])
        row1.extend([hex_ref(colors[color]['base']), rgb])
    csv.append(row1)

    for sh in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
        row1 = [f'{sh}']
        for i in range(len(colors)):
            color = color_names[i]
            rgb = rgb_ref(colors[color]['shades'][sh])
            row1.extend([hex_ref(colors[color]['shades'][sh]), rgb])
        csv.append(row1)
    return '\n'.join([','.join(r) for r in csv])

def colors_to_svg():
    global colors
    color_names = list(colors.keys())
    width = 800
    padding = 25
    spacing = 50
    lg_box_size = 150
    lg_box_spacing = 60
    lg_box_n_x = math.floor((width - (padding * 2)) / (lg_box_size + lg_box_spacing))
    lg_box_n_y = math.ceil(len(colors) / lg_box_n_x)
    lg_box_x = (width - (padding * 2) - ((lg_box_n_x * (lg_box_size + lg_box_spacing)) - lg_box_spacing)) / 2
    sm_box_w = 100
    sm_box_h = 50
    sm_box_x = (width - (padding * 2) - (len(colors) * sm_box_w)) / 2
    height = padding * 2 + (lg_box_n_y * (lg_box_size + lg_box_spacing)) + spacing + sm_box_h * (len(colors[list(colors.keys())[0]]['shades']) + 1)

    svg_header = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" fill="#fefefe">\n'
    svg_content = ''
    x_i = 0
    y_i = 0
    for i in range(len(colors)):
        color = color_names[i]
        if x_i > lg_box_n_x - 1:
            x_i = 0
            y_i += 1

        box_x = padding + lg_box_x + x_i * (lg_box_size + lg_box_spacing)
        box_y = padding + y_i * (lg_box_size + lg_box_spacing)
        x_i += 1
        svg_content += f'''
            <rect x="{box_x}" y="{box_y}" width="{lg_box_size}" height="{lg_box_size}" fill="{hex_ref(colors[color]['main'])}" />
            <text x="{box_x + (lg_box_size / 2)}" y="{box_y + lg_box_size + 25}" font-size="20" font-family="Helvetica" text-anchor="middle" fill="{hex_ref(colors[color]['main'])}">
                {color}
            </text>
            <text x="{box_x + (lg_box_size / 2)}" y="{box_y + lg_box_size + 45}" font-size="16" font-family="Helvetica" text-anchor="middle" fill="{hex_ref(colors[color]['main'])}">
                {hex_ref(colors[color]['main']).upper()}
            </text>
        '''
    
    for i in range(len(colors)):
        y_i = 0
        color = color_names[i]
        shades = list(colors[color]['shades'].keys())
        shades.reverse()
        box_x = padding + sm_box_x + i * sm_box_w 
        box_y = padding + lg_box_n_y * (lg_box_size + lg_box_spacing) + spacing + y_i * sm_box_h
        y_i += 1
        svg_content += f'''
        <rect x="{box_x}" y="{box_y}" width="{sm_box_w}" height="{sm_box_h}" fill="{hex_ref(colors[color]['main'])}" />
        <text x="{box_x + (sm_box_w / 2)}" y="{box_y + (sm_box_h / 2) + 5}" font-size="20" font-family="Helvetica" text-anchor="middle" fill="#fefefe">
            {color}
        </text>
        '''

        for s in range(len(colors[color]['shades'])):
            shade = shades[s]
            box_x = padding + sm_box_x + i * sm_box_w 
            box_y = padding + lg_box_n_y * (lg_box_size + lg_box_spacing) + spacing + y_i * sm_box_h
            y_i += 1
            svg_content += f'''
            <rect x="{box_x}" y="{box_y}" width="{sm_box_w}" height="{sm_box_h}" fill="{hex_ref(colors[color]['shades'][shade])}" />
            <text x="{box_x + (sm_box_w / 2)}" y="{box_y + (sm_box_h / 2) + 5}" font-size="20" font-family="Helvetica" text-anchor="middle" fill="#fefefe">
                {hex_ref(colors[color]['shades'][shade]).upper()}
            </text>
        '''

    svg_footer = '</svg>'
    return svg_header + svg_content + svg_footer

def color_to_figma(color, pname):
    global colors
    figma = {pname: {}}
    color_names = list(colors.keys())
    figma[pname][color] = {
        shd: {
            "$type": "color",
            "$value": colors[color]['shades'][shd]
        } for shd in colors[color_names[0]]['shades']
    }
    return figma


if __name__ == "__main__":
    print('Welcome to the Color Palette generator.')
    print('Prepare your colors in hexadecimal format. Suggestion: Use a tool like www.coolors.com to help you build your initial color palette.')

    while True:
        color = input('\nEnter a hexadecimal color value or enter an empty line to end.\n>> ')

        if color == '':
            break

        if not is_hex_color(color):
            print('Invalid hexadecimal color code. Try again.')
            continue

        name = input('Give this color a name >> ')
        colors[name] = {
            'main': color
        }
    
    if len(colors) > 0:
        for color in colors:
            rgb = hex_to_rgb(colors[color]['main'])
            colors[color]['base'] = rgb_to_hex(color_with_lightness(rgb, 0.5))
            colors[color]['shades'] = {m: rgb_to_hex(color_with_lightness(rgb, m)) for m in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]}


        input('\nHit enter for the results >> ')

        print(colors_to_text())

        while True:
            next = input('\nEnter "e" to export or an empty line to end >> ')
            if next == '':
                break
            
            if next != 'e':
                print('Invalid input. Try again.')
                continue

            while True:
                print('Choose a format to export:\n1) Text File\n2) Comma-Separated Values (CSV)\n3) Scalable Vector Graphic (SVG)\n4) Figma Variables')
                format = input('>> ')

                if format == '':
                    break

                try:
                    format = int(format)
                except ValueError:
                    print('Enter a number between 1 and 4 or an empty line to end. Try again.')
                    continue

                if format < 1 and format > 4:
                    print('Invalid entry. Try again.')
                    continue
                
                print('What would you like to name the file?')
                fn = input('>> ')
                fn = fn.removesuffix('.txt').removesuffix('.svg').removesuffix('.csv').removesuffix('.json').removesuffix('.zip')
                if not os.path.isabs(fn):
                    fpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), fn)
                else:
                    fpath = fn
                if format == 1:
                    with open(fpath + '.txt', 'w') as f:
                        f.write(colors_to_text())
                elif format == 2:
                    with open(fpath + '.csv', 'w') as f:
                        f.write(colors_to_csv())
                elif format == 3:
                    with open(fpath + '.svg', 'w') as f:
                        f.write(colors_to_svg())
                elif format == 4:
                    fns = []
                    for c in colors:
                        with open(fpath + '_' + c + '.json', 'w') as f:
                            json.dump(color_to_figma(c, fn), f)
                        fns.append(fpath + '_' + c + '.json')
                    with zipfile.ZipFile(fpath + '.zip', 'w') as zipf:
                        for file in fns:
                            if os.path.isfile(file):
                                zipf.write(file, os.path.basename(file))
                            else:
                                print(f"File {file} does not exist and will be skipped.")
                    for file in fns:
                        os.remove(file)
                break

            