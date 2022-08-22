# Generates BTCTools configuration files via NMAP-formatted IP ranges. - https://pool.btc.com/tools

import itertools
import configparser

btc_ini_template = 'btctools-template.ini'

# format: {'name': 'ip_range', ...}
ranges_to_add = {
                 # Example
                 "Pod 1": "192.168.1.1-80",
                 "Container 1": "10.10.1.1-200"
}


def expand_range(num_range: str):
    if '-' in num_range:
        lower, higher = list(map(int, num_range.split('-')))
        individual_numbers = []
        # Add +1 because iteration stops on the upper number
        for x in range(lower, higher + 1):
            individual_numbers.append(x)
        return individual_numbers
    else:
        return [num_range]


def alter_btctools_ini(new_ranges_dict: dict):
    formatted_text = []
    for name, ip_range in new_ranges_dict.items():
        first_expanded = second_expanded = third_expanded = fourth_expanded = None

        first_octet = ip_range.split(".")[0]
        first_expanded = expand_range(first_octet)

        second_octet = ip_range.split(".")[1]
        second_expanded = expand_range(second_octet)

        third_octet = ip_range.split(".")[2]
        third_expanded = expand_range(third_octet)

        fourth_octet = ip_range.split(".")[3]
        fourth_expanded = expand_range(fourth_octet)

        generated_entry = []
        for o1 in first_expanded:
            for o2 in second_expanded:
                for o3 in third_expanded:
                    generated_entry.append("{0}.{1}.{2}.{3}-{0}.{1}.{2}.{4}"
                                           .format(o1, o2, o3, fourth_expanded[0], fourth_expanded[-1]))

        formatted_text.append("#{}:".format(name) + ','.join(generated_entry))

    formatted_text = ';'.join(formatted_text)

    # Alters only ipRangeGroups
    config = configparser.ConfigParser()
    config.read(btc_ini_template)

    previous_value = config.get('ui', 'ipRangeGroups')

    # If alteration was already made, exit the function
    if formatted_text in previous_value:
        print("Alteration was already made!")
        return

    config.set('ui', 'ipRangeGroups', '"' + formatted_text + '"')

    with open("btctools.ini", 'w') as configfile:
        config.write(configfile)


alter_btctools_ini(ranges_to_add)