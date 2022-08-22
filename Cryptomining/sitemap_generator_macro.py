import itertools

# Generates Sitemap CSV files for Foreman - https://foreman.mn/

# Racks = shelving units/sections
ip_ranges = ["10.7.1-40.1-24"]  # Ranges in NMAP format, individual addresses will generate in descending order
rack_range = range(40)  # You have to name racks as ascending numbers in the Foreman sitemap: 1, 2, 3, 4, etc.
rack_size = range(24)  # How many miners are on a rack
rows_per_rack = range(6)  # How many shelves/rows are on a rack
index_per_row = range(4)  # How many miners are on a shelf
pickaxe_id = "ce6ca240-6db9-47dd-8e74-8955f7b6a549"  # Get this from Foreman's pickaxe section
miner_port = "4028"  # API port for Antminer devices
header = ["pickaxe_id", "miner_ip", "miner_port", "rack", "row", "index"]  # CSV header that Foreman accepts


def generate_rack_cells(rack_range, rack_size):
    entries = []
    for rack in rack_range:
        for x in rack_size:
            entries.append(rack + 1)  # adding 1 because counting starts from 0
    return entries


def generate_row_cells(index_per_row, rows_per_rack, rack_range):
    entries = []
    for rack in rack_range:
        for row in rows_per_rack:
            for index in index_per_row:
                entries.append(row)  # adding 1 because counting starts from 0
    return entries


def generate_index_cells(index_per_row, rows_per_rack, rack_range):
    entries = []
    for rack in rack_range:
        for row in rows_per_rack:
            for index in index_per_row:
                entries.append(index)
    return entries


def expand_ip_ranges(ip_ranges):
    address_list = []
    for item in ip_ranges:
        octets = item.split('.')
        chunks = [list(map(int, octet.split('-'))) for octet in octets]
        ranges = [range(c[0], c[1] + 1) if len(c) == 2 else c for c in chunks]

        for address in itertools.product(*ranges):
            address_list.append('.'.join(map(str, address)))
    return address_list


def generate_sitemap_macro():
    doc = XSCRIPTCONTEXT.getDocument()
    sheet = doc.CurrentController.ActiveSheet

    # Fill header
    row = 0
    column = 0
    for item in header:
        cell = sheet[row, column]
        cell.setString(item)
        column += 1


    # Fill miner_ip column
    column = 1  # B
    row = 1
    host_list = expand_ip_ranges(ip_ranges)
    host_length = len(host_list)
    for host in host_list:
        cell = sheet[row, column]
        cell.setString(str(host))
        row += 1

    # Fill rack column
    column = 3
    row = 1
    for rack_entry in generate_rack_cells(rack_range, rack_size):
        cell = sheet[row, column]
        cell.setString(str(rack_entry))
        row += 1

    # Fill row column
    column = 4
    row = 1
    for row_entry in generate_row_cells(index_per_row, rows_per_rack, rack_range):
        cell = sheet[row, column]
        cell.setString(str(row_entry))
        row += 1

    # Fill index column
    column = 5
    row = 1
    for index in generate_index_cells(index_per_row, rows_per_rack, rack_range):
        cell = sheet[row, column]
        cell.setString(str(index))  # adding 1 because counting starts from 0
        row += 1

    # Fill pickaxe_id column
    column = 0
    row = 1
    for cell in range(host_length):
        cell = sheet[row, column]
        cell.setString(pickaxe_id)
        row += 1

    # Fill miner_port column
    column = 2
    row = 1
    for cell in range(host_length):
        cell = sheet[row, column]
        cell.setString(miner_port)
        row += 1


print(expand_ip_ranges(ip_ranges))
