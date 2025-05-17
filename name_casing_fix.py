def print_inconsistent_cases(resource_file):
    """
    Scans through the JSON list of matched names and prints out any instances where a folder name is
    inconsistently cased.
    """
    prev = ''

    for line in open(resource_file, 'r'):
        split_line = line.split('/')
        split_prev = prev.split('/')
        for index, folder in enumerate(split_prev):
            if index >= len(split_line):
                continue
            if not split_line[index] == folder:
                if split_line[index].lower() == folder.lower():
                    partial_prev = '/'.join(split_prev[:index + 1])
                    partial_line = '/'.join(split_line[:index + 1])
                    print(f"{partial_prev.strip()}: {partial_line.strip()}")
                break

        prev = line

if __name__ == '__main__':
    mp_resource_file = r'./output_json/mp_resource_names.json'
    print_inconsistent_cases(mp_resource_file)
