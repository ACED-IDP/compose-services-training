-- delete all imported data

\c metadata_db ;
TRUNCATE        "node_condition"       CASCADE ;
TRUNCATE        "node_datarelease"     CASCADE ;
TRUNCATE        "node_diagnosticreport"        CASCADE ;
TRUNCATE        "node_documentreference"       CASCADE ;
TRUNCATE        "node_encounter"        CASCADE ;
TRUNCATE        "node_imagingstudy"     CASCADE ;
TRUNCATE        "node_location"         CASCADE ;
TRUNCATE        "node_medication"       CASCADE ;
TRUNCATE        "node_medicationrequest"       CASCADE ;
TRUNCATE        "node_observation"     CASCADE ;
TRUNCATE        "node_organization"     CASCADE ;
TRUNCATE        "node_patient"  CASCADE ;
TRUNCATE        "node_practitioner"     CASCADE ;
TRUNCATE        "node_practitionerrole"         CASCADE ;
TRUNCATE        "node_procedure"         CASCADE ;
TRUNCATE        "node_researchstudy"   CASCADE ;
TRUNCATE        "node_researchsubject"         CASCADE ;
TRUNCATE        "node_root"     CASCADE ;
TRUNCATE        "node_specimen"         CASCADE ;
TRUNCATE        "node_task"    CASCADE ;

\c  indexd_db; 
TRUNCATE 	"base_version"	CASCADE ;
TRUNCATE 	"index_record"	CASCADE ;
TRUNCATE 	"index_record_authz"	CASCADE ;
TRUNCATE 	"index_record_hash"	CASCADE ;
TRUNCATE 	"index_record_metadata"	CASCADE ;
TRUNCATE 	"index_record_url"	CASCADE ;

