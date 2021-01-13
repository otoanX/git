import argparse
import pickle
from sklearn.linear_model import LinearRegression
import time

class Trainer():
    def __init__(self, uid):
        self.uid = uid
        # df = pd.read_csv("%s.csv"%uid) など
        pass
    
    def fit(self):
        model = LinearRegression()
        
        # 学習部分は省略
        print("学習開始")
        time.sleep(5) # 5秒待機
        print("学習終了")
        
        with open("model/%s_model.pkl"%self.uid, 'wb') as f:
                pickle.dump(model, f)
        return
    
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--uid', dest='uid', type=str, required=True)
    args = parser.parse_args()

    print("uid", args.uid)

    tr = Trainer(args.uid)
    tr.fit()