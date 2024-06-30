import os
from typing import List
from llama_index_client import Document
from llama_parse import LlamaParse
import logging
from pydantic import BaseModel, field_validator

from dotenv import load_dotenv
import yaml


load_dotenv()

logger = logging.getLogger(__name__)


class FileLoaderParserConfig(BaseModel):
    data_dir: str = "contracts"
    use_llama_parser: bool = False

    @field_validator("data_dir")
    def data_dir_must_exist(cls, dir_value):
        if not os.path.isdir(dir_value):
            raise ValueError(f"Directory '{dir_value}' does not exist")
        return dir_value


def load_config_file_parser():
    with open("config/file-parser.yaml") as f:
        config = yaml.safe_load(f)
    return config


def llama_parse_parser():
    if os.getenv("LLAMA_CLOUD_API_KEY") is None:
        raise ValueError(
            "LLAMA_CLOUD_API_KEY environment variable is not set. "
            "Please set it in .env file or in your shell environment then run again!"
        )
    parser = LlamaParse(result_type="text", language="pt")
    print("Llama parser initialized")
    return parser


def get_file_documents(
    contract_name: str, config: FileLoaderParserConfig
) -> List[Document] | list:
    from llama_index.core.readers import SimpleDirectoryReader

    try:
        reader = SimpleDirectoryReader(
            input_files=[f"{config.data_dir}/{contract_name}"]
        )
        logger.info(f"Loading file documents from {config.data_dir}/{contract_name}")

        if config.use_llama_parser:
            logger.info("Using LLAMA parser to parse the documents")
            parser = llama_parse_parser()
            reader.file_extractor = {".pdf": parser}
        print("Loading data")
        return reader.load_data()
    except ValueError as e:
        import sys, traceback

        # Catch the error if the data dir is empty
        # and return as empty document list
        _, _, exc_traceback = sys.exc_info()
        function_name = traceback.extract_tb(exc_traceback)[-1].name
        if function_name == "_add_files":
            logger.warning(
                f"Failed to load file documents, error message: {e} . Return as empty document list."
            )
            return []
        else:
            # Raise the error if it is not the case of empty data dir
            raise e
