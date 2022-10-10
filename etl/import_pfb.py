import json
from datetime import datetime

import psycopg2
from psycopg2.sql import Identifier, SQL

from fastavro import reader
from pfb.base import handle_schema_field_unicode, is_enum, decode_enum
from pelican.dictionary import init_dictionary, DataDictionaryTraversal


def create_node_dict(node_id, node_name, values, edges):
    node_dict = {
        "id": node_id,
        "name": node_name,
        "object": values,
        "relations": edges[node_id] if node_id in edges else [],
    }

    return node_dict


def split_by_n(input_list, n=10000):
    return [input_list[x : x + n] for x in range(0, len(input_list), n)]


def get_ids_from_table(db, table, ids, id_column):
    data = None

    if not table or not ids or not id_column:
        # TODO we need to use gen3logging
        print(
            f"[WARNING] Got a false-y input to a query. table: {table}, ids: {ids}, id_column: {id_column}"
        )
        return data

    for ids_chunk in split_by_n(ids):
        try:
            current_chunk_data = (
                db.option(
                    "query",
                    "SELECT * FROM {} WHERE {} IN ('{}')".format(
                        table, id_column, "','".join(ids_chunk)
                    ),
                )
                .option("fetchsize", "10000")
                .load()
            )

            if data:
                data = data.union(current_chunk_data)
            else:
                data = current_chunk_data
        except TypeError:
            print(
                f"[ERROR] Query got invalid inputs: table: {table}, ids: {ids}, id_column: {id_column}."
                f"Split: {split_by_n(ids)}"
            )
            pass
        else:
            print(
                f"[WARNING] Got a false-y ids_chunk by splitting ids: {ids}. Split: {split_by_n(ids)}"
            )

    return data if data and data.first() else None


def convert_to_node(x, is_base64, project_id):
    obj = x["object"]
    to_update = {}
    for name, value in obj.items():
        if name in is_base64[x["name"]]:
            if value and is_base64[x["name"]][name]:
                to_update[name] = decode_enum(value)
    # TODO get parameter from CLI
    to_update['project_id'] = project_id
    obj.update(to_update)

    r = {
        "created": datetime.now(),
        "acl": json.dumps({}),
        "_sysan": json.dumps({}),
        "_props": json.dumps(obj),
        "node_id": x["id"],
    }

    return r


def convert_to_edge(x, edge_tables):
    return [
        (
            edge_tables[(x["name"], i["dst_name"])],
            {
                "created": datetime.now(),
                "acl": json.dumps({}),
                "_sysan": json.dumps({}),
                "_props": json.dumps({}),
                "src_id": x["id"],
                "dst_id": i["dst_id"],
            },
        )
        for i in x["relations"]
    ]


def write_table(cur, table, node, dry_run=True):
    """Write node to table."""
    # TODO - improve speed https://naysan.ca/2020/05/09/pandas-to-postgresql-using-psycopg2-bulk-insert-performance-benchmark/
    columns = ','.join(node.keys())
    place_holders = ','.join(['%s'] * len(node.keys()))
    values = [node[column] for column in node.keys()]
    if 'node_id' in node.keys():
        # vertex
        insert = f'insert into "{table}" ({columns}) values ({place_holders}) on conflict(node_id) do nothing;'
    else:
        # edge
        insert = f'insert into "{table}" ({columns}) values ({place_holders}) on conflict(src_id, dst_id) do nothing;'
    if not dry_run:
        cur.execute(SQL(insert), values)


