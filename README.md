# Python MIDI Player working on Linux/Windows

![Exemple](exemple1.gif)  

## Requirements
**Python 3.6+**, **pip**

## Installation
`pip install --user -r requirements.txt`

## Usage
`python main.py [options ...] [midifiles ...]`

### Create a new particle texture
- Draw the particle that you want, pure white (255, 255, 255) will be transparent,
pure black (0,0,0) will be replaced by the channel color, and the rest will be unchanged.
Save it as PNG in resources, then use --particles_texture filename. (without the extension .png)

### Use another background
- Save the background as PNG in resources, then use --background_image filename. (without the extension .png)

![Exemple](exemple2.png)  

![Exemple](exemple3.png)  

### Troubleshooting
- The Gui is a bit laggy

    Disable Particles via option --no_particles

- There is no sound

    The Player doesn't produce any sound by itself. You need a MIDI synthesizer.

    On Windows, you probably already have one, but probably not on linux.

    Open a port with Timidity:

      install a soundfond like soundfond-fluid and a Jack Audio Connection Kit

      install Timidity++

      sudo modprobe snd-seq-device

      sudo modprobe snd-seq-midi

      timidity -iA -B2,8 -Os1l -s 44100

    List open port : `python main.py --list_port`

    Specify the port : `python main.py --port "TiMidity:TiMidity port 0 128:0" file.mid`

- The sound is ugly

    Your synthesizer/soundfont is bad. Change it. Or change midi port.
