-- delete all imported data

\c metadata_db ;

TRUNCATE	"node_Condition"	CASCADE ;
TRUNCATE	"node_DiagnosticReport"	CASCADE ;
TRUNCATE	"node_DocumentReference"	CASCADE ;
TRUNCATE	"node_Encounter"	CASCADE ;
TRUNCATE	"node_ImagingStudy"	CASCADE ;
TRUNCATE	"node_Location"	CASCADE ;
TRUNCATE	"node_Medication"	CASCADE ;
TRUNCATE	"node_MedicationRequest"	CASCADE ;
TRUNCATE	"node_Observation"	CASCADE ;
TRUNCATE	"node_Organization"	CASCADE ;
TRUNCATE	"node_Patient"	CASCADE ;
TRUNCATE	"node_Practitioner"	CASCADE ;
TRUNCATE	"node_Procedure"	CASCADE ;
TRUNCATE	"node_ResearchStudy"	CASCADE ;
TRUNCATE	"node_ResearchSubject"	CASCADE ;
TRUNCATE	"node_Specimen"	CASCADE ;
TRUNCATE	"node_Task"	CASCADE ;