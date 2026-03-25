import argparse
import json
from keystone import Ks, KS_ARCH_ARM, KS_ARCH_ARM64, KS_MODE_ARM, KS_MODE_THUMB, KsError
from capstone import Cs, CS_ARCH_ARM, CS_ARCH_ARM64, CS_MODE_ARM, CS_MODE_THUMB, CsError
import sys

def assemble(assembly_code, arch, mode):
    try:
        ks_arch, ks_mode = (KS_ARCH_ARM, KS_MODE_THUMB if mode == 'thumb' else KS_MODE_ARM) if arch == 'arm' else (KS_ARCH_ARM64, 0)
        ks = Ks(ks_arch, ks_mode)
        
        instructions = [line.strip() for line in assembly_code.strip().split('\n') if line.strip()]
        results = []

        for instruction in instructions:
            try:
                encoding, count = ks.asm(instruction.encode('utf-8'))
                if encoding:
                    hex_code = ''.join(f'{b:02x}' for b in encoding).upper()
                    results.append({"instruction": instruction, "hex": hex_code})
                else:
                    results.append({"instruction": instruction, "hex": None})
            except KsError:
                results.append({"instruction": instruction, "hex": None})
        
        return {"results": results}, None

    except Exception as e:
        return None, f"Assembly Setup Error: {e}"

def disassemble(hex_code, arch, mode):
    try:
        cs_arch, cs_mode = (CS_ARCH_ARM, CS_MODE_THUMB if mode == 'thumb' else CS_MODE_ARM) if arch == 'arm' else (CS_ARCH_ARM64, CS_MODE_ARM)
        cs = Cs(cs_arch, cs_mode)
        
        all_asm = []
        hex_lines = hex_code.strip().split()

        for line in hex_lines:
            try:
                code_bytes = bytes.fromhex(line)
                asm_instructions = []
                for i in cs.disasm(code_bytes, 0):
                    asm_instructions.append(f"{i.mnemonic} {i.op_str}")
                if not asm_instructions:
                     all_asm.append(f"Failed to disassemble '{line}'")
                else:
                    all_asm.append('\n'.join(asm_instructions))
            except ValueError:
                all_asm.append(f"Invalid HEX value: '{line}'")

        return {"disassembly": '\n'.join(all_asm)}, None

    except CsError as e:
        return None, f"Disassembly Error: {e}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("code")
    parser.add_argument("--arch", default="arm64")
    parser.add_argument("--mode", default="arm")
    parser.add_argument("--action", default="assemble", choices=['assemble', 'disassemble'])
    args = parser.parse_args()

    if args.action == 'assemble':
        result, error = assemble(args.code, args.arch, args.mode)
    else:
        result, error = disassemble(args.code, args.arch, args.mode)
    
    if error:
        print(json.dumps({'error': error}), file=sys.stderr)
        sys.exit(1)
        
    print(json.dumps(result))

if __name__ == "__main__":
    main()
