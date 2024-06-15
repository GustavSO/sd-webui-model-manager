from ast import Dict
import json

from pathlib import Path
from pyexpat import model
from typing import List
from scripts.mm_libs.debug import d_debug
from scripts.mm_libs.model import convert_size
from modules import scripts

CACHE_LOCATION: Path = Path(scripts.basedir()) / "data"
CACHE_FILE = Path(scripts.basedir()) / "data/storage_cache.json"

class FileDetail:
    '''Class to store the details of a file.'''
    def __init__(self, filePath: str, fileName: str, fileSize: float, sha256: str, crc32: str, blake3: str, api: str):
        self.filePath : Path = Path(filePath)
        self.fileName : str = fileName
        self.fileSize : float = fileSize
        self.sha256 : str = sha256
        self.crc32 : str = crc32
        self.blake3 : str = blake3
        self.api : str = api

    def get_hash(self) -> str:
        '''Get the hash of the file.'''
        return self.crc32 or self.sha256 or self.blake3 or "No Hash"

    def __str__(self):
        return f"File: {self.fileName} - Size: {convert_size(self.fileSize)} - SHA256: {self.sha256} - CRC32: {self.crc32} - Blake3: {self.blake3} - API: {self.api}"
    
    def to_dict(self):
        return {
            "filePath": str(self.filePath),
            "fileName": self.fileName,
            "fileSize": self.fileSize,
            "sha256": self.sha256,
            "crc32": self.crc32,
            "blake3": self.blake3,
            "api": self.api
        }
    
    @staticmethod
    def from_dict(dict):
        return FileDetail(**dict)

class ModelType:
    '''Class to store the details of a model type'''
    def __init__(self):
        self.count = 0
        self.size = 0.0  # This could be calculated based on the fileSize of each FileDetail
        self.hashedCount = 0
        self.sha256Count = 0
        self.crc32Count = 0
        self.blake3Count = 0
        self.files: List[FileDetail] = []

    def update_size(self, fileSize: float):
        self.size += fileSize

    def to_dict(self, short=False):
        if short:
            return {
                "count": self.count,
                "size": convert_size(self.size),
                "hashedCount": self.hashedCount,
                "sha256Count": self.sha256Count,
                "crc32Count": self.crc32Count,
                "blake3Count": self.blake3Count,
                "files": "[...]"
            }
        
        return {
            "count": self.count,
            "size": self.size,
            "hashedCount": self.hashedCount,
            "sha256Count": self.sha256Count,
            "crc32Count": self.crc32Count,
            "blake3Count": self.blake3Count,
            "files": [file.to_dict() for file in self.files]
        }
    

    def from_dict(dict):
        model_type = ModelType()
        model_type.count = dict["count"]
        model_type.size = dict["size"]
        model_type.hashedCount = dict["hashedCount"]
        model_type.sha256Count = dict["sha256Count"]
        model_type.crc32Count = dict["crc32Count"]
        model_type.blake3Count = dict["blake3Count"]
        model_type.files = [FileDetail(**file) for file in dict["files"]]
        return model_type


