import argparse
import os

parser = argparse.ArgumentParser(
    prog="gbpkextractor",
    description="Extracts GoBit .pak files"
)

parser.add_argument("input_file", help=".pak file to process")
parser.add_argument("-o", "--output-dir", default="./output", help="Output directory for extracted .pak file")
parser.add_argument("-d", "--delete-old", action="store_true", help="Deletes old output files in the output directory")

PNGSTART = b'\x89\x50\x4E\x47'
PNGEND = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'

FILEINDEXSTART = b'\x47\x42\x50\x4b\x06\x14\x02\x00\x02\x00\x00\x00\x01\x90\x08\x00\x00\x19\x00'
FILEINDEXEND = b'\x08\xC6\x1C\x40\x60\x8C\x2B\xBA\x01\x79\xC9\x01'

FONTSZ = b'\x00\x66\x6f'
IMAGEZ = b'\x00\x69\x6d'
PNGFEND = b'\x2e\x70\x6e\x67'

# 4F 67 67 53 00 02: start page

# 4F 67 67 53 00 00: data page

# 4F 67 67 53 00 04: last page?

OGGSTART = b'\x4F\x67\x67\x53\x00\x02'
OGGEND = b'\x4F\x67\x67\x53\x00\x04'

def main():
    args = parser.parse_args()
    pakFileHandle = open(args.input_file, mode="rb")
    isgbpk = pakFileHandle.read(4)

    if isgbpk != b'GBPK':
        print("Provided file is not a GoBit .pak file (no GBPK header?)")
        return 1
    
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
        os.mkdir(args.output_dir + f"/./image_assets/")
        os.mkdir(args.output_dir + f"/./audio_assets/")

    pakFileHandle.seek(0)
    data = pakFileHandle.read()

    ### EXPERIMENTAL: File index reading
    ### ----- THIS IS BULLSHIT AND ONLY SEEMS TO HAVE FONT DATA ----- ###

    #print("-----[ Reading file index ]-----")
    #idx = 0
    #endidx = 0
    #
    #while True:
    #    idx = data.find(FONTSZ, endidx)
    #    endidx = data.find(PNGFEND, endidx) + len(PNGFEND)
    #
    #    print(f"Found a file index entry at offset {hex(idx)} to end {hex(endidx)}")
    #    
    #    pakFileHandle.seek(idx)
    #    readData = pakFileHandle.read(endidx - idx).replace(b'\x00', b'').replace(b'\xf8|mW', b'')
    #
    #    print(readData)
    #
    #return 1


    print("-----[ Extracting PNGs ]-----")

    idx = 0
    endidx = 0

    counter = 0
    while True:
        idx = data.find(PNGSTART, endidx)
        endidx = data.find(PNGEND, endidx) + len(PNGEND)
        print(f"Found a PNG block at offset {hex(idx)} to end {hex(endidx)} (length {endidx - idx} bytes)")

        counter += 1
        
        if (idx == -1):
            print("Found every PNG block")
            break

        pakFileHandle.seek(idx)
        readData = pakFileHandle.read(endidx - idx)

        if os.path.exists(args.output_dir + f"/./image_assets/{counter}.png"):
            os.remove(args.output_dir + f"/./image_assets/{counter}.png")
    
        with open(args.output_dir + f"/./image_assets/{counter}.png", "wb") as newFile:
            newFile.write(readData)
    

    pakFileHandle.seek(0)

    print("-----[ Extracting OGGs ]-----")

    idx = 0
    endidx = 0

    counter = 0
    while True:
        idx = data.find(OGGSTART, endidx)
        endidx = data.find(OGGEND, endidx) + len(OGGEND)
        print(f"Found an OGG block at offset {hex(idx)} to end {hex(endidx)} (length {endidx - idx} bytes)")

        counter += 1
        
        if (idx == -1):
            print("Found every OGG block")
            break

        pakFileHandle.seek(idx)
        readData = pakFileHandle.read(endidx - idx)

        if os.path.exists(args.output_dir + f"/./audio_assets/{counter}.ogg"):
            os.remove(args.output_dir + f"/./audio_assets/{counter}.ogg")
    
        with open(args.output_dir + f"/./audio_assets/{counter}.ogg", "wb") as newFile:
            newFile.write(readData)

    

if __name__ == "__main__":
    main()