def import_pfb_job(pfb_file, project_id, project_node_id, ddt, conn, dry_run, document_reference_object_ids):
    """Import the PFB into the database."""
    start_time = datetime.now()
    print(start_time)

    with open(pfb_file, "rb") as schema_field:
        avro_reader = reader(schema_field)
        writer_schema = avro_reader.writer_schema

        schema = []
        for schema_field in writer_schema["fields"]:
            if schema_field["name"] == "object":
                it = iter(schema_field["type"])
                # skip metadata
                next(it)
                for node in it:
                    schema.append(node)
                    for field in node["fields"]:
                        handle_schema_field_unicode(field, encode=False)

        _is_base64 = {}

        for node in schema:
            _is_base64[node["name"]] = fields = {}
            for field in node["fields"]:
                fields[field["name"]] = is_enum(field["type"])

        edge_table_by_labels = ddt.get_edge_table_by_labels()

        insert_count = 0
        total_count = 0
        batch_size = 10000
        cur = conn.cursor()
        for record in avro_reader:
            if record['name'] == 'Metadata':
                continue
            if record['name'] == 'ResearchStudy':
                # link the ResearchStudy to the gen3 project
                record['relations'] = [{"dst_id": project_node_id, "dst_name": "project"}]
            if record['name'] == 'DocumentReference':
                # link the ResearchStudy to the gen3 project
                if record['id'] in document_reference_object_ids:
                    record['object']['object_id'] = document_reference_object_ids[record['id']]
                    # print(f"Set document_reference_object_ids {record['object']['object_id']}")

            write_table(
                cur=cur,
                table=ddt.get_node_table_by_label()[record['name']],
                node=convert_to_node(record, _is_base64, project_id),
                dry_run=dry_run
            )
            edge_tuples = convert_to_edge(record, edge_table_by_labels)
            if edge_tuples:
                for edge_tuple in edge_tuples:
                    edge_table = edge_tuple[0]
                    edge = edge_tuple[1]
                    write_table(
                        cur=cur,
                        table=edge_table,
                        node=edge,
                        dry_run=dry_run
                    )
            insert_count += 1
            if insert_count == batch_size:
                conn.commit()
                total_count += insert_count
                insert_count = 0
                print("total_count {} {} {}".format(total_count, record['name'], datetime.now()))
        conn.commit()
        total_count += insert_count
        time_elapsed = datetime.now() - start_time
        print("Elapsed time: {} total_count {}".format(time_elapsed, total_count))
        cur.close()
        conn.close()
    return


if __name__ == "__main__":

    # TODO - get this from the command line
    dry_run = False
    # TODO - get this from the command line
    dictionary_url = 'https://aced-public.s3.us-west-2.amazonaws.com/aced.json'  # os.environ["DICTIONARY_URL"]

    # TODO - get this from the command line
    with open("Secrets/sheepdog_creds.json") as pelican_creds_file:
        sheepdog_creds = json.load(pelican_creds_file)

    # DB_URL = "jdbc:postgresql://{}/{}".format(
    #     sheepdog_creds["db_host"], sheepdog_creds["db_database"]
    # )
    DB_USER = sheepdog_creds["db_username"]
    DB_PASS = sheepdog_creds["db_password"]

    # TODO - get this from the command line
    DB_NAME = 'metadata_db'

    # TODO - get this from the command line
    program_name = 'MyFirstProgram'
    project_code = 'MyFirstProject'

    # NEW_DB_NAME = input_data_json["db"]

    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        # TODO - get this from the command line
        host='localhost',
        # port=DATABASE_CONFIG.get('port'),
    )

    cur = conn.cursor()
    cur.execute("select node_id, _props from \"node_program\";")
    programs = cur.fetchall()
    programs = [{'node_id': p[0], '_props': p[1]} for p in programs]
    program = next(iter([p for p in programs if p['_props']['name'] == program_name]), None)
    assert program, f"{program_name} not found in node_program"
    cur.execute("select node_id, _props from \"node_project\";")
    projects = cur.fetchall()
    projects = [{'node_id': p[0], '_props': p[1]} for p in projects]
    project_node_id = next(iter([p['node_id'] for p in projects if p['_props']['code'] == project_code]), None)
    assert project_node_id, f"{project_code} not found in node_project"
    project_id = f"{program_name}-{project_code}"

    # TODO - get this from the command line
    pfb_file = 'output/research_study_Alzheimers.pfb'
    print(f"Importing {pfb_file} into {project_id} project node {project_node_id}")

    dictionary, model = init_dictionary(url=dictionary_url)
    ddt = DataDictionaryTraversal(model)

    # TODO - get this from the command line
    # get the object ids created by file upload-pfb
    document_reference_object_ids = {}
    with open('file-object_ids.ndjson') as f:
        for line in f.readlines():
            document_reference_object_id = json.loads(line)
            document_reference_object_ids[document_reference_object_id['id']] = document_reference_object_id['object_id']

    import_pfb_job(
        pfb_file=pfb_file,
        project_id=project_id,
        project_node_id=project_node_id,
        ddt=ddt,
        conn=conn,
        dry_run=dry_run,
        document_reference_object_ids=document_reference_object_ids
    )