class Storage:
    '''Class to store the details of the storage. It is a singleton class.'''
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Storage, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.modelTypes = {
                "TextualInversion": ModelType(),
                "Hypernetwork": ModelType(),
                "Checkpoint": ModelType(),
                "LORA": ModelType()
            }
            self.initialize_storage()
            self.initialized = True

    def initialize_new_cache(self):
        '''Initialize the storage to default values. And save it to the cache file.'''
        self.modelTypes = {
            "TextualInversion": ModelType(),
            "Hypernetwork": ModelType(),
            "Checkpoint": ModelType(),
            "LORA": ModelType()
        }
        self.totalCount = 0
        self.totalSize = 0.0
        self.hashedTotalSize = 0.0
        self.nonHashedTotalSize = 0.0

        self.update_cache_file()


    def initialize_storage(self):
        '''Tries to load the cache file. If it doesn't exists it creates it.'''
        if not CACHE_FILE.exists():
            d_debug(f"Cache file not found at {CACHE_FILE}")
            self.create_cache_file()
            self.initialize_new_cache()
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                storage_dict = json.load(f)
                self.totalCount = storage_dict["totalCount"]
                self.totalSize = storage_dict["totalSize"]
                self.hashedTotalSize = storage_dict.get("hashedTotalSize", 0.0)
                self.nonHashedTotalSize = storage_dict.get("nonHashedTotalSize", 0.0)
                self.modelTypes = {key: ModelType.from_dict(value) for key, value in storage_dict["modelTypes"].items()}
            d_debug(f"Loaded cache file from {CACHE_FILE}", )
        except Exception as e:
            d_debug(f"Error loading cache file: {e}")
            self.initialize_new_cache() 

    def create_cache_file(self):
        '''Create the cache file and the cache location if they don't exist.'''
        if not CACHE_LOCATION.exists():
            CACHE_LOCATION.mkdir(parents=True)
        if not CACHE_FILE.exists():
            CACHE_FILE.touch()

    def add_file_by_type(self, model_type: str, file_detail: FileDetail):
        '''Add a file detail of a specific type to the storage.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            model.files.append(file_detail)
            model.count += 1
            model.update_size(file_detail.fileSize)
            self.totalSize += file_detail.fileSize
            self.totalCount += 1
            self.update_hash_counts(model, file_detail)
            self.update_size_breakdown(file_detail)

    def add_files_by_type(self, model_type: str, file_details: List[FileDetail]):
        '''Add a list of file details of a specific type to the storage.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            model.files.extend(file_details)
            model.count += len(file_details)
            for file_detail in file_details:
                model.update_size(file_detail.fileSize)
                self.totalSize += file_detail.fileSize
                self.update_hash_counts(model, file_detail)
                self.update_size_breakdown(file_detail)
            self.totalCount += len(file_details)

    # TODO: This function is not used - could be useful later so remember to implement it
    def replace_files(self, model_type: str, file_details: List[FileDetail]):
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            model.files = file_details
            model.count = len(file_details)
            model.size = sum([file.fileSize for file in file_details])
            self.totalSize = sum([file.fileSize for file in file_details])
            self.totalCount = len(file_details)
            self.update_all_hash_counts(model)
            self.update_all_size_breakdown()

    def get_file_of_type(self, model_type: str, file_name: str) -> FileDetail:
        '''Get a file of a specific type by its name.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            for file in model.files:
                if file.fileName == file_name:
                    return file
        return None

    def get_files_of_type(self, model_type: str) -> List[FileDetail]:
        '''Get all the files of a specific type.'''
        if model_type in self.modelTypes:
            return self.modelTypes[model_type].files
        return []
    
    def get_all_files(self) -> List[FileDetail]:
        '''Get all the files in the storage.'''
        return [file for model in self.modelTypes.values() for file in model.files]
    
    def get_all_hashed_files(self) -> List[FileDetail]:
        '''Get all the files in the storage that have a hash.'''
        return [file for model in self.modelTypes.values() for file in model.files if file.sha256 or file.crc32 or file.blake3]
    
    def get_all_non_hashed_files(self) -> List[FileDetail]:
        '''Get all the files in the storage that don't have a hash.'''
        return [file for model in self.modelTypes.values() for file in model.files if not file.sha256 and not file.crc32 and not file.blake3]

    def get_non_hashed_files_by_type(self, model_type : str) -> List[FileDetail]:
        '''Get all the files of a specific type that don't have a hash.'''
        return [file for file in self.get_files_of_type(model_type) if not file.sha256 and not file.crc32 and not file.blake3]

    def get_non_hashed_files_by_type_and_algorithm(self, model_type : str, hash_algorithm: str) -> List[FileDetail]:
        '''Get all the files of a specific type that don't have a specific hash algorithm.'''
        return [file for file in self.get_files_of_type(model_type) if not getattr(file, hash_algorithm)]

    def get_hashed_files_by_type_and_algorithm(self, model_types : List[str], hash_algorithm: str) -> List[FileDetail]:
        '''Get all the files of a specific type that have a specific hash algorithm.'''
        return [file for model_type in model_types for file in self.get_files_of_type(model_type) if not getattr(file, hash_algorithm)]

    def get_non_empty_modeltypes(self) -> List[str]:
        '''Get all the model types that have files in them.'''
        return [model_type for model_type, model in self.modelTypes.items() if model.count > 0]

    def add_hash_to_file_by_model(self, model_type: str, file_path: str, hash_type: str, hash_value: str):
        '''Add a hash to a file in the storage by its model type and file path.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            for file in model.files:
                if file.filePath == file_path:
                    self.update_file_hash(file, hash_type, hash_value)
                    self.update_hash_counts(model, file)
                    self.update_size_breakdown(file, inserted_hash=True)
                    break 

    def add_hash_to_file(self, file_path: str, hash_type: str, hash_value: str):
        '''Add a hash to a file in the storage by its file path.'''
        for model in self.modelTypes.values():
            for file in model.files:
                if file.filePath == file_path:
                    self.update_file_hash(file, hash_type, hash_value)
                    self.update_hash_counts(model, file)
                    self.update_size_breakdown(file, inserted_hash=True)
                    break


    def get_type_count(self, model_type: str) -> float:
        '''Get the count of a specific model type.'''
        return self.modelTypes[model_type].count

    def update_file_hash(self, file: FileDetail, hash_type: str, hash_value: str):
        '''Update the hash of a file in the storage.'''
        match hash_type:
            case "sha256":
                file.sha256 = hash_value
            case "crc32":
                file.crc32 = hash_value
            case "blake3":
                file.blake3 = hash_value
            case _:
                raise ValueError(f"Unknown hash type: {hash_type}")
            

    def update_hash_counts(self, model: ModelType, file: FileDetail):
        '''Update the hash counts of a model type based on a file.'''
        if file.sha256 or file.crc32 or file.blake3:
            model.hashedCount += 1
        if file.sha256:
            model.sha256Count += 1
        if file.crc32:
            model.crc32Count += 1
        if file.blake3:
            model.blake3Count += 1

    def update_all_hash_counts(self, model: ModelType):
        '''Update the hash counts of a model type based on all the files in it.'''
        model.hashedCount = sum(1 for file in model.files if file.sha256 or file.crc32 or file.blake3)
        model.sha256Count = sum(1 for file in model.files if file.sha256)
        model.crc32Count = sum(1 for file in model.files if file.crc32)
        model.blake3Count = sum(1 for file in model.files if file.blake3)

    def update_size_breakdown(self, file: FileDetail, inserted_hash=False):
        '''Update the storage size breakdown based on a file.'''
        if inserted_hash:
            self.hashedTotalSize += file.fileSize
            self.nonHashedTotalSize -= file.fileSize
        else:
            if file.sha256 or file.crc32 or file.blake3:
                self.hashedTotalSize += file.fileSize
            else:
                self.nonHashedTotalSize += file.fileSize

    def update_all_size_breakdown(self):
        '''Update the storage size breakdown based on all the files in it.'''
        self.hashedTotalSize = sum(file.fileSize for model in self.modelTypes.values() for file in model.files if file.sha256 or file.crc32 or file.blake3)
        self.nonHashedTotalSize = sum(file.fileSize for model in self.modelTypes.values() for file in model.files if not file.sha256 and not file.crc32 and not file.blake3)

    # Since filename isn't unique, we should use some other unique identifier
    # Potentially use hash if it exists
    def update_file_detail(self, model_type: str, file_detail: FileDetail):
        '''Update a file detail in the storage. Uses the file name to find the file.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            for idx, file in enumerate(model.files):
                if file.fileName == file_detail.fileName:
                    model.files[idx] = file_detail
                    self.update_hash_counts(model, file_detail)
                    self.update_size_breakdown(file_detail)
                    break

    def filter_existing_files(self, model_type: str, file_paths: List[str]) -> List[str]:
        '''Filter out the file paths that are already in the storage.'''
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            existing_file_paths = {file.filePath for file in model.files}
            return [path for path in file_paths if path not in existing_file_paths]
        else:
            d_debug(f"Model type {model_type} not found in storage")   
            return file_paths

    # Use both filename, path, and size to determine if the file is the same
    def contains_file(self, model_type: str, filename : str) -> bool:
        if model_type in self.modelTypes:
            model = self.modelTypes[model_type]
            for file in model.files:
                if file.fileName == filename:
                    return True
        return False
    
    def contains_model_type(self, model_type: str) -> bool:
        '''Check if the storage contains a specific model type.'''
        return model_type in self.modelTypes

    def save_storage_to_file(self, file_path: str):
        '''Save the storage to a file in a specific location.'''
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def update_cache_file(self):
        '''Update the cache file with the current storage.'''
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    # TODO: This isn't implemented correctly yet as it isn't used - could be useful later so remember to implement it
    def load_storage_from_file(self, file_path: Path) -> dict:
        '''Load the storage from a file.'''
        if not file_path.exists():
            return {}

        with open(file_path, "r", encoding="utf-8") as f:
            storage_dict = json.load(f)
            self.totalCount = storage_dict["totalCount"]
            self.totalSize = storage_dict["totalSize"]
            self.hashedTotalSize = storage_dict.get("hashedTotalSize", 0.0)
            self.nonHashedTotalSize = storage_dict.get("nonHashedTotalSize", 0.0)
            self.modelTypes = {key: ModelType.from_dict(value) for key, value in storage_dict["modelTypes"].items()}
        
        return storage_dict

    # TODO: If this is ever used, it should use d_debug instead of print
    def print_storage(self, print_files=False):
        '''Print the storage to the console.'''
        print(f"Total Count: {self.totalCount} - Total Size: {convert_size(self.totalSize)} \n")
        print(f"Hashed Total Size: {convert_size(self.hashedTotalSize)}")
        print(f"Non-Hashed Total Size: {convert_size(self.nonHashedTotalSize)} \n")
        for model_type, model in self.modelTypes.items():
            print(f"{model_type}")
            print(f" - File Count: {model.count}")
            print(f" - Collective Size: {convert_size(model.size)}")
            print(f" - Hashed Files: {model.hashedCount}")
            print(f" - SHA256 Files: {model.sha256Count}")
            print(f" - CRC32 Files: {model.crc32Count}")
            print(f" - Blake3 Files: {model.blake3Count}")
            print(f" - Unhashed Files: {model.count - model.hashedCount}")
            print("\n")
            if print_files:
                for file in model.files:
                    print(file)
        print("\n")

    # TODO: If this is ever used, it should use d_debug instead of print
    def print_storage_types(self):
        '''Print the types of the fields in the storage.'''
        print(f"Total Count: {type(self.totalCount)} - Total Size: {type(self.totalSize)} \n")
        print(f"Hashed Total Size: {type(self.hashedTotalSize)}")
        print(f"Non-Hashed Total Size: {type(self.nonHashedTotalSize)} \n")
        model = self.modelTypes["TextualInversion"]
        if model:
            print(f"{model}")
            print(f" - File Count: {type(model.count)}")
            print(f" - Collective Size: {type(model.size)}")
            print(f" - Hashed Files: {type(model.hashedCount)}")
            print(f" - SHA256 Files: {type(model.sha256Count)}")
            print(f" - CRC32 Files: {type(model.crc32Count)}")
            print(f" - Blake3 Files: {type(model.blake3Count)}")
            print(f" - Unhashed Files: {type(model.count - model.hashedCount)}")
            file_detail = model.files[0]
            if file_detail:
                print(f"{file_detail}")
                print(f" - File Detail: {type(file_detail)}")
                print(f" - File Path: {type(file_detail.filePath)}")
                print(f" - File Name: {type(file_detail.fileName)}")
                print(f" - File Size: {type(file_detail.fileSize)}")
                print(f" - SHA256: {type(file_detail.sha256)}")
                print(f" - CRC32: {type(file_detail.crc32)}")
                print(f" - Blake3: {type(file_detail.blake3)}")
                print(f" - API: {type(file_detail.api)}")
            print("\n")


    def to_dict(self, ui_friendly=False):
        '''Return the storage as a json string.'''
        if ui_friendly:
            return {
                "totalCount": self.totalCount,
                "totalSize": convert_size(self.totalSize),
                "hashedTotalSize": convert_size(self.hashedTotalSize),
                "nonHashedTotalSize": convert_size(self.nonHashedTotalSize),
                "modelTypes": {key: value.to_dict(short=True) for key, value in self.modelTypes.items()}
            }
        
        return {
            "totalCount": self.totalCount,
            "totalSize": self.totalSize,
            "hashedTotalSize": self.hashedTotalSize,
            "nonHashedTotalSize": self.nonHashedTotalSize,
            "modelTypes": {key: value.to_dict() for key, value in self.modelTypes.items()}
        }
        
    
    def clear(self):
        '''Clear the storage.'''
        self.modelTypes = {
            "TextualInversion": ModelType(),
            "Hypernetwork": ModelType(),
            "Checkpoint": ModelType(),
            "LORA": ModelType()
        }
        self.totalCount = 0
        self.totalSize = 0.0
        self.hashedTotalSize = 0.0
        self.nonHashedTotalSize = 0.0

    def purge_cache(self):
        '''Purge the cache file.'''
        self.clear()
        self.update_cache_file()