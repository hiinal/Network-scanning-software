import psycopg2
import json

conn = psycopg2.connect(
    dbname="employees",
    user="postgres",
    password="1111",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

with open('HP.json', 'r') as jsonfile:
    json_data = json.load(jsonfile)

insert_query = """
INSERT INTO system_info (
    system_info, boot_time, cpu_info, memory_info, 
    disk_info, network_info, gpu_info, bios_info, 
    software_list, product_key
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

data_to_insert = (
    json.dumps(json_data['System Information']),
    json_data['Boot Time'],
    json.dumps(json_data['CPU Information']),
    json.dumps(json_data['Memory Information']),
    json.dumps(json_data['Disk Information']),
    json.dumps(json_data['Network Information']),
    json.dumps(json_data['GPU Information']),
    json.dumps(json_data['BIOS Information']),
    json.dumps(json_data['Software List']),
    json_data['Product Key']
)

cur.execute(insert_query,data_to_insert)

conn.commit()

cur.close()
conn.close()

