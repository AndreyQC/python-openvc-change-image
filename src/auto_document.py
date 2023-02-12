import json
import os
import auto_document_modules as adm
import pandas as pd


class FilesToReview:
    config = "files to review"
    files = list()


class DataFlowObects:
    config_json = "dataflow.json"
    config_path = "set"
    objects = list()

    def save_as_json(self):
        json_str = json.dumps(self.__dict__)
        with open(Config.CFG_JSON_OUTPUT_FILE, 'w') as f1:
            f1.write(json_str)


def prepare_config_in_json(mp: FilesToReview):
    json_str = json.dumps(mp.__dict__)
    with open(Config.CFG_JSON_OUTPUT_FILE, 'w') as f1:
        f1.write(json_str)


def read_config_from_json():

    with open(os.path.join(Config.CFG_JSON_OUTPUT_FILE), 'r') as f:
        data = json.load(f)
    return data

def save_list_as_json(dflw_objects, folder, file_name):
    """
    dump list to json
    :param dflw_objects: list of dfwl objects
    :param folder:
    :return: none
    """
    json_str = json.dumps(dflw_objects)
    with open(os.path.join(folder, file_name + "." + "json"), 'w') as f1:
        f1.write(json_str)
    pass

class Config():
    """
    configuration
    """
    CFG_WORKING_PATH = r"C:\repos\SomeFirm\snowflake\Scripts\digital-bi-data-someproject.spic-sf-objects"
    CFG_EXCLUDED_PATHS = ["SCRIPTS","RELEASES_QAT"]
    CFG_CONTAINER_NAME = "DEV_someproject"
    CFG_CONTAINER_TYPE = "Snowflake database"
    CFG_JSON_OUTPUT_FILE = r"C:\repos\SomeFirm\snowflake\Scripts\digital-bi-data-someproject.spic-sf-objects\SCRIPTS\auto-document\output\output-files.json"
    CFG_CSV_OUTPUT_FILE = r"C:\repos\SomeFirm\snowflake\Scripts\digital-bi-data-someproject.spic-sf-objects\SCRIPTS\auto-document\output\output-csv-report.csv"
    CFG_JSON_OUTPUT_PATH = r"C:\repos\SomeFirm\snowflake\Scripts\digital-bi-data-someproject.spic-sf-objects\SCRIPTS\auto-document\output"    

def get_files_by_path(path, excluded_paths):
    """
    function accept path
    :param string: path
    :param string: excluded_paths
    :return: array of dictinaries 
    """
    list_of_files = []
    files_result = []
    for root, dirs, files in os.walk(path):
        for file in files:
            # print(f"------------- file  {root}   ---- {os.path.join(root, file)}")
            if not any(excluded_path in root for excluded_path in excluded_paths):
                list_of_files.append(os.path.join(root, file))
    for name in list_of_files:
        files_result.append(get_file_info(name))
    return files_result


def get_file_info(file_full_path):
    """
    function accept file full path and return parsed dict
    :param string: filefullpath
    :return: dict 
    """
    filepath, file_extension = os.path.splitext(file_full_path)
    file_info = dict()
    file_info['filename'] = os.path.basename(file_full_path)
    file_info['filedirname'] = os.path.dirname(file_full_path)
    file_info['fileextension'] = file_extension
    file_info['filefullpath'] = file_full_path
    return file_info

def prepare_json_with_objects():

    # prepare a list of scripts for review
    mp = FilesToReview()
    mp.config = "config"
    # get a list of files of snowflake database
    mp.files = [f for f in get_files_by_path(Config.CFG_WORKING_PATH, Config.CFG_EXCLUDED_PATHS) if f['fileextension'] == '.sql']
    
    for file in mp.files:
        print("-------" + file['filename'])
        # TODO - remove for debug
        # if file['filename'] == "Configuration.sql":
        object_from_file = adm.extract_object_from_file_snowflake(file["filefullpath"])
        if object_from_file["type"] != "null":
            object_from_file["container_name"] = Config.CFG_CONTAINER_NAME
            object_from_file["container_type"] = Config.CFG_CONTAINER_TYPE
            object_from_file["object_source_file_full_path"] = file["filefullpath"]
            object_from_file["object_key"] = Config.CFG_CONTAINER_TYPE + '/' + Config.CFG_CONTAINER_NAME + '/' + object_from_file[
                "type"] + '/' + object_from_file["fullname"]
            object_from_file["object_key"] = object_from_file["object_key"].replace(' ', '_')
            file["object"] = object_from_file

    # dump to json file
    prepare_config_in_json(mp)
    pass


if __name__ == '__main__':

    # prepare a json with files and database obects inside them
    # prepare_json_with_objects()
    data = read_config_from_json()

    db_objects = list()

    for file in data["files"]:
        db_obect = file.get("object")
        if db_obect:
            db_objects.append(db_obect)

    df = pd.DataFrame(db_objects)
    df.to_csv(Config.CFG_CSV_OUTPUT_FILE, index=False, header=True, sep=";")









