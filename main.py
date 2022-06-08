import nltk
nltk.download('wordnet',quiet=True)
nltk.download('averaged_perceptron_tagger',quiet=True)
nltk.download('stopwords',quiet=True)
nltk.download('punkt',quiet=True)
from agent import Agent
import pandas as pd
from pandasql import sqldf
from flask import Flask, request
from sequenceprocessor import Linkedlist


app = Flask(__name__)
df = pd.read_csv('data/sampletable2.csv')


class Nullqueryerror(Exception):
    pass


class DataframeEmptyerror(Exception):
    pass


def preprocess_df(df):
    '''
    preprocess the DataFrame
    '''
    df.columns = df.columns.str.replace(' ', '')
    for i in df.columns:
        if df[i].dtype == 'object':
            df[i] = df[i].str.strip()
    return df


def seqcorrection(sequence, columns):
    """
    Parameters
    ----------
    sequence : Given query
    columns  : Columns names

    Returns
    -------
    Seq : formatted sequence using levenstein's edit distance
    """
    sequence = " ".join(sequence.lower().split())
    sequence = sequence.split(' ')
    ll = Linkedlist()
    ll.insert_values(sequence)
    ll.initial_manipulation(columns)
    ll.data_manipulation(columns)
    seq = ll.print()
    return seq


@app.route('/nlq', methods=['GET'])
def run():
    # handle valid queries - {special characters - !@#$%^&*}
    # CHECK whether it is alpha or not
    # if it is alpha pass
    try:
        sequence = request.args.get('query')
        if len(sequence) != 0:
            if sequence[0] == '"' and sequence[-1] == '"': sequence = sequence[1:-1]
        if len(sequence) > 0:
            sequence = seqcorrection(sequence, df.columns.tolist())
            print(sequence)
            if df is not None:
                agent = Agent(preprocess_df(df))
                if 'distinct' in sequence or 'unique' in sequence:
                    query = agent.get_query(sequence,distinct=True)
                else:
                    query = agent.get_query(sequence)
                query = query.replace('dataframe', 'df')
                pysqldf = lambda q: sqldf(q, globals())
                print(query)
                result = pysqldf(query)
                print(result)
                return result.to_json(orient='records', indent=4)
            else:
                raise DataframeEmptyerror
        else:
            raise Nullqueryerror
    except Nullqueryerror:
        return {"error encountered": "Query cannot be Empty"}
    except DataframeEmptyerror:
        return {"error encountered": "Dataframe cannot be Empty"}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)