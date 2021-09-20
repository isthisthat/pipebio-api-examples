import os

from library.models.job_type import JobType
from library.pipebio_client import PipebioClient


def example_05_download_original_files():
    """
    Cluster Example
    Clusters a known annotated document from a known project.
    """

    project_name = os.environ['PROJECT_NAME']
    sequence_document_id = os.environ['TARGET_DOCUMENT_ID']

    if sequence_document_id is None or project_name is None:
        raise Exception("Error! Set sequence_document_id and project_name to continue.")
    else:
        sequence_document_id = int(sequence_document_id)

    client = PipebioClient()

    # Either login with hardcoded variables or use environment variables.
    # PIPE_EMAIL=<my-email> PIPE_PASSWORD=<my-password> PIPE_TOKEN=<my-token> python login.py
    client.login()

    # Display who we are logged in as.
    user = client.authentication.user
    print('\nLogged in as {}. \n'.format(user['firstName'], user['lastName']))

    # Get a list of all available projects for the user's organization.
    projects = client.shareables.list()

    # Find a specific project having a name "Example".
    example_project = next((project for project in projects if project['name'] == project_name), None)
    if example_project is None:
        print(f'Error: Example project named "{project_name}" not found')
        quit()

    # Find a specific document with an id "22333"
    entities = client.shareables.list_entities(example_project['id'])
    annotated_doc = next((entity for entity in entities if entity['id'] == str(sequence_document_id)), None)
    if annotated_doc is None:
        print('Error: annotated_doc not found')
        quit()

    # Run a cluster job on that document.
    organization_id = user['orgs'][0]['id']
    job_id = client.jobs.create(
        owner_id=organization_id,
        shareable_id=annotated_doc['ownerId'],
        input_entity_ids=[annotated_doc['id']],
        job_type=JobType.ClusterJob,
        name='Cluster job from python client',
        params={
            "filter": [],
            "regions": [
                "CDR-H3"
            ],
            "identity": "0.90",
            "wordSize": 5,
            "algorithm": "CDHit",
            "selection": [],
            "translate": True,
            "aggregates": [],
            "targetFolderId": annotated_doc['path'].split('.')[-2],
            "translationTable": "Standard"
        }
    )

    # Wait for the job to be completed.
    client.jobs.poll_job(job_id)

    print('\nDone.\n\n')


if __name__ == "__main__":
    example_05_download_original_files()
