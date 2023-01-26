import os
import re
import sys
import shutil

from os.path import split
from pathlib import Path
from sys import argv


def create_folders_from_groups(path_to_folder, folder_names):
    """This func creates folders for sorted files"""
    for folder_for_sorted in folder_names.keys():

        os.makedirs(path_to_folder + '\\' + folder_for_sorted, exist_ok=True)


def delete_empty_folders(paths_to_folders):
    """This func removes empty folders"""
    for folder_path in paths_to_folders:
        folder_path = Path(folder_path)
        if folder_path.is_dir() and not next(folder_path.iterdir(), None):
            os.rmdir(folder_path)
            delete_empty_folders(paths_to_folders)


def normalize(item_name):
    """This func takes a file name string, translates and returns a string"""
    item_name = re.sub(r'\W', '_', item_name.split('.')[0]) + '.' + item_name.split('.')[-1]
    cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    latin = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t",
             "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    translating_map = {}
    for cyril_symbol, latin_symbol in zip(cyrillic, latin):
        translating_map[ord(cyril_symbol)] = latin_symbol
        translating_map[ord(cyril_symbol.upper())] = latin_symbol.upper()
    table = item_name.maketrans(translating_map)
    return str(item_name).translate(table)


def parse_files(folder_path, ignore_list):
    """This func iterates through the files and returns the names and paths of all files in the argument-folder"""
    path = Path(folder_path)
    file_names = []
    set_of_paths = set()
    for item in path.rglob("*"):
        if item.is_file():
            file_names.append(item.name)
            if split(item)[0].split('\\')[-1] not in ignore_list:
                set_of_paths.add(Path(item))
    return file_names, set_of_paths


def parse_folders(folder_path):
    """This func iterates through the folders and returns the names and paths of all folders in the argument-folder"""
    ignore_list = ['images', 'video', 'documents', 'audio', 'archives']
    path = Path(folder_path)
    names_of_folders = []
    set_of_paths = set()
    for item in path.rglob("*"):
        if not item.is_file():
            if item.name not in ignore_list:
                names_of_folders.append(item.name)
                set_of_paths.add(Path(item))
    return names_of_folders, set_of_paths


def sort_files(paths_to_files, file_groups, path_folder_for_sort, ignore_list):
    """This func moves all files to folders for sorted"""
    for path_to_file in paths_to_files:
        # get previously folder (/ARCHIVES/file.rar)
        previously_folder = split(path_to_file)[0].split('\\')[-2]
        for name_of_group, formats_list in file_groups.items():
            # check if folder in ignore list
            if split(path_to_file)[-1] in formats_list and previously_folder not in ignore_list:
                if Path(path_to_file) != Path(path_folder_for_sort + '\\' + name_of_group + '\\' + split(path_to_file)[-1]):
                    shutil.move(path_to_file, path_folder_for_sort + '\\' + name_of_group + '\\')


def unpack_archives(path_to_archives, groups_of_format):
    # path to folder 'archives' with sorted archives
    path_to_archives = Path(str(path_to_archives) + '\\' + 'archives')
    for archive in path_to_archives.rglob('*'):
        # checks if format is known in archive formats
        if archive.name.split('.')[-1].upper() in groups_of_format['archives']:
            # gets name with archive name for folder
            path_for_unpack = Path(str(path_to_archives) + '\\' + archive.name.split('.')[0])
            # creates folder with name for folder
            os.mkdir(path_for_unpack)
            # unpack archive to created folder
            shutil.unpack_archive(archive, path_for_unpack, archive.name.split('.')[-1])


def main():
    # path to current folder
    path_folder_for_sort = os.getcwd()
    # ignore list with names of folders to be ignored
    ignore_list = ['images', 'video', 'documents', 'audio', 'archives']

    groups_of_format = {
        'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
        'video': ['AVI', 'MP4', 'MOV', 'MKV'],
        'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
        'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
        'archives': ['ZIP', 'GZ', 'TAR'],
    }
    # dict with files in its type of format
    groups_of_files = {
        'images': [],
        'video': [],
        'documents': [],
        'audio': [],
        'archives': [],
    }

    set_of_formats = set()  # create set for known formats of files
    set_of_unknown_formats = set()  # create set for unknown formats of files
    # Create lists with names and paths to files and folders
    files_names, files_paths = parse_files(path_folder_for_sort, ignore_list)
    folders_names, folders_paths = parse_folders(path_folder_for_sort)

    # Fill sets of known and unknown formats
    for file in files_names:
        for name_group, formats in groups_of_format.items():
            if file.split('.')[-1].upper() in formats:
                set_of_formats.add(file.split('.')[-1])
            elif file.split('.')[-1].upper() not in formats:
                set_of_unknown_formats.add(file.split('.')[-1])
                set_of_unknown_formats = set_of_unknown_formats.difference(set_of_formats)
    # Rename all files by normalize
    for file_for_rename in files_paths:
        for known_formats in groups_of_format.values():
            if str(file_for_rename).split('.')[-1].upper() in known_formats:
                new_name = normalize(file_for_rename.name)
                os.rename(file_for_rename, split(file_for_rename)[0] + '\\' + new_name)
    # Rename all folders
    list_of_paths = [str(folder_path_for_sort) for folder_path_for_sort in folders_paths]
    list_of_paths = reversed(sorted(list_of_paths, key=len))  # sorted paths by len to sort in correctly turn
    for folder_for_rename in list_of_paths:
        new_name = normalize(str(Path(folder_for_rename).name))
        os.rename(folder_for_rename, str(split(folder_for_rename)[0]) + '\\' + new_name.split('.')[0])
    # Update lists with names and paths to files and folders after renaming
    files_names, files_paths = parse_files(path_folder_for_sort, ignore_list)
    folders_names, folders_paths = parse_folders(path_folder_for_sort)
    # Fill list with file names and formats of files
    for file in files_names:
        for name_group, formats in groups_of_format.items():
            if file.split('.')[-1].upper() in formats:
                groups_of_files[name_group].append(file)
    # Calling functions
    create_folders_from_groups(path_folder_for_sort, groups_of_format)
    sort_files(files_paths, groups_of_files, path_folder_for_sort, ignore_list)
    delete_empty_folders(folders_paths)
    unpack_archives(Path(path_folder_for_sort), groups_of_format)
    # Data output
    for name, list_of_formats in groups_of_files.items():
        print(f'In category {name} files: {list_of_formats}')
    print('Known formats: ', ', '.join(set_of_formats))
    print('Unknown formats: ', ', '.join(set_of_unknown_formats))


if __name__ == '__main__':
    main()
