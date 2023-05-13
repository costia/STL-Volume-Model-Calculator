#! /usr/bin/env python3
'''
VOLUME CALCULATION STL binary MODELS
Author: Mar Canet (mar.canet@gmail.com) - september 2012
Description: useful to calculate cost in a 3D printing ABS or PLA usage

Modified by:
Author: Saijin_Naib (Synper311@aol.com)
Date: 2016-06-26 03:55:13.879187
Description: Added input call for print material (ABS or PLA), added print of object mass, made Python3 compatible, changed tabs for spaces
Material Mass Source: https://www.toybuilderlabs.com/blogs/news/13053117-filament-volume-and-length
'''

import struct
import sys
import json

# move to external JSON
materialList = json.load(open('materials.json'))

print('Available materials:')
for ind, x in enumerate(materialList):
    print('\t {:d}: {:s}'.format(ind+1,x['name']))
materialInput = input('Enter material ID: ')

try:
    materialInput = int(materialInput)
    material = materialList[materialInput-1]
except:
    print('could not determine material type')
    exit(-1)


class STLUtils:
    def resetVariables(self):
        self.normals = []
        self.points = []
        self.triangles = []
        self.bytecount = []
        self.fb = []  # debug list

    # Calculate volume for the 3D mesh using Tetrahedron volume
    # based on: http://stackoverflow.com/questions/1406029/how-to-calculate-the-volume-of-a-3d-mesh-object-the-surface-of-which-is-made-up
    def signedVolumeOfTriangle(self, p1, p2, p3):
        v321 = p3[0] * p2[1] * p1[2]
        v231 = p2[0] * p3[1] * p1[2]
        v312 = p3[0] * p1[1] * p2[2]
        v132 = p1[0] * p3[1] * p2[2]
        v213 = p2[0] * p1[1] * p3[2]
        v123 = p1[0] * p2[1] * p3[2]
        return (1.0 / 6.0) * (-v321 + v231 + v312 - v132 - v213 + v123)

    def unpack(self, sig, l):
        s = self.f.read(l)
        self.fb.append(s)
        return struct.unpack(sig, s)

    def read_triangle(self):
        n = self.unpack('<3f', 12)
        p1 = self.unpack('<3f', 12)
        p2 = self.unpack('<3f', 12)
        p3 = self.unpack('<3f', 12)
        b = self.unpack('<h', 2)

        self.normals.append(n)
        l = len(self.points)
        self.points.append(p1)
        self.points.append(p2)
        self.points.append(p3)
        self.triangles.append((l, l + 1, l + 2))
        self.bytecount.append(b[0])
        return self.signedVolumeOfTriangle(p1, p2, p3)

    def read_length(self):
        length = struct.unpack('@i', self.f.read(4))
        return length[0]

    def read_header(self):
        self.f.seek(self.f.tell() + 80)

    def calculateVolume(self, infilename, unit):
        self.resetVariables()
        totalVolume = 0
        totalMass = 0
        try:
            self.f = open(infilename, 'rb')
            self.read_header()
            l = self.read_length()
            print('total triangles: {:,}'.format(l))
            count=0
            print('Calculating volume',end='',flush=True)
            try:
                while True:
                    totalVolume += self.read_triangle()
                    count = count+1
                    if count%100000==0:
                        print('.',end='',flush=True)
            except Exception as e:
                pass
            print('')
            totalVolume = (totalVolume / 1000)
            totalMass = totalVolume * material['density']
            print('Total mass: %.2fg'%totalMass)

            if unit == 'cm':
                print('Total volume: %.2fcm^3' % totalVolume)
            else:
                print('Total volume: %.2finch^3' % (totalVolume* 0.0610237441))
                    
        except Exception as e:
            print(e)
        return totalVolume


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Define model to calculate volume ej: python measure_volume.py torus.stl')
    else:
        mySTLUtils = STLUtils()
        measurmentUnit='cm'
        if(len(sys.argv) > 2 and sys.argv[2] == 'inch'):
            measurmentUnit='inch'
        
        mySTLUtils.calculateVolume(sys.argv[1], measurmentUnit)

