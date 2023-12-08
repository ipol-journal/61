#!/usr/bin/env python3

import subprocess
import argparse
from PIL import Image
import math

# parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--denoise", type=int)
ap.add_argument("--sigma", type=int)
ap.add_argument("--lambd", type=int) #radio
ap.add_argument("--lambd_dyn", type=str)
ap.add_argument("--lambd_fix", type=float)
args = ap.parse_args()


#denoise=1 : Guess noise, then denoise
add_noise = 1 if not args.denoise else 0
lambd_dyn = 1 if not args.lambd else 0

files = ['input_0', 'denoised', 'diff']
sigmaguessed = 10

#Guess noise then denoise
if args.denoise: 
    
    if lambd_dyn:
        #dynamic lambda
        option = 3
    else:
        #fixed lambda
        option = 4

    with open('guessed_lambda.txt', 'w') as file:           
        subprocess.run(['chambolle_ipol', str(option), 'input_0.png', str(sigmaguessed), str(args.lambd_fix), 'noisy.png', 'denoised.png'],stdout=file)


    subprocess.run(['imdiff_ipol', 'input_0.png', 'denoised.png', 'diff.png', str(args.sigma)])

else:
    #add noise then denoise
    
    #dynamic lambda
    if lambd_dyn:
        option = 1
    else:
        #fixed lambda
        option = 2
    
    files.append('noisy')
    with open('guessed_lambda.txt', 'w') as file:           
        subprocess.run(['chambolle_ipol', str(option), 'input_0.png', str(args.sigma), str(args.lambd_fix), 
                                'noisy.png', 'denoised.png'], stdout=file)

    with open('rmse_noisy.txt', 'w') as file:           
        subprocess.run(['imdiff_ipol', 'input_0.png', 'noisy.png', 'diff.png', str(args.sigma)], stdout=file)

    with open('rmse_denoised.txt', 'w') as file:           
        subprocess.run(['imdiff_ipol', 'input_0.png', 'denoised.png', 'diff.png', str(args.sigma)], stdout=file)


# Resize for visualization (always zoom by at least 2x)
(sizeX, sizeY) = Image.open('input_0.png').size
zoomfactor = max(1, int(math.ceil(480.0/max(sizeX, sizeY))))

if zoomfactor > 1:
    (sizeX, sizeY) = (zoomfactor*sizeX, zoomfactor*sizeY)
    
    for filename in files:
        im = Image.open(filename + '.png')
        im = im.resize((sizeX, sizeY))
        im.save(filename + '_zoom.png')
