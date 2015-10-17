import argparse
import socket
import json


class Node:

    def __init__(self, hostname, address):
        self.hostname = hostname
        self.address = address


def start():
    pass


def GetConfigData(apps, nodes):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', "--apps", type=str, default='')
    parser.add_argument('-n', "--nodes", type=str, default='')
    config_file = parser.parse_args().apps
    try:
        config_data = open(config_file).readlines()
        for i in config_data:
            space_index = i.find(' ')
            apps.append(i.strip())
    except:
        print("Wrong apps file")
        exit(1)
    config_file = parser.parse_args().nodes
    try:
        config_data = open(config_file).readlines()
        for i in config_data:
            nodes.append(Node(i.split()[0], i.split()[1]))
    except:
        print("Wrong nodes file")
        exit(1)


def main():
    apps, nodes = [], []
    GetConfigData(apps, nodes)
    


if __name__ == "__main__":
    main()
