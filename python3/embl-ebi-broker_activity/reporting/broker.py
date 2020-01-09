
class BaseQuery:
    status = {
        "draft": "1",
        "private": "2",
        "cancelled": "3",
        "public": "4",
        "suppressed": "5",
        "killed": "6"
    }

    def __init__(self, data_type, broker_name, status, verbose, analysis_type):
        self.data_type = data_type
        self.broker_name = broker_name
        self.status = status
        self.verbose = verbose
        self.analysis_type= analysis_type


    def query_builder(self):
        if self.data_type.lower() == 'submission':
            query = """
            select A.data_type, A.created_first, A.submission_account_id, A.count, B.broker_name from (
            select '{data_type}' as data_type, to_char(first_created, 'mm-yyyy') created_first,
            submission_account_id, count(*) as count
            from {data_type} where submission_id in 
            (select submission_id from submission where submission_account_id in 
            (select submission_account_id from submission_account 
            where lower(broker_name) like ('%{broker}%'))) 
            group by 
            to_char(first_created, 'mm-yyyy'), 
            submission_account_id
            ) A left join submission_account B on A.submission_account_id = B.submission_account_id
            """.format(data_type=self.data_type.upper(), broker=self.broker_name.lower())
        else:
            if not self.analysis_type:
                if self.verbose:
                    print("*"*100)
                    print("Analysis_type not provided")
                    print("*"*100)
                query = """
                select A.data_type, A.created_first, A.status_id, A.submission_account_id, A.count, B.broker_name , B.center_name from (
                select '{data_type}' as data_type, to_char(first_created, 'mm-yyyy') created_first, status_id,
                submission_account_id, count(*) as count
                from {data_type} where submission_id in 
                (select submission_id from submission where submission_account_id in 
                (select submission_account_id from submission_account 
                where broker_name is not null and lower(broker_name) like ('%{broker}%'))) and status_id in ('{status}')
                group by to_char(first_created, 'mm-yyyy'), 
                submission_account_id,status_id
                
                ) A left join submission_account B on A.submission_account_id = B.submission_account_id
                """
            else:
                if self.verbose:
                    print("*" * 100)
                    print("Analysis_type provided {}.......".format(self.analysis_type))
                    print("*" * 100)
                query="""
                select A.data_type, A.analysis_type, A.created_first, A.status_id, A.submission_account_id, A.count, B.broker_name, B.center_name from (
                select '{data_type}' as data_type, to_char(first_created, 'mm-yyyy') created_first, status_id,
                submission_account_id, count(*) as count, analysis_type
                from analysis where submission_id in 
                (select submission_id from submission where submission_account_id in 
                (select submission_account_id from submission_account 
                where broker_name is not null and lower(broker_name) like ('%{broker}%'))) and status_id in ('{status}')
                and analysis_type in ('{analysis_type}')
                group by to_char(first_created, 'mm-yyyy'),
                submission_account_id,status_id, analysis_type
                ) A left join submission_account B on A.submission_account_id = B.submission_account_id
                """
            if not self.status:
                if self.analysis_type and self.data_type.lower() == "analysis":
                    analysis_type = "','".join([x.upper() for x in self.analysis_type])
                    query = query.format(data_type=self.data_type.upper(), broker=self.broker_name.lower(),
                                         status="1','2','4", analysis_type=analysis_type)
                else:

                    query = query.format(data_type=self.data_type.upper(), broker=self.broker_name.lower(), status="1','2','4")
            else :
                status_id = "','".join(BaseQuery.status[x] for x in [x.lower() for x in self.status])

                if self.analysis_type and self.data_type.lower() == "analysis":
                    analysis_type = "','".join([x.upper() for x in self.analysis_type])
                    query = query.format(data_type=self.data_type.upper(), broker=self.broker_name.lower(),
                                         status=status_id, analysis_type=analysis_type)
                else:
                    query = query.format(data_type=self.data_type.upper(), broker=self.broker_name.lower(), status=status_id)
        return query