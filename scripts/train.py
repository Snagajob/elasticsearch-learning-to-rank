"""
Functions to create the judgement file and train a LTR model
"""
from __future__ import print_function
import os
from features import kwDocFeatures, buildFeaturesJudgmentsFile

def trainModel(judgmentsWithFeaturesFile, modelOutput):
    # java -jar RankLib-2.6.jar -ranker 6 -train sample_judgements_wfeatures.txt -save model.txt
    cmd = "java -jar RankLibPlus-0.1.0.jar  -ranker 6 -train %s -save %s" % (judgmentsWithFeaturesFile, modelOutput)
    print("Running %s" % cmd)
    os.system(cmd)
    pass


def saveModel(es, scriptName, modelFname):
    """ Save the ranklib model in Elasticsearch """
    with open(modelFname) as modelFile:
        modelContent = modelFile.read()
        es.put_script(lang='ranklib', id=scriptName, body={"script": modelContent})

if __name__ == "__main__":
    from elasticsearch import Elasticsearch
    from judgments import judgmentsFromFile, judgmentsByQid
    esUrl="http://localhost:9200"
    es = Elasticsearch(timeout=1000)
    judgements = judgmentsByQid(judgmentsFromFile(filename='sample_judgements.txt'))
    kwDocFeatures(es, index='tmdb', searchType='movie', judgements=judgements)
    buildFeaturesJudgmentsFile(judgements, filename='sample_judgements_wfeatures.txt')
    trainModel(judgmentsWithFeaturesFile='sample_judgements_wfeatures.txt', modelOutput='model.txt')
    # there's an initial error : Limit of script size in bytes [65535] has been exceeded for script [test] with size [2280732]
    # need to configure at config/elasticsearch.yml. add the following line:
    # script.max_size_in_bytes: [super large number]
    saveModel(es, scriptName='test', modelFname='model.txt')
