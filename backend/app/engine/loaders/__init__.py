import logging
import yaml
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents

logger = logging.getLogger(__name__)


def load_config_file_parser():
    with open("config/file-parser.yaml") as f:
        config = yaml.safe_load(f)
    return config

def get_file_document(document_id: str):
    config = load_config_file_parser()
    document = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))
    return document

