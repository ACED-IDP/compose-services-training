
from dotwiz import DotWiz
from util import get_guppy_service

import logging
logger = logging.getLogger('dash')


def get_file_histograms(dot_notation=True, variables={"filter": {"AND": []}}):
    """Fetch histogram of counts for all projects.
    @param variables: a graphql filter
    @type dot_notation: bool render results as a lightweight class"""

    histogram_query = """
    query ($filter: JSON) {
      _aggregation {
        file (filter: $filter, filterSelf: false, accessibility: all) {
          
    project_id {
      histogram {
        key
        count
      }
    },
    file_category {
      histogram {
        key
        count
      }
    },
    data_type {
      histogram {
        key
        count
      }
    },
    data_format {
      histogram {
        key
        count
      }
    },
    patient_id {
      histogram {
        key
        count
      }
    },
    patient_gender {
      histogram {
        key
        count
      }
    },
    patient_disability_adjusted_life_years {
      histogram {
        key
        count
      }
    },
    patient_ombCategory {
      histogram {
        key
        count
      }
    },
    patient_ombCategory_detail {
      histogram {
        key
        count
      }
    },
    patient_us_core_birthsex {
      histogram {
        key
        count
      }
    },
    patient_quality_adjusted_life_years {
      histogram {
        key
        count
      }
    },
    patient_maritalStatus_coding_0_display {
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
