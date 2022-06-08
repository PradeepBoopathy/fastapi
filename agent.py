from nlp import Nlp
import pandas as pd
from logging_utils import get_logger
import logging
import string

def Likestatements(seq):
    s = ["begins", "starts", "ends", "begin", "start", "end", 'contains','containing']
    start = ["begins", "starts", "begin", "start"]
    end = ["ends", "end"]
    contains = ['contains','containing']
    likestat = ''
    sequence = seq.lower()
    words = [i for i in sequence.split()]
    keyword = ''
    for i in words:
        if i in s:
            keyword = i
            break
    if keyword in start:
        word = words.index(i)
        startletter = words[word+2]
        if startletter[-1] == '?':
            startletter = startletter[:-1].upper()
        columnname = words[word-2]
        likestat = " WHERE {} LIKE '{}%'".format(columnname,startletter)
        seq = seq[:seq.find(columnname) + len(columnname)]
    if keyword in end:
        word = words.index(i)
        startletter = words[word+2]
        if startletter[-1] == '?':
            startletter = startletter[:-1].upper()
        columnname = words[word-2]
        likestat = " WHERE {} LIKE '%{}'".format(columnname,startletter)
        seq = seq[:seq.find(columnname) + len(columnname)]
    if keyword in contains:
        if keyword =='contains':
            word = words.index(i)
            pattern = words[word+1]
            if pattern[-1] == '?':
                pattern = pattern[:-1].upper()
            columnname = words[word-2]
            likestat = " WHERE {} LIKE '%{}%'".format(columnname, pattern)
            seq = seq[:seq.find(columnname) + len(columnname)]
        else:
            word = words.index(i)
            pattern = words[word+1]
            if pattern[-1] == '?':
                pattern = pattern[:-1].upper()
            columnname = words[word-1]
            likestat = " WHERE {} LIKE '%{}%'".format(columnname, pattern)
            seq = seq[:seq.find(columnname) + len(columnname)]
    if keyword == '':
        likestat = ''
    return likestat,seq

def group_by(seq):
    sequence = seq.translate(str.maketrans('', '', string.punctuation))
    words = [i for i in sequence.split()]
    grouped = 1 if 'each' in words else 0
    if grouped == 1:
        key_index = words.index('each')
        groupbycol = key_index+1
        groupstr = ' GROUP BY ' + words[groupbycol]
        words.pop(key_index + 1)
        words.pop(key_index)
        seq = ' '.join([str(elem) for elem in words])
    else:
        groupstr = ''
        seq = seq
    return groupstr, seq

def Topstatements(seq):
    sequence = seq.lower()
    sequence = sequence.split(' ')
    out = ''
    if 'top' in sequence or 'Top' in sequence:
        topkey = sequence.index('top')
        number = sequence[topkey+1]
        out = ' LIMIT ' + number
        sequence.pop(topkey+1)
        sequence.pop(topkey)
        sequence = ' '.join([str(elem) for elem in sequence])
    else:
        sequence = seq
    return out, sequence

def like_helper(framed_query,likestatement_query):
    if 'WHERE' in framed_query:
        likestatement = likestatement_query.replace('WHERE','AND')
    else:
        likestatement = likestatement_query
    return likestatement

class Agent:
    """
    Generates sql queries and fetches query results from database.
    Methods
    -------
    get_query(question, verbose=False, distinct=False)
        Function that returns a SQL query from the question.
    """

    def __init__(self, data_dir, schema_dir=None, db_type='sqlite', username='', password='', database='db', host='localhost', port=None, drop_db=True, aws_db=False, aws_s3=False, access_key_id="", secret_access_key=""):
        """
        Constructs all the necessary attributes for the agent object.
        """
        self.data_dir = data_dir
        self.schema_dir = schema_dir
        self.db_type = db_type
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.drop_db = drop_db
        self.aws_db = aws_db
        self.aws_s3 = aws_s3
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    def get_query(self, question, verbose=False, distinct=False):
        """
        This function returns the SQL query from the question.

        Arguments
        ----------
        question: `str`
                Contains input utterance.
        verbose: `boolean`
                Default value: False
        distinct: `boolean`
                To select distinct values from dataframe

        Returns
        ----------
        Returns a  `str` of generated sql query.
        """
        topstats,question = Topstatements(question)
        groupby_stat, question = group_by(question)
        likestatement, question = Likestatements(question)
        nlp = Nlp(self.data_dir, self.schema_dir, self.aws_s3, self.access_key_id, self.secret_access_key)
        root_logger = logging.getLogger()
        if isinstance(self.data_dir, pd.DataFrame):
            df = self.data_dir
        else:
            df = nlp.csv_select(question)
        if df is None:
            print("Sorry,didn't catch that")
        else:
            if verbose:
                root_logger.setLevel(logging.INFO)
                logger = get_logger(__name__)
                sql_query = nlp.get_sql_query(df, question, distinct=distinct)
                logger.info('SQL query = %s', sql_query)
                if len(groupby_stat) != 0:
                    sql_query_list = sql_query.split(' ')
                    groupby_list = groupby_stat.split(' ')
                    sql_query_list = sql_query_list[:2] + [','] + [groupby_list[3]] + sql_query_list[2:]
                    sql_query = ' '.join([str(elem) for elem in sql_query_list])
                    return sql_query + like_helper(sql_query,likestatement) + topstats + groupby_stat
                else:
                    return sql_query + like_helper(sql_query,likestatement) + topstats + groupby_stat
            else:
                root_logger.setLevel(logging.WARNING)
                sql_query = nlp.get_sql_query(df, question, distinct=distinct)
                if len(groupby_stat) != 0:
                    sql_query_list = sql_query.split(' ')
                    groupby_list = groupby_stat.split(' ')
                    sql_query_list = sql_query_list[:2] + [','] + [groupby_list[3]] + sql_query_list[2:]
                    sql_query = ' '.join([str(elem) for elem in sql_query_list])
                    return sql_query + like_helper(sql_query,likestatement) + topstats + groupby_stat
                else:
                    return sql_query + like_helper(sql_query,likestatement) + topstats + groupby_stat