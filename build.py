import PyInstaller.__main__
import os
import shutil

# Get the current directory
path = os.path.dirname(os.path.abspath(__file__))

def build():
    # Clean up previous builds
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # PyInstaller arguments
    PyInstaller.__main__.run([
        'desktop.py',                 # Script to package
        '--name=AINews',             # App name
        '--windowed',                 # GUI app, no console
        '--noconfirm',                # Overwrite dist without asking
        '--add-data=templates:templates', # Include templates folder
        '--icon=icon.icns',           # Custom app icon
        '--clean',                    # Clean cache
    ])

if __name__ == '__main__':
    build()
