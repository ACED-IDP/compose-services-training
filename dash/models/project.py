import logging

from dotwiz import DotWiz
from util import get_submission_service

logger = logging.getLogger('dash')


def get_project_summaries(dot_notation=True):
    """Fetch summaries for all projects.
    @type dot_notation: bool render results as a lightweight class
    """
    project_summaries_query = """
        query gqlHelperHomepageQuery {
          projects: project(first: 10000) {
            name: project_id
            code
            id
          }
          research_subject_count: _research_subject_count
          specimen_count: _specimen_count
          observation_count: _observation_count
          document_reference_count: _document_reference_count
        }    
    """
    query_service = get_submission_service()
    data = query_service.query(project_summaries_query)['data']
    # logger.debug(data)
    if dot_notation:
        return DotWiz(data)
    return data


def project_detail_counts(dot_notation=True):
    """Return detailed information about projects.
    @type dot_notation: bool render results as a lightweight class
    """
    project_detail_counts_query = """
        query gqlHelperProjectDetailQuery(
          $name: [String]
        ) {
          project(project_id: $name) {
            name: project_id
            code
            id
          }
          research_subject_count: _research_subject_count(project_id: $name)
          specimen_count: _specimen_count(project_id: $name)
          observation_count: _observation_count(project_id: $name)
          document_reference_count: _document_reference_count(project_id: $name)
        }    
    """
    query_service = get_submission_service()
    project_summaries = get_project_summaries()
    for project in project_summaries.projects:
        data = query_service.query(project_detail_counts_query, variables={'name': project.name})['data']
        # logger.debug(data)
        if dot_notation:
            yield DotWiz(data)
        else:
            yield data
