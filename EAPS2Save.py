import argparse, hashlib

class EAPS2Save:
    MAGIC = 0x4D433032
    HEADER_SIZE = 28
    POLY = 0x04C11DB7
    GAMES = {"nfsu": "Need For Speed Underground", "nfsu2": "Need For Speed Underground 2", "nfsmw": "Need For Speed Most Wanted",
             "nfsc": "Need For Speed Carbon", "nfsps": "Need For Speed ProStreet", "tg": "The Godfather"}

    def __init__(self, path, game):
        self.path = path
        self.game = game
        self.initCrcTab()

        with open(path, "rb") as f:
            self.data = bytearray(f.read())


    def initCrcTab(self):
        self.crctab = [0] * 256

        for i in range(256):
            crc = i << 24

            for _ in range(8):
                crc = ((crc << 1) ^ self.POLY) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF

            self.crctab[i] = crc


    def calcCrc(self, start, n):
        if n < 4: return 0

        crc = (self.data[start] << 24) | (self.data[start + 1] << 16) | (self.data[start + 2] << 8) | self.data[start + 3]
        crc = (~crc) & 0xFFFFFFFF
        n -= 4

        for i in range(start + 4, start + 4 + n):
            crc = (((crc << 8) | self.data[i]) ^ self.crctab[crc >> 24]) & 0xFFFFFFFF

        return (~crc) & 0xFFFFFFFF


    def calcCrcNfsu(self):
        n = len(self.data) - 4
        crc = 0xFFFFFFFF
        
        for i in range(n):
            crc = ((crc << 8) ^ self.crctab[(crc >> 24) ^ self.data[i]]) & 0xFFFFFFFF

        for b in n.to_bytes((n.bit_length() + 7) // 8, "little"):
            crc = ((crc << 8) ^ self.crctab[(crc >> 24) ^ b]) & 0xFFFFFFFF

        return (~crc) & 0xFFFFFFFF


    def check(self):
        print(f"Path: {self.path}")
        print(f"Game: {self.GAMES[self.game]}")

        if self.game == "nfsu":
            crc = int.from_bytes(self.data[len(self.data) - 4:], "little")

            print(f"Checksum: {crc}", end = "")
            if crc != self.calcCrcNfsu():
                print(" (invalid)", end = "")
            print()

            return

        magic = int.from_bytes(self.data[0:4], "little")
        size = int.from_bytes(self.data[4:8], "little")
        size1 = int.from_bytes(self.data[8:12], "little")
        size2 = int.from_bytes(self.data[12:16], "little")
        crc1 = int.from_bytes(self.data[16:20], "little")
        crc2 = int.from_bytes(self.data[20:24], "little")
        crc3 = int.from_bytes(self.data[24:28], "little")

        print(f"Magic: {magic}", end = "")
        if magic != self.MAGIC:
            print(" (invalid)", end = "")
        print()

        print(f"Size: {size}", end = "")
        if size != len(self.data):
            print(" (invalid)", end = "")
        print()

        print(f"Size 1: {size1}")
        print(f"Size 2: {size2}")

        print(f"Checksum 1: {crc1}", end = "")
        if crc1 != self.calcCrc(self.HEADER_SIZE, size1):
            print(" (invalid)", end = "")
        print()

        print(f"Checksum 2: {crc2}", end = "")
        if crc2 != self.calcCrc(self.HEADER_SIZE + size1, size2):
            print(" (invalid)", end = "")
        print()

        print(f"Checksum 3: {crc3}", end = "")
        if crc3 != self.calcCrc(0, self.HEADER_SIZE - 4):
            print(" (invalid)", end = "")
        print()

        if self.game == "nfsmw":
            md5 = self.data[len(self.data) - 16:].hex().upper()

            print(f"MD5: {md5}", end = "")
            if md5 != hashlib.md5(self.data[52:len(self.data) - 16]).hexdigest().upper():
                print(" (invalid)", end = "")
            print()


    def fix(self):
        if self.game == "nfsu":
            self.data[len(self.data) - 4:] = self.calcCrcNfsu().to_bytes(4, "little")

        else:
            if self.game == "nfsmw":
                self.data[len(self.data) - 16:] = hashlib.md5(self.data[52:len(self.data) - 16]).digest()

            size1 = int.from_bytes(self.data[8:12], "little")
            size2 = int.from_bytes(self.data[12:16], "little")
            self.data[16:20] = self.calcCrc(self.HEADER_SIZE, size1).to_bytes(4, "little")
            self.data[20:24] = self.calcCrc(self.HEADER_SIZE + size1, size2).to_bytes(4, "little")
            self.data[24:28] = self.calcCrc(0, self.HEADER_SIZE - 4).to_bytes(4, "little")

        with open(self.path, "wb") as f:
            f.write(self.data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", action = "store", help = "set save's path")
    parser.add_argument("-fix", action = "store_true", help = "fix save's checksums")
    parser.add_argument("-game", action = "store", help = "set save's game", choices = EAPS2Save.GAMES.keys())
    args = parser.parse_args()

    if args.fix:
        EAPS2Save(args.path, args.game).fix()

    else:
        EAPS2Save(args.path, args.game).check()