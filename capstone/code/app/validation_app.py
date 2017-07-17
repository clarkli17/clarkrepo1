from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import spacy
from textblob import Word
from itertools import chain
import enchant
eng = enchant.Dict("en_US")

app = Flask(__name__)
app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://clarkrds:capstone17@postgressql-capstone.cw4n5kyvg7ex.us-east-1.rds.amazonaws.com:5432/AirbnbDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)

def split_by_sentence(review_data):
    nlp = spacy.load('en')
    manual_stop = ['so','other','-PRON-']
    skip=0
    data_split=[]
    feat_list=[]
    syno_used={}
    cand_feat=[]
    for rev in review_data:
        if rev.review_text:
            doc =nlp(rev.review_text)
            for sent in doc.sents:
                if len(sent)>1 and 1.0 * sum([1 for w in sent if eng.check(w) and w.pos_ != 'PUNCT'])/len([w for w in sent if w.pos_ != 'PUNCT'])>0.5:
                    feat_list=[]
                    feat = ''
                    for i,d in enumerate(sent):
                        #print i, d.lemma_,d.pos_,d.dep_, [c for c in d.children]
                        if skip == 0:
                            if d.pos_ in ['NOUN','PROPN']:
                                if i < len(doc) -2:
                                    feat = ' '.join([n.lemma_ for n in sent[i:i+2] if n.pos_ in ['NOUN','PROPN']])
                                    #print 'feat', feat, len(feat.split())
                                    skip = len(feat.split())

                                #when reached the end of review sentence:
                                else:
                                    feat = d.lemma_
                                synonyms = set(chain.from_iterable([word.lemma_names() for word in Word(feat).synsets]))
                                syno_feat = list(synonyms & set(cand_feat))

                                if syno_feat:
                                    if syno_feat[0]!= feat:
                                        syno_used[syno_feat[0]][1].append(feat)
                                        syno_used[syno_feat[0]][0]+=1
                                    feat = syno_feat[0]
                                else:
                                    syno_used[feat]=[0,[]]
                                    cand_feat.append(feat)
                                feat_list.append(feat)
                        skip = max(0,skip-1)
                    #print feat_list
                    data_split.append([rev.listing_id,rev.review_id,sent.string,feat_list])
    return data_split

class Reviews(db.Model):
    __tablename__ = 'reviews'

    listing_id = db.Column(db.Integer)
    review_id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text)
    source_city = db.Column(db.Text)

    def __repr__(self):
        return '<1_Data {},{}>'.format(self.review_id, self.review_text)

class Reviews_labeled(db.Model):
    __tablename__ = 'reviews_labeled'

    listing_id = db.Column(db.Integer)
    review_id = db.Column(db.Integer, primary_key=True)
    sentence_in_review = db.Column(db.Text)
    feature = db.Column(db.Text)
    orientation = db.Column(db.Text)


@app.route('/')
def index():
    return 'hello'

@app.route('/manual_label', methods = ['GET','POST'])
def manual_label():
    check = db.session.query(Reviews_labeled.review_id.distinct())
    data = db.session.query(Reviews).filter(Reviews.listing_id==311259).filter(~Reviews.review_id.in_(check)).limit(20)
    data_split = split_by_sentence(data)
    session['data_split'] = data_split
    n = len(data_split)
    return render_template('validate2.html',data=enumerate(data_split), num_aspects = range(3))#), teamform = teamform)


@app.route('/handle_result', methods=['POST'])
def handle_result():
    data_split = session['data_split']
    n=len(data_split)
    #print data_split
    result = request.form.to_dict()
    objects=[]
    feats, sentiments = {},{}
    for k,v in result.iteritems():
        if k!='edit':
            i,j,t = k.split('+')
            if int(i) not in feats.keys(): feats[int(i)]={}
            if int(i) not in sentiments.keys():sentiments[int(i)]={}
            if t == '"feat"':
                feats[int(i)][int(j)]=v
            elif t == '"sentiment"':
                sentiments[int(i)][int(j)]=v
    print feats
    for i in range(n):
        for j in range(3):

            if feats[i][j]!='':
                objects.append(Reviews_labeled(listing_id = data_split[i][0],
                                       review_id = data_split[i][1],
                                       sentence_in_review = data_split[i][2],
                                       feature = feats[i][j],
                                       orientation = sentiments[i][j]))

    db.session.bulk_save_objects(objects)
    db.session.commit()

    return redirect(url_for('manual_label'))


if __name__ == '__main__':
    app.run(debug=True)
