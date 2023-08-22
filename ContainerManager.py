import docker
import logging

def is_container_running(container_name_or_id:str) -> bool:
    client = docker.from_env()
    try:
        container = client.containers.get(container_name_or_id)
        return container.status == 'running'
    except:
        logging.error('Error in the container research')
        return False
