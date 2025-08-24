import sys
import os

def xor_encrypt(data, key):
    encrypted_data = bytearray()
    for i in range(len(data)):
        encrypted_data.append(data[i] ^ key[i % len(key)])
    return encrypted_data

def generate_random_key(length=32):
    return os.urandom(length)

def main():
    if not os.path.exists("shellcode.bin"):
        print("Error: shellcode.bin not found")
        sys.exit(1)

    with open("shellcode.bin", "rb") as f:
        shellcode = f.read()

    key = generate_random_key()
    encrypted_shellcode = xor_encrypt(shellcode, key)

    with open("shellcode.h", "w") as f:
        f.write("// shellcode.h\n")
        f.write("// Encrypted shellcode and decryption key\n")
        f.write("#pragma once\n\n")
        f.write("unsigned char encrypted_shellcode[] = {\n")
        for i, byte in enumerate(encrypted_shellcode):
            f.write(f"0x{byte:02x},")
            if (i + 1) % 16 == 0:
                f.write("\n")
        f.write("\n};\n\n")

        f.write("unsigned char key[] = {\n")
        for i, byte in enumerate(key):
            f.write(f"0x{byte:02x},")
            if (i + 1) % 16 == 0:
                f.write("\n")
        f.write("\n};\n")

    print("Shellcode encrypted and shellcode.h generated")

if __name__ == "__main__":
    main()