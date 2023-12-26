import csv

# Your dictionary
htpg = {'192.168.0.2': [('NetBT', 'CVE-2017-0161', 0.6, ('192.168.0.4', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.04, ('192.168.0.4', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.5, ('192.168.0.4', 'Root')),
                                      ('Apache', 'CVE-2017-9798', 0.8, ('192.168.0.3', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.6, ('192.168.0.3', 'Root')),], 
                      '192.168.0.3': [('Apache', 'CVE-2017-9798', 0.5, ('192.168.0.5', 'User')),
                                      ('Apache', 'CVE-2014-0226', 0.1, ('192.168.0.5', 'Root')),], 
                      '192.168.0.4': [('NetBT', 'CVE-2017-0161', 0.8, ('192.168.0.5', 'User')),
                                      ('Win32k', 'CVE-2018-8120', 0.02, ('192.168.0.5', 'Root')),
                                      ('VBScript', 'CVE-2018-8174', 0.2, ('192.168.0.5', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.4, ('192.168.0.6', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.2, ('192.168.0.6', 'Root')),
                                      ('HFS', 'CVE-2014-6287', 0.3, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.7', 'Root')),], 
                      '192.168.0.5': [('HFS', 'CVE-2014-6287', 0.6, ('192.168.0.7', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.3, ('192.168.0.7', 'Root')),
                                      ('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root')),],
                      '192.168.0.6': [],
                      '192.168.0.7': [('OJVM', 'CVE-2016-5555', 0.2, ('192.168.0.8', 'User')),
                                      ('RDP', 'CVE-2012-0002', 0.1, ('192.168.0.8', 'Root'))],
                      '192.168.0.8': [],}

# Open a csv file for writing
with open('htpg.csv', 'w', newline='') as csvfile:
    # Create a csv writer object
    writer = csv.writer(csvfile)
    # Write the header row
    writer.writerow(['source', 'service', 'cve', 'exploit_prob', 'target', 'privilege'])
    # Loop through the dictionary
    for source, services in htpg.items():
        # Loop through the list of tuples
        for service, cve, exploit_prob, (target, privilege) in services:
            # Write a row for each edge
            writer.writerow([source, service, cve, exploit_prob, target, privilege])