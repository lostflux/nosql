from configparser import ConfigParser
  
def read_db_config(filename='dbconfig.ini', section='mongodb'):
    """ Read database configuration file and return a dictionary object
    Based on examples from [MySQL with Python tutorial ](http://www.mysqltutorial.org/python-mysql)
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """

    # create parser and read ini configuration file, default 'dbconfig.ini'
    parser = ConfigParser()
    parser.read(filename)
 
    # get section, default to mysql
    dbconfig = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            dbconfig[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
 
    return dbconfig

