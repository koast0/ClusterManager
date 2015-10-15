import argparse

def config_data () :
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--config", type=str, default='')
    result = []
    config_file = parser.parse_args().config
    try:
        config_data = open(config_file).readlines()
        for i in config_data:
            space_index = i.find(' ')
            i = i.lstrip()
            i = i.rstrip()
            if space_index == -1:
                if i.size()!=0:
                    result.append((i,''))
            else:
                result.append((i[0:space_index], i[space_index:]))

    except:
        print("Wrong config file")
        exit(0)
    return result


if __name__ == "__main__":
    data = config_data()
    print(data)
    


