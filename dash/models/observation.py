
from dotwiz import DotWiz
from util import get_guppy_service

import logging
logger = logging.getLogger('dash')


def get_patients(variables={"filter": {"AND": []}}):
    """Query histogram on patient_id to get all unique patients
    @type variables: object graphql filter object
    @return list of patient_id strings
    """
    query = """
        query ($filter: JSON) {
          _aggregation {
            case(filter: $filter) {
              patient_id {
                histogram {
                  key
                  count
                }
              }
            }
          }
        }  
    """
    guppy_service = get_guppy_service()
    data = guppy_service.graphql_query(query, variables=variables)['data']
    data = DotWiz(data)
    return [h.key for h in data._aggregation.case.patient_id.histogram]  # noqa


def get_observation_histograms(dot_notation=True, variables={"filter": {"AND": []}}):
    """Fetch histogram of counts for all observations.
    @param variables: a graphql filter
    @type dot_notation: bool render results as a lightweight class
    """

    histogram_query = """
    query ($filter: JSON) {
      _aggregation {
        case(filter: $filter, filterSelf: false, accessibility: all) {
          category {
            histogram {
              key
              count
            }
          }
          code_display {
            histogram {
              key
              count
            }
          }
          patient_id {
            histogram {
              key
              count
            }
          }
          encounter_type {
            histogram {
              key
              count
            }
          }
          encounter_start {
            histogram {
              key
              count
            }
          }
          project_id {
            histogram {
              key
              count
            }
          }
        }
      }
    }
    
    """
    guppy_service = get_guppy_service()
    data = guppy_service.graphql_query(histogram_query, variables=variables)['data']
    if dot_notation:
        return DotWiz(data)
    return data
