def check_compatibility(cpu, gpu, ram, motherboard, storage, psu, case):
    errors = []
    total_power = 50  # Base system overhead

    # Rule 1: CPU socket vs Motherboard socket
    if cpu and motherboard:
        if cpu.socket != motherboard.socket:
            errors.append(
                f'CPU/Motherboard socket mismatch: {cpu.name} uses {cpu.socket} '
                f'but {motherboard.name} supports {motherboard.socket}.'
            )

    # Rule 2: RAM type vs Motherboard RAM support
    if ram and motherboard:
        if ram.ram_type != motherboard.ram_type:
            errors.append(
                f'RAM type mismatch: {ram.name} is {ram.ram_type} but '
                f'{motherboard.name} supports {motherboard.ram_type}.'
            )

    # Rule 3: PSU wattage vs total system power draw
    if cpu and cpu.power_draw:
        total_power += cpu.power_draw
    if gpu and gpu.power_draw:
        total_power += gpu.power_draw
    if psu:
        if psu.wattage < total_power:
            errors.append(
                f'PSU too weak: System needs ~{total_power}W but '
                f'{psu.name} only provides {psu.wattage}W.'
            )

    # Rule 4: Case form factor vs Motherboard form factor
    fits = {'ATX': ['ATX'], 'mATX': ['ATX', 'mATX'], 'ITX': ['ATX', 'mATX', 'ITX']}
    if case and motherboard and motherboard.form_factor and case.form_factor:
        if case.form_factor not in fits.get(motherboard.form_factor, []):
            errors.append(
                f'Form factor mismatch: {case.name} ({case.form_factor}) does not '
                f'fit {motherboard.name} ({motherboard.form_factor}).'
            )

    return {
        'is_compatible': len(errors) == 0,
        'errors': errors,
        'total_power': total_power
    }
