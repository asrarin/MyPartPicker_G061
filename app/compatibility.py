


def check_compatibility(cpu, gpu, ram, motherboard, storage, psu, case):
    errors      = []
    total_power = 50  # base system overhead (fans, drives, etc.)

    # Rule 1 — CPU socket must match Motherboard socket
    if cpu and motherboard:
        if cpu.socket and motherboard.socket:
            if cpu.socket.upper() != motherboard.socket.upper():
                errors.append(
                    f'CPU/Motherboard socket mismatch: '
                    f'{cpu.name} uses {cpu.socket} but '
                    f'{motherboard.name} requires {motherboard.socket}.'
                )

    # Rule 2 — RAM type must match Motherboard RAM support
    if ram and motherboard:
        if ram.ram_type and motherboard.ram_type:
            if ram.ram_type.upper() != motherboard.ram_type.upper():
                errors.append(
                    f'RAM type mismatch: '
                    f'{ram.name} is {ram.ram_type} but '
                    f'{motherboard.name} supports {motherboard.ram_type}.'
                )

    # Rule 3 — PSU wattage must cover total system power draw
    if cpu and cpu.power_draw:
        total_power += cpu.power_draw
    if gpu and gpu.power_draw:
        total_power += gpu.power_draw

    if psu and psu.wattage:
        if psu.wattage < total_power:
            errors.append(
                f'PSU too weak: system needs ~{total_power}W but '
                f'{psu.name} only provides {psu.wattage}W.'
            )

    # Rule 4 — Case form factor must fit Motherboard size
    fits = {
        'ATX':  ['ATX'],
        'mATX': ['ATX', 'mATX'],
        'ITX':  ['ATX', 'mATX', 'ITX'],
    }
    if case and motherboard:
        if case.form_factor and motherboard.form_factor:
            allowed = fits.get(motherboard.form_factor, [motherboard.form_factor])
            if case.form_factor not in allowed:
                errors.append(
                    f'Form factor mismatch: '
                    f'{case.name} ({case.form_factor}) does not fit '
                    f'{motherboard.name} ({motherboard.form_factor}). '
                    f'Compatible cases: {", ".join(allowed)}.'
                )

    return {
        'is_compatible': len(errors) == 0,
        'errors':        errors,
        'total_power':   total_power,
    }
