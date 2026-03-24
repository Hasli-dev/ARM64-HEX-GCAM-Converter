import argparse
from keystone import Ks, KS_ARCH_ARM, KS_ARCH_ARM64, KS_MODE_ARM, KS_MODE_THUMB, KsError
import sys

def assemble(assembly_code, arch, mode):
    try:
        ks_arch, ks_mode = (KS_ARCH_ARM, KS_MODE_THUMB if mode == 'thumb' else KS_MODE_ARM) if arch == 'arm' else (KS_ARCH_ARM64, 0)
        ks = Ks(ks_arch, ks_mode)
        encoding, count = ks.asm(assembly_code.encode('utf-8'))
        if encoding:
            return ''.join(f'{b:02x}' for b in encoding).upper(), None
        return None, f"Failed to assemble '{assembly_code}'"
    except KsError as e:
        return None, f"Assembly Error: {e}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("code")
    parser.add_argument("--arch", default="arm64")
    parser.add_argument("--mode", default="arm")
    args = parser.parse_args()

    hex_code, error = assemble(args.code, args.arch, args.mode)
    
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
        
    print(hex_code)

if __name__ == "__main__":
    main()
