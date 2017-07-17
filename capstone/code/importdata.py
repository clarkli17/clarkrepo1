from sqlalchemy import create_engine
import io
import pandas as pd
import glob
import time

def import_csv_to_postgresql (engine,table):
    conn= engine.raw_connection()
    cur = conn.cursor()
    #grab data files for loading
    file_list = glob.glob("../capstone data/{}_*.csv.gz".format(table))
    #print file_list
    #iterate through files to load one by one
    for f in file_list:
        city = f[f.index('_')+1:f.index('.csv')]
        if city not in ['']:# ['Toronto','Vancouver','WashingtonDC','Boston','Chicago','LA','NewOrleans','Portland','QuebecCity','SanFrancisco','NYC','Oakland','Seattle']:
        #if city in ['Toronto']:
            start=time.time()
            print 'loading {} data for {} now..'.format(table, city)
            df = pd.read_csv(f)
            rows = df.shape[0]
            #label the city identified by the source file
            df['source_city'] = city
            if city in ['Oakland', 'Seattle'] and table == 'listings':
                df.insert(12,'access','NA',True)
                df.insert(13,'interaction','NA',True)
                df.insert(14,'house_rules','NA',True)
            #The following three cities have trouble loading the data in csv, so I used the to_sql method which is slower but works
            if city in ['NYC','SanFrancisco','SanDiego'] and table == 'listings':
                df.to_sql(table, engine, if_exists='append',index=False)
            #For the rest of the cities, loading the data as csv is a lot faster:
            else:
                #create a csv object for loading into PostgresSQL table later (faster than to_sql method):
                s_buf = io.BytesIO()
                df.to_csv(s_buf, index=False, header=True, sep=',')
                s_buf.seek(0)
                #run copy method to load into PostgresSQL table:
                cur.copy_expert("""COPY {} FROM STDIN WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',')""".format(table), s_buf)
                conn.commit()
            end = time.time()
            print 'loading completed: {} rows in {}s'.format(rows, end - start)

if __name__ == "__main__":
    host = 'postgressql-capstone.cw4n5kyvg7ex.us-east-1.rds.amazonaws.com:5432'
    dbname = 'AirbnbDB'
    user = 'clarkrds'
    password = 'capstone17'
    #set up PostgresSQL connection with AWS RDS
    engine = create_engine('postgresql://{}:{}@{}/{}'.format(user,password,host,dbname))

    #conn = psycopg2.connect("host={} port='5432' dbname={} user={} password={}".format(host,dbname,user,password))
    #import_csv_to_postgresql(conn,'reviews')
    #import_csv_to_postgresql(engine,'listings')
    import_csv_to_postgresql(engine,'calendar')
