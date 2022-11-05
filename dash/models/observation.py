
from dotwiz import DotWiz
from util import get_guppy_service

import logging
logger = logging.getLogger('dash')


def get_observation_histograms(dot_notation=True):
    """Fetch histogram of counts for all observations.
    @type dot_notation: bool render results as a lightweight class"""

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
    data = guppy_service.graphql_query(histogram_query, variables={"filter": {"AND": []}})['data']
    if dot_notation:
        return DotWiz(data)
    return data
