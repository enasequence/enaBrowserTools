#!/usr/bin/env python3

import argparse
import sys
from reporting import broker
import cx_Oracle
import db_config
import pandas as pd
from pandas.io.json import json_normalize
from alive_progress import alive_bar



def process_arguments(args):
    """
    process_arguments : this process the arguments passed
    on the command line
    :param args: list of arguments
    :return: return the configuration file
    """

    parser = argparse.ArgumentParser(description='Report on a Broker monthly '
                                                 'data type submission activity')

    parser.add_argument('-d', '--data_type', type=str,
                        help='Please provide the data type to report on '
                             '[analysis|sample|experiment|submission|runs|studies|]',
                        dest='data_type', required=True)
    parser.add_argument('-b', '--broker_name', type=str, dest='broker_name',
                        help='Provide the broker name example [ArrayExpress|EBI-EMG]'
                             'or provide three or more character for a greedy search',
                        required=True)
    parser.add_argument('-s', '--status', nargs='*', type=str, dest='status',
                        help='Space separated data type status a combination '
                        'of the following:[draft|private|cancelled|public|suppressed|killed],'
                        'default[draft,private,public]')
    parser.add_argument('-v', '--verbose', help='Increase processing verbosity',
                        action="store_true")
    parser.add_argument('-t', '--analysis_type', nargs="*", type=str,
                        dest='analysis_type',
                        help='Report on specific analysis type. '
                        'A space separate analysis type, a combination of the following:'
                        '[SEQUENCE_VARIATION|PROCESSED_READS|GENOME_MAP|SEQUENCE_ASSEMBLY|'
                        'TRANSCRIPTOME_ASSEMBLY|AMR_ANTIBIOGRAM|SAMPLE_PHENOTYPE|PATHOGEN_ANALYSIS|'
                        'TAXONOMIC_REFERENCE_SET|SEQUENCE_FLATFILE|REFERENCE_ALIGNMENT|'
                        'REFERENCE_SEQUENCE|SEQUENCE_ANNOTATION]', required=False)
    options = parser.parse_args(args)
    return options


def report_activity(db_config, sqlquery):
    dsn_tns = cx_Oracle.makedsn(db_config.host, db_config.port, service_name=db_config.database)
    with cx_Oracle.connect(user=db_config.user, password=db_config.password, dsn=dsn_tns) as conn:
        with conn.cursor() as cursor:
            with alive_bar(3) as bar:
                cursor.execute(sqlquery)
                cols = list(map(lambda x: x[0], cursor.description))
                result = []
                for i in cursor.fetchall():
                    result.append(dict(zip(tuple(cols), i)))
                    bar()
    return result


if __name__ == '__main__':
    options = process_arguments(sys.argv[1:])
    sql_query = broker.BaseQuery(data_type=options.data_type, broker_name=options.broker_name,
                                 status=options.status, verbose=options.verbose,
                                 analysis_type=options.analysis_type)
    sqlquery = sql_query.query_builder()
    if options.verbose:
        print("*"*100)
        print("Extracting activity with the following query\n{}\n{}".format("*"*100, sqlquery))
        print("*"*100)

    result = report_activity(db_config, sqlquery)
    result = json_normalize(result)
    status = dict([(value, key) for key, value in broker.BaseQuery.status.items()])
    if not result.empty:
        result['CREATEDED_FIRST'] = pd.to_datetime(result['CREATED_FIRST'], format="%m-%Y")
        result.sort_values(by=['CREATEDED_FIRST'], inplace=True, ascending=True)
        result = result.drop(['CREATEDED_FIRST'], axis=1)
        result['STATUS_ID'] = [status['{}'.format(x)] for x in result['STATUS_ID']]
        print(result.to_string(index=False))

    else:
        print(options.status)
        print("*"*100)
        if options.status:
            print("""No recorded activities for broker
                 {} on data type:{} with status :{}""".
              format(options.broker_name, options.data_type, ",".join([x for x in options.status])))
        else:
            print("""No recorded activities for broker
                             {} on data type:{} with status :{}""".
                  format(options.broker_name, options.data_type, ",".join(['draft','private','public'])))
        print("*"*100)
