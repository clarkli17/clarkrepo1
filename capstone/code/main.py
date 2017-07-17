import numpy as np
import pandas as pd
import io
import spacy
import pickle
from sqlalchemy import create_engine
from textblob import Word, TextBlob
from itertools import chain
from operator import itemgetter
import enchant
from textblob.wordnet import NOUN

eng = enchant.Dict("en_US")
nlp = spacy.load('en')
pd.set_option('display.max_colwidth', -1)

def extract_feat_opinion_by_sent_base(df_reviews):

    manual_stop = ['so','other','-PRON-']
    df_cand_feat = pd.DataFrame(columns = ['review_id','review_sent','feats','sentiment','orientation'])
    skip=0
    cand_feat={}
    syno_used={}
    for ind, review in df_reviews.iterrows():
        rev = review['review_text']
        rev_id = review['review_id']
        if rev:
            doc =nlp(rev)
            for sent in doc.sents:
                feat = ''
                if 1.0 * sum([1 for w in sent if eng.check(w) and w.pos_ != 'PUNCT'])/max(1,len([w for w in sent if w.pos_ != 'PUNCT']))>0.5:
                    for i,d in enumerate(sent):
                        if skip == 0:
                            if d.pos_ in ['NOUN','PROPN']:
                                if i < len(doc) -2:
                                    if d.ent_type_ == 'PERSON':
                                        feat = 'host'
                                    else:
                                        feat = ' '.join([n.lemma_ for n in sent[i:i+2] if n.pos_ in ['NOUN','PROPN']])
                                        skip = len(feat.split())
                                    adj = [c for n in sent[i:i+2] if n.pos_ in ['NOUN','PROPN'] for c in n.children if c.pos_ =='ADJ' and c.lemma_ not in manual_stop]

                                #when reached the end of review sentence:
                                else:
                                    if d.ent_type_ == 'PERSON':
                                        feat= 'host'
                                    else:
                                        feat = d.lemma_
                                    adj = [c for c in d.children if c.pos_ == 'ADJ' and c.lemma_ not in manual_stop]
                                adv = [l for k in adj for l in k.children if l.pos_ in ['ADV'] and l.lemma_ not in manual_stop]
                                amod = ' '.join(map(str,adv+adj))

                                #record and accumulate candidate features as they appear:
                                #feat_list.append(feat)

                                synonyms = set(chain.from_iterable([word.lemma_names() for word in Word(feat).get_synsets(pos=NOUN)]))
                                syno_feat = list(synonyms & set(cand_feat.keys()))

                                if syno_feat:
                                    if syno_feat[0]!= feat:
                                        syno_used[syno_feat[0]][1].append(feat)
                                        syno_used[syno_feat[0]][0]+=1
                                    feat = syno_feat[0]
                                    cand_feat[feat][0]+=1
                                    if amod !='':
                                        cand_feat[feat][1].append(amod)
                                        #amod_list.append(amod)
                                #if feat not in cand_feat.keys():
                                else:
                                    syno_used[feat]=[0,[]]
                                    if amod=='':
                                        cand_feat[feat]=[1,[]]
                                    else:
                                        cand_feat[feat]=[1,[amod]]
                                        #amod_list.append(amod)
                                df_cand_feat = df_cand_feat.append({'review_id':rev_id, 'review_sent':sent.string, 'feats':feat, 'sentiment':amod},ignore_index=True)

                            #Extract opinions through VERB dependency
                            elif d.pos_ == 'VERB' and feat <>'':
                                #print d.text, feat
                                #print [c for c in d.children if c.pos_ in ['NOUN','ADJ']]
                                adj = [c for c in d.children if c.pos_ in ['ADJ'] and c.lemma_ not in manual_stop]
                                adv = [l for k in adj for l in k.children if l.pos_ in ['ADV'] and l.lemma_ not in manual_stop]
                                amod = ' '.join(map(str,adv+adj))
                                #print amod
                                if amod != '':
                                    cand_feat[feat][1].append(amod)
                                    #amod_list.append(amod)
                                    #print rev_id, sent.string, feat

                                    df_cand_feat.loc[(df_cand_feat['review_id']==rev_id)& \
                                                 (df_cand_feat['review_sent']== sent.string) &\
                                                 (df_cand_feat['feats']== feat),'sentiment'] += ', ' +amod
                        skip = max(0,skip-1)


    return cand_feat, df_cand_feat, syno_used




def classify_orie(sentiment):
    pol = TextBlob(sentiment).sentiment.polarity
    if pol > 0: return 'Positive'
    elif pol <0: return 'Negative'
    else: return 'Neutral'

def pull_review_data(engine,city,min_reviews,neighbourhood='neighbourhood', l_id='id'):

    qry = '''
        select id, name, description, neighbourhood, neighbourhood_cleansed, review_scores_rating,
        review_scores_accuracy,review_scores_cleanliness,review_scores_checkin,
        review_scores_communication,review_scores_location,review_scores_value,number_of_reviews,review_id, review_text
        from listings l inner join reviews r on l.id = r.listing_id
        where l.source_city ='{}'
        and neighbourhood = {}
        and number_of_reviews >{}
        and id = {}'''.format(city, neighbourhood, min_reviews,l_id)
    return pd.read_sql_query(qry, engine)




def summarize(candfeat_df):
    candfeat_df.orientation = map(classify_orie, candfeat_df.sentiment)
    candfeat_df_filtered = candfeat_df[candfeat_df['orientation']!='Neutral']
    feat_matrix = candfeat_df_filtered.groupby(['feats','orientation']).count().unstack(fill_value=0)['review_id']
    feat_matrix['Total']=feat_matrix['Negative']+feat_matrix['Positive']
    feat_matrix.sort_values(by='Total',ascending=False, inplace=True)
    top10 = feat_matrix.head(10).index.values

    feat_sent = candfeat_df_filtered.groupby(['feats','orientation']).apply(lambda x: list(x['sentiment']))

    top10_feat_sent = feat_sent[list(top10)].unstack()
    return feat_matrix, top10_feat_sent


if __name__=='__main__':

    engine = create_engine('postgresql://clarkrds:capstone17@postgressql-capstone.cw4n5kyvg7ex.us-east-1.rds.amazonaws.com:5432/AirbnbDB')

    data = pull_review_data(engine=engine,city='SanFrancisco',min_reviews=0, neighbourhood="'Mission District'")#neighborhood='Mission District')
    test_reviews = data[['id','review_id','review_text']]
    candidate_feat, candfeat_df,syno_used = extract_feat_opinion_by_sent_base(test_reviews)
    feat_opinion, top10_feat_sent = summarize(candfeat_df)
    pickle.dump(feat_opinion, open( "feat_opinion_mission.p", "wb" ) )
    pickle.dump(top10_feat_sent, open( "top10_feat_sent_mission.p", "wb" ) )
    print feat_opinion[:10]
    print top10_feat_sent